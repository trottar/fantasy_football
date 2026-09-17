# Market Model

Football utility and manager behavior are separate layers.

```text
football physics
    -> true roster utility response
       -> our policy
       -> manager behavior model
          -> transaction resolver
             -> market state
```

Behavior kernels may include:
- roster need
- market perception
- ownership
- acquisition trends
- waiver priority
- package structure

They must not alter intrinsic football production.

## Waivers

The target architecture is ordered contingent claim lists per manager plus a league resolver implementing actual waiver priority/claim/drop mechanics.

## Trades

The target architecture separates:
- football response
- roster construction/legal completion
- market/perception response
- acceptance/counter/reject behavior

Search coverage must match evaluator capability; larger packages cannot exist only in the evaluator while automated search remains 1-for-1.
