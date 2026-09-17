from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import math
import hmac
import json
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any, Mapping


DEFAULT_REPLACEMENT = "[REDACTED]"
DEPTH_REPLACEMENT = "[REDACTED:MAX_DEPTH]"
BINARY_REPLACEMENT = "[REDACTED:BINARY]"

_SENSITIVE_COMPONENTS = frozenset(
    {
        "password",
        "passwd",
        "secret",
        "token",
        "cookie",
        "authorization",
        "credential",
        "credentials",
        "session",
        "swid",
    }
)

_DEFAULT_EXACT_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "espn_s2",
        "set_cookie",
        "access_token",
        "refresh_token",
        "id_token",
        "client_id",
        "session_id",
        "account_id",
        "user_id",
        "profile_id",
        "league_id",
        "email",
        "phone",
        "phone_number",
    }
)

_HEADER_PATTERN = re.compile(
    r"(?i)\b(authorization|cookie|set-cookie)\s*:\s*[^\r\n]+"
)
_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(espn_s2|swid|api[_-]?key|access[_-]?token|"
    r"refresh[_-]?token|id[_-]?token|password|passwd|secret)"
    r"\s*[:=]\s*[^;\s,]+"
)
_AUTH_PATTERN = re.compile(
    r"(?i)\b(Bearer|Basic)\s+[A-Za-z0-9._~+/=-]+"
)
_NAMESPACE_RE = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")


def _normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")


def is_sensitive_key(
    key: str,
    *,
    exact_keys: frozenset[str] = _DEFAULT_EXACT_KEYS,
) -> bool:
    if not isinstance(key, str):
        raise TypeError("key must be a string")
    normalized = _normalize_key(key)
    if normalized in exact_keys:
        return True
    parts = tuple(part for part in normalized.split("_") if part)
    return any(part in _SENSITIVE_COMPONENTS for part in parts)


def _freeze_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _freeze_json(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    return value


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True)
class RedactionPolicy:
    replacement: str = DEFAULT_REPLACEMENT
    sensitive_keys: frozenset[str] = _DEFAULT_EXACT_KEYS
    sensitive_exact_values: tuple[str, ...] = ()
    redact_inline_secrets: bool = True
    max_depth: int = 16

    def __post_init__(self) -> None:
        if not isinstance(self.replacement, str) or not self.replacement:
            raise ValueError("replacement must be a non-empty string")
        if not isinstance(self.sensitive_keys, frozenset):
            object.__setattr__(self, "sensitive_keys", frozenset(self.sensitive_keys))
        normalized_keys = set()
        for key in self.sensitive_keys:
            if not isinstance(key, str) or not key:
                raise ValueError("sensitive_keys must contain non-empty strings")
            normalized_keys.add(_normalize_key(key))
        object.__setattr__(self, "sensitive_keys", frozenset(normalized_keys))

        values: list[str] = []
        for value in self.sensitive_exact_values:
            if not isinstance(value, str) or not value:
                raise ValueError(
                    "sensitive_exact_values must contain non-empty strings"
                )
            if value not in values:
                values.append(value)
        values.sort(key=len, reverse=True)
        object.__setattr__(self, "sensitive_exact_values", tuple(values))

        if not isinstance(self.redact_inline_secrets, bool):
            raise TypeError("redact_inline_secrets must be a bool")
        if isinstance(self.max_depth, bool) or not isinstance(self.max_depth, int):
            raise TypeError("max_depth must be an integer")
        if self.max_depth < 1:
            raise ValueError("max_depth must be >= 1")

    def key_is_sensitive(self, key: str) -> bool:
        normalized = _normalize_key(key)
        if normalized in self.sensitive_keys:
            return True
        parts = tuple(part for part in normalized.split("_") if part)
        return any(part in _SENSITIVE_COMPONENTS for part in parts)


@dataclass(frozen=True)
class RedactionResult:
    data: Any
    redacted_fields: int
    redacted_matches: int
    depth_replacements: int
    binary_replacements: int

    def to_value(self) -> Any:
        return _thaw_json(self.data)

    def to_dict(self) -> dict[str, Any]:
        return {
            "data": self.to_value(),
            "redacted_fields": self.redacted_fields,
            "redacted_matches": self.redacted_matches,
            "depth_replacements": self.depth_replacements,
            "binary_replacements": self.binary_replacements,
        }


class _Counts:
    def __init__(self) -> None:
        self.fields = 0
        self.matches = 0
        self.depth = 0
        self.binary = 0


def _sanitize_string(
    value: str,
    policy: RedactionPolicy,
    counts: _Counts,
) -> str:
    result = value
    for secret in policy.sensitive_exact_values:
        occurrences = result.count(secret)
        if occurrences:
            result = result.replace(secret, policy.replacement)
            counts.matches += occurrences

    if policy.redact_inline_secrets:
        def header_repl(match: re.Match[str]) -> str:
            counts.matches += 1
            return f"{match.group(1)}: {policy.replacement}"

        def assignment_repl(match: re.Match[str]) -> str:
            counts.matches += 1
            return f"{match.group(1)}={policy.replacement}"

        def auth_repl(match: re.Match[str]) -> str:
            counts.matches += 1
            return f"{match.group(1)} {policy.replacement}"

        result = _HEADER_PATTERN.sub(header_repl, result)
        result = _ASSIGNMENT_PATTERN.sub(assignment_repl, result)
        result = _AUTH_PATTERN.sub(auth_repl, result)

    return result


def _redact(
    value: Any,
    policy: RedactionPolicy,
    counts: _Counts,
    depth: int,
) -> Any:
    if depth > policy.max_depth:
        counts.depth += 1
        return DEPTH_REPLACEMENT

    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float is not JSON-safe")
        return value
    if isinstance(value, str):
        return _sanitize_string(value, policy, counts)
    if isinstance(value, (bytes, bytearray, memoryview)):
        counts.binary += 1
        return BINARY_REPLACEMENT
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("datetime values must be timezone-aware")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, Path):
        return _sanitize_string(str(value), policy, counts)
    if isinstance(value, Enum):
        return _redact(value.value, policy, counts, depth)
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("mapping keys must be strings")
            if policy.key_is_sensitive(key):
                redacted[key] = policy.replacement
                counts.fields += 1
            else:
                redacted[key] = _redact(item, policy, counts, depth + 1)
        return redacted
    if isinstance(value, (list, tuple)):
        return [_redact(item, policy, counts, depth + 1) for item in value]
    if isinstance(value, (set, frozenset)):
        rows = [_redact(item, policy, counts, depth + 1) for item in value]
        return sorted(rows, key=repr)
    raise TypeError(
        f"unsupported redaction value type {type(value).__name__}"
    )


def redact(
    value: Any,
    *,
    policy: RedactionPolicy | None = None,
) -> RedactionResult:
    active = RedactionPolicy() if policy is None else policy
    if not isinstance(active, RedactionPolicy):
        raise TypeError("policy must be a RedactionPolicy or None")
    counts = _Counts()
    data = _redact(value, active, counts, 0)
    return RedactionResult(
        data=_freeze_json(data),
        redacted_fields=counts.fields,
        redacted_matches=counts.matches,
        depth_replacements=counts.depth,
        binary_replacements=counts.binary,
    )


def redact_value(
    value: Any,
    *,
    policy: RedactionPolicy | None = None,
) -> Any:
    return redact(value, policy=policy).to_value()


def redact_event(
    event: object,
    *,
    policy: RedactionPolicy | None = None,
) -> RedactionResult:
    if isinstance(event, Mapping):
        row = dict(event)
    elif hasattr(event, "to_dict"):
        row = event.to_dict()
        if not isinstance(row, Mapping):
            raise TypeError("event.to_dict() must return a mapping")
        row = dict(row)
    else:
        raise TypeError("event must be a mapping or provide to_dict()")
    return redact(row, policy=policy)


def redacted_event_json(
    event: object,
    *,
    policy: RedactionPolicy | None = None,
) -> str:
    return json.dumps(
        redact_event(event, policy=policy).to_value(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def pseudonymize_text(
    value: str,
    *,
    key: bytes,
    namespace: str = "id",
    length: int = 16,
) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("value must be a non-empty string")
    if not isinstance(key, bytes) or len(key) < 16:
        raise ValueError("key must be at least 16 bytes")
    if not isinstance(namespace, str) or not _NAMESPACE_RE.fullmatch(namespace):
        raise ValueError("namespace must be a safe lowercase identifier")
    if isinstance(length, bool) or not isinstance(length, int):
        raise TypeError("length must be an integer")
    if length < 8 or length > 64:
        raise ValueError("length must be between 8 and 64")
    digest = hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{namespace}:{digest[:length]}"
