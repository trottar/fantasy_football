# Memory Checkpoint Identity Semantics — 2026-09-21

## Classification

`M2 CHECKPOINT IDENTITY SEMANTICS = CONTENT COMPLETE / NO FOOTBALL OR RUNTIME CHANGE`

M2 resolves M0 finding A08: active memory must not require a future commit SHA in
order to be truthful.

The already-published M0+M1 reconciliation checkpoint is the predecessor for this
maintenance slice. M2 does not allocate a numbered architecture/football
decision; it therefore does not consume the next Phase 1B decision identifier.

## Problem

A commit cannot normally contain its own not-yet-created SHA. Requiring
`CURRENT.md` or the handoff to state "the latest durable checkpoint is <SHA>"
creates one of two bad outcomes:

1. the active file is one checkpoint behind immediately after publication; or
2. a documentation-only follow-up commit is required only to write the previous
   commit's SHA.

Both outcomes create avoidable state churn and make a fresh session reconcile
text that should have been self-consistent.

## Adopted Semantics

### 1. Committed repository state

When current memory is read from a Git commit/ref, the Git context containing the
files identifies that checkpoint.

If exact current identity is needed, query the containing Git/ref at read time.
Do not require active memory to name its own commit.

### 2. Local package/application state

Before commit, a local maintenance/source state is identified by:

- package ID;
- explicit affected-file predecessor identities;
- target identities or exact semantic result contract;
- successful local validation receipt.

This state is `LOCAL-APPLIED / VALIDATED` at most. File content alone does not
make it committed or pushed.

### 3. Isolated staging state

A publication candidate is identified by:

- expected remote predecessor;
- exact reviewed source allowlist;
- Git clean-filtered staged blob identities;
- regenerated schema-2 memory manifest;
- staged tree OID;
- passing staging gates.

The staged tree is not yet a commit.

### 4. Committed and remote state

After commit:

- commit SHA identifies the commit object;
- parent SHA proves lineage;
- tree OID proves committed content.

After push/verification:

- the remote branch/ref must resolve to that commit SHA.

`COMMITTED`, `PUSHED`, and `REMOTE VERIFIED` remain distinct evidence strengths.

### 5. Historical concrete SHAs

Evidence, decisions, dated history, commissioning records, and predecessor
contracts may record concrete SHAs because those identities are already known.

An SHA in active memory must have an explicit role such as:

- predecessor;
- commissioned source checkpoint;
- historical evidence checkpoint.

It must not be interpreted implicitly as "the commit containing this file."

## Active-Memory Rule

`CURRENT.md`, `CURRENT_HANDOFF.md`, and roadmap status may use self-relative
language:

- if this exact state is already on remote `main`, the durability gate is
  satisfied;
- if it exists only as local-applied content, publish the reviewed scope first.

That wording remains truthful before and after publication and avoids recursive
checkpoint bookkeeping.

Do not create a follow-up commit solely to insert the SHA of the just-created
memory checkpoint into active memory.

## Control Root Boundary

The control root remains a synchronization surface. Its local Git metadata may
lag files applied or synchronized through isolated checkpoint workflows.

Therefore:

- local apply uses package predecessor/result contracts;
- staging/commit uses the isolated staging clone's Git state;
- exact remote durability is resolved from the remote ref;
- active memory content is not proof of remote publication when read from the
  control root alone.

## Scope of M2

M2 changes only memory/checkpoint semantics and active continuity metadata.

It does not:

- alter football/model/application logic;
- alter the commissioned runtime;
- authorize persistent evidence;
- modify the retained Phase 1B technical candidate;
- reopen completed Phase 1A validation.

## Validation Contract

The M2 package must:

- verify exact M1 active-file predecessors;
- verify canonical Git-blob predecessors for edited policy files while tolerating
  declared UTF-8 BOM/newline representation differences;
- preserve original policy-file BOM/newline representation;
- apply one exact identity-semantics section to each canonical policy owner;
- create this evidence record exactly;
- keep `docs/memory/manifest.json` unchanged during local apply;
- keep the control-root Git index unchanged;
- pass strict memory health;
- support idempotent rerun;
- roll back all affected paths on post-write validation failure.

## Next Memory Step

Resolve M2 durability from the containing Git/ref state. Once M2 is present on
remote `main`, proceed to **M3 — procedure/ownership cleanup** only.

Week 3 prospective capture remains a harder calendar gate than nonessential M3-M7
progress.
