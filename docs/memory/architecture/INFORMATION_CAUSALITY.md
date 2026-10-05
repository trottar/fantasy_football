# Information and Causality

Prospective action policy:

`a(t) = pi[S(t), I(t)]`

Only information available at the decision time may influence the prospective action.

Required distinctions:
- frozen pregame state vs later observation
- raw observation vs derived/calibrated state
- decision-time evidence vs hindsight
- screening frontier vs decision authority
- football response vs behavior response

Never backfill a prospective capture after relevant outcomes are known and label it prospective.

If a deadline is missed, record the missing measurement honestly and continue from the next causally valid capture.

## Historical Replay Information Boundary

Historical replay is always labeled retrospective.

`CAUSAL_FROZEN_REPLAY` means every material decision-driving input is a genuine
decision-time artifact or is otherwise proven available at that time. A frozen
snapshot alone is insufficient if configuration, values, availability, market,
lock, transaction, or other material dependencies were reconstructed later.

Any material substitution or reconstruction requires
`RECONSTRUCTED_RETROSPECTIVE_REPLAY`.

Replay evaluation uses a two-phase firewall: predictive candidate generation,
evaluation, uncertainty, ranking, and model-action selection are frozen before
observed outcomes are attached. The oracle-best feasible action is computed only
after that freeze and is hindsight description, never action authority.

Neither replay mode may be called a backfilled prospective capture.
