# I-001 v0.36 Fixture Restoration

<!-- FANTASY_V036_FIXTURE_RESTORATION_EVIDENCE_20260917:BEGIN -->
## v0.36 fixture-restoration evidence

Classification: `V036_RELEASE_PACKAGING_FIXTURE_REGRESSION_CONFIRMED`

The two deterministic v0.36 failures disappear after restoring only the four missing baseline mock-draft fixtures, and the full v0.36 suite then passes.

Restored files:
- `data/mock_drafts/Pasted_markdown_20260830-223840_.csv` — SHA-256 `ca8556577c5bfdd42683da4b3a24d112522c650ac8f301fb406edaa20dc50603`
- `data/mock_drafts/Pasted_markdown_20260830-223840__summary.json` — SHA-256 `97a693e6fd1c890c9beab20e05b02ab6fc263d2d9816675936a772d6046f6054`
- `data/mock_drafts/mock_20260830_full.csv` — SHA-256 `008461de49f486dc837feb5c867ba222db2a3b02bfc619772c36384ea4b3f78b`
- `data/mock_drafts/mock_20260830_full_summary.json` — SHA-256 `c6e2f2334cb3f2f1723fc9459400bcea5a79df1ba1848e83f2746afe6fd99050`

Before targeted exits:
`[1, 1]`

After targeted exits:
`[0, 0]`

Full suite after restoration:
`0`

Detailed sanitized pytest outputs are retained in local evidence ZIP
`phase0_v036_fixture_probe_20260917_040448.zip` with SHA-256
`823fd30bf500dd4835bbc4cfa942774783a6958bf8f5c8a7c2da2b2d769e02f9`.
<!-- FANTASY_V036_FIXTURE_RESTORATION_EVIDENCE_20260917:END -->
