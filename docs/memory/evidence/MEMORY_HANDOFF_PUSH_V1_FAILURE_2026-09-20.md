# Memory Reconciliation Push v1 Failure — 2026-09-20

## Classification

`FAILED BEFORE STAGING / FAILED BEFORE COMMIT / FAILED BEFORE PUSH`

No football/model/application/runtime file changed. The control-root Git index
was not staged. No commit was created and no push occurred.

## Observed sequence

1. The script verified the exact 22-file v6 local payload.
2. The script resolved remote `main` as
   `f22115e7c75357e4321912831a3f99d1ea3e5c3f`.
3. `git clone --branch main --single-branch ...` started successfully and created
   an isolated temporary staging checkout.
4. The next intended operation was `git -C <staging> rev-parse HEAD`.
5. The actual failing command shown in the terminal was only
   `git -C <staging>`, followed by Git's usage text and exit code 1.
6. The script terminated immediately. It never copied/staged the payload,
   generated the manifest, committed, pushed, or synchronized the manifest.

## Root cause

The exact delivered wrapper declared:

```powershell
function Invoke-Git {
    param([string]$Repo, [string[]]$Args)
    return Invoke-Native -FilePath 'git' -Arguments (@('-C', $Repo) + $Args)
}
```

PowerShell already defines `$args` as an automatic variable. Parameter and
variable names are case-insensitive, so the formal parameter name `$Args`
collided with that automatic variable. Named calls such as
`-Args @('rev-parse', 'HEAD')` did not survive into the wrapper's command-array
construction, yielding bare `git -C <repo>`.

The defect affected every `Invoke-Git` call in push v1, not only the first one.

## Corrective rule

- Never use `Args` as a PowerShell function/script formal parameter name.
- Use a specific name such as `GitArgs` or `CommandArgs`.
- Statically scan delivered PowerShell for formal `Args` parameters.
- Before any modifying Git operation, execute a concrete wrapper self-test whose
  expected output proves the subcommand and arguments were preserved.
- Continue to judge native-command success from `$LASTEXITCODE`, not stderr text.

## Modification state

- local v6 memory payload: unchanged by this failure;
- control-root project files: unchanged by push v1;
- staging/index: not attempted;
- commit: not attempted;
- push: not attempted;
- remote verification of a new commit: not applicable.
