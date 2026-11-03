# Week 9 existing portable v2 — guarded supervised GUI entrypoint (source candidate)

`durable_memory_updated: true`

## Observed problem and exact authority

On November 3, the user verified that the updated ranked MC board renders on the running portable v2 and correctly labels the frozen October 28 Week 8 receipt `SAVED_WEEK_NOT_CURRENT_DO_NOT_ACT`. The existing "Refresh saved decisions" only calls `collect(runtime)` and redraws the saved data; no fresh ESPN, capture, native MC, or legality refresh occurs. The approved v2 operator's published source blob is `eb5990de21d2bd80d701fdbfb218dd71db17c2a7`. Its explicitly opt-in `--mode trial --ack-live-readonly` is the existing guarded integrated phase chain. Normal `run` requires a separate commissioning receipt and is **not** used here.

## Narrow patch

Add a **supervised** evaluation control to the existing weekly GUI panel. A visible checkbox requires explicit local human acknowledgment of six-provider reads, immutable prospective capture and native nine-channel MC, without automatic ESPN roster/market/trade writes. A new minimal GUI adapter refuses an unexpected portable tree, changed operator source, missing runtime, unsupported day, or an already-started protected slot. It does not use any arbitrary shell invocation. It observes fixed local phase receipt filenames (no raw private contents) and renders a bounded sanitized result from the native operator public result line. The save-only refresh displays `SAVED_EVIDENCE_RELOADED`/`SAVED_EVIDENCE_UNCHANGED` and a UTC refresh time.

All stochastic evaluation, provider access, lineage, timing and phase restart protection remain inside the existing published operator. No football kernels, behavior model, score mapping, league settings, snapshot schema, or ESPN write path are altered. Negative/missing states stay blocked; even a complete MC is `NATIVE_MC_COMPLETE_ACTION_CERTIFICATION_BLOCKED` pending §5A. There is no background scheduler, automatic MC on page load, or positive ESPN action certificate.

## Validation/rollout boundary

Provider-free tests cover Tuesday calendar and DST rollover, pinned identity, prior launch refusal, phase filename progression, bounded/redacted child output, strict authority result checks, single child-spawn and approved CLI flags. The local-apply package must pass exact predecessor-identity checks, local compile/tests, generated-source syntax and rollback gates. **Source-only:** it performs no ESPN GET, pregame capture, predictive MC, runtime sync, Git commit/push, or GUI restart. Full staged QA, remote publication, separate guarded installed-portable sync, independent-machine acceptance, and actual supervised prospective run remain separate observable gates; do not claim them before evidence.
