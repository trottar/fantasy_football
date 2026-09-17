# State Model

Conceptual weekly state:

`S_w = (P_w, D_w, K_w, M_w, I_w)`

- `P_w`: player-channel roster/market state
- `D_w`: defense-channel state
- `K_w`: kicker-channel state
- `M_w`: market/manager state
- `I_w`: information available at week/decision time

State transition:

`S_{w+1} = T(S_w, a_w, omega_w, Delta I_w)`

where `a_w` is our action, `omega_w` represents stochastic football/league outcomes, and `Delta I_w` is newly available information.

Counterfactual utility:

`Delta U = U(S + delta S) - U(S)`

Use common random numbers for paired comparisons when practical.

Dropped/released players remain in league state. The league is not a one-team vacuum.
