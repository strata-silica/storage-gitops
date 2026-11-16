# RE8CH Storage GitOps

<!-- gitops-status:start -->
[![Reconcile](https://github.com/strata-silica/storage-gitops/actions/workflows/storage-reconcile.yml/badge.svg?branch=main)](https://github.com/strata-silica/storage-gitops/actions/workflows/storage-reconcile.yml?query=branch%3Amain)
[![Contract validation](https://github.com/strata-silica/storage-gitops/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/strata-silica/storage-gitops/actions/workflows/validate.yml?query=branch%3Amain)
<!-- gitops-status:end -->

Reviewed desired-state authority for RE8CH storage infrastructure. The repository
owns cutover-approved data-storage contracts and three locked Ceph releases.
Kubernetes holds runtime state; protected GitHub Environments, exact OIDC claims
and contract allowlists bound mutation.

## Context chain

```text
Project → parent Issue → Issue → branch/worktree → signed commits → PR
        → checks → accepted artifact → runtime evidence → Project status
```

Use [the Project context template](.github/PROJECT_CONTEXT_TEMPLATE.md). Storage
observations, migration narratives and sanitized Kubernetes output belong in the
[Wiki](https://github.com/strata-silica/storage-gitops/wiki), planning Issues in
the owning control-plane repository, or observability systems.

## Authority

- Ownership boundary: [`governance/authority.yaml`](governance/authority.yaml)
- Migration inventory: [`docs/migration-inventory.md`](docs/migration-inventory.md)
- GitHub governance: `governance/github/`
- Reconciliation: `.github/workflows/storage-reconcile.yml`

Exact release digests, namespaces, field managers and accepted state define the
handoff. Each resource has one active writer. Storage-specific Runtime Anatomy
profiles live here; the generic framework remains in `re8ch/service-backend`.

## Working here

1. Start from current `strata/main` in an Issue-specific `codex/*` worktree.
2. Keep one concern in the worktree and closing PR.
3. Build each revision once and reuse its signed digest.
4. Record checks and sanitized runtime evidence in the Issue or Wiki.
5. Update Project status after verified evidence.

Comments explain storage invariants, ownership boundaries and external
contracts. Issues and Wiki carry examples, experiments and operational stories.
Tool discovery starts at [`docs/RE8CH-TOOLS.md`](docs/RE8CH-TOOLS.md).
