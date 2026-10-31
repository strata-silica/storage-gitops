# Storage GitOps migration inventory

## Safety state

This repository has no Kubernetes credentials, protected deployment
Environments, reconciliation schedule, Flux source, or cluster-writing job.
Creation of this repository therefore does not change runtime authority.
Validation uses the enterprise `GitOps R640` runner group with the
`untrusted-build` label and performs offline checks only. The Sijie Macmini is
currently registered only to `re8ch/service-backend` and is not assumed to be
available across organizations.

## Initial ownership candidates

| Area | Current location | Destination | Initial action |
| --- | --- | --- | --- |
| Ceph compiler | `service-backend/.github/workflows/ceph-shadow-compile.yml` | this repository | copy for offline shadow comparison |
| Ceph releases | `service-backend/.github/workflows/ceph-static-release.yml` and `contracts/releases/ceph/` | this repository | inventory identities and accepted digests |
| Data-storage releases | six `main-data-storage-*` contracts | this repository | migrate five active storage releases; separately classify the retired Supabase identity release |
| Storage desired state | `service-backend/clusters/re8ch/domains/data-storage/` | this repository | copy only after secret and dependency audit |
| Storage operations | `service-backend/operations/storage/` | split by desired-state versus runbook ownership | preserve operational history |
| Bucket/object storage | distributed declarations and controllers | this repository | build exact object and workflow inventory |
| Runtime Anatomy | generic framework plus storage profiles | split | move only storage-specific profiles and probes |

## Explicit exclusions

- `main-data-storage-supabase-pg-re8ch` is already retired to
  `re8ch/identity-gitops`; it must not be reintroduced here.
- Product-owned database source code does not move here.
- Generic catalog, workspace locking and cross-domain Runtime Anatomy remain in
  `re8ch/service-backend`.
- No resource ownership changes during inventory or shadow phases.

## Staged cutover

1. Inventory exact files, objects, namespaces, GitHub Environments, OIDC
   audiences, field managers, bundles and accepted digests.
2. Copy only non-secret declarations and run offline rendering/validation.
3. Add GitHub-native protected Environments without credentials or deployment
   authorization; verify effective settings through the API.
4. Produce shadow bundles and compare immutable digests without cluster writes.
5. Approve one low-risk release handoff through paired pull requests.
6. Disable the old writer before enabling the new writer, then verify GitHub
   checks and runtime independently.
7. Move Ceph only after lower-risk data-storage handoffs are stable.
