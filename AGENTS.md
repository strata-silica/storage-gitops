# Storage GitOps agent instructions

## Start work

1. Read the planning Issue and its parent outcome.
2. Start from current `strata/main` in one task-specific `codex/*` worktree.
3. Read `governance/authority.yaml` and `docs/migration-inventory.md`.
4. Discover current RE8CH tools through `docs/RE8CH-TOOLS.md`.

## Delivery context

```text
Project → parent Issue → Issue → branch/worktree → signed commits → PR
        → checks → accepted artifact → runtime evidence → Project status
```

- Give each Project item type, lifecycle, status and dates.
- Keep one concern per branch and closing PR.
- Preserve exact digests, namespaces, field managers and accepted state.
- Keep comments for storage invariants, safety boundaries and external contracts.
- Put Kubernetes output, migration stories and experiments in Issues, Wiki or
  observability.

## Authority

GitHub `main` is desired-state authority. Cutover-approved contracts use the
bounded storage release path. Each resource has one active writer. Storage-only
Runtime Anatomy profiles belong here; the generic framework belongs to
`re8ch/service-backend`.

Credentials, kubeconfigs, decrypted SOPS material and runner tokens remain in
approved secret systems.
