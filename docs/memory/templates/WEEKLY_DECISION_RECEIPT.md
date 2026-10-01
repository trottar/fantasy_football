# Weekly Decision / Operational Health Receipt Template

Use this record for the authoritative weekly completion matrix defined by
`architecture/WEEKLY_DECISION_COMPLETION.md`. A missing required row is itself
`INCOMPLETE_COVERAGE`; an absent/stale required health item is `BLOCKED_HEALTH`.

## Provenance / Freshness

```yaml
season:
week:
fantasy_stage:
decision_time_utc:
source_checkpoint:
runtime_version:
config_identity:
data_snapshot_identity:
prospective_capture_id:
prospective_data_as_of_utc:
receipt_generated_utc:
```

- Material state change since capture: YES / NO
- Fresh capture required: YES / NO
- Required artifact missing/error flags:

## Decision Coverage Matrix

| Required channel / gate | Status | Receipt / evidence | Scope / gap / action |
| --- | --- | --- | --- |
| Lineup / availability | | | |
| Player waiver / free-agent (QB/RB/WR/TE) | | | |
| DST waiver / free-agent | | | |
| Kicker waiver / free-agent | | | |
| IR / reserve / open-slot / injury replacement | | | |
| One-for-one player trades | | | |
| Supported multi-player / unequal trades | | | |
| DST/K-inclusive trades when league-legal | | | |
| Prospective capture / provenance | | | |
| Weekly operational health | | | |

Allowed required-row states:

- `PASS / ACTION`
- `PASS / HOLD:<scope>`
- `NOT APPLICABLE:<reason>`
- `INCOMPLETE_COVERAGE:<gap>`
- `BLOCKED_HEALTH:<gate>`

A channel HOLD is never a roster-wide HOLD unless every other mandatory row is
also complete and healthy.

## Channel Integrity

- Player authority / paired-MC receipt:
- DST commissioned-policy receipt:
- K commissioned-policy receipt:
- `P ⊕ D ⊕ K` preserved internally: YES / NO
- Any league-legal cross-channel transaction composed only at complete-roster
  utility/state boundary: YES / NO / NOT APPLICABLE
- User examples narrowed search scope: MUST BE NO

## Weekly Operational Health

| Health item | Status | Evidence / freshness |
| --- | --- | --- |
| Repository/checkpoint identity | | |
| Commissioned runtime/source/config/data identities | | |
| Live provider/source health | | |
| Capture integrity / pre-data firewall | | |
| Persistence / observability non-interference state | | |
| Strict durable-memory health | | |
| Required decision-receipt inventory | | |
| Unresolved diagnostic blockers | | |

## Source / Change Health

Complete when source, decision orchestration, diagnostic tooling, runtime, or
health tooling changed. Otherwise state `NOT APPLICABLE:<reason>`.

- targeted tests:
- full pytest:
- compileall:
- generated-artifact / exact package validation:
- `git diff --check`:
- staged `git diff --cached --check`:
- changed/staged allowlist:
- schema-2 manifest validation:
- runtime synchronization / commissioning:
- remote verification:

## Overall Decision State

Choose exactly one only after all mandatory rows are accounted for:

- `COMPLETE / ACTION_REQUIRED`
- `COMPLETE / NO_ACTION`
- `INCOMPLETE_COVERAGE`
- `BLOCKED_HEALTH`
- `CAPTURE_REQUIRED`

Reason:

Authorized actions, if any:

Unsupported/missing action families:

Stale/missing health gates:
