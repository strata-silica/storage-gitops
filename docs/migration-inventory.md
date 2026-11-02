# Storage GitOps migration inventory

## Safety state

The data-storage executor uses the protected `release-executor-data-storage`
Environment and exact GitHub OIDC identity. Validation and compilation use the
enterprise R640 pool; bounded SSA execution uses the Sijie Macmini trusted-audit
runner. Secret values remain only in GitHub Environments.

## Initial ownership candidates

| Area | Current location | Destination | Initial action |
| --- | --- | --- | --- |
| Ceph compiler | `service-backend/.github/workflows/ceph-shadow-compile.yml` | this repository | migrated; publishes and signs from `strata-silica/storage-gitops` |
| Ceph releases | `service-backend/.github/workflows/ceph-static-release.yml` and `contracts/releases/ceph/` | this repository | cutover approved for `rook-ceph`, `ceph-csi-drivers`, and `rook-ceph-cluster` |
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
7. Publish all three Ceph bundles under the storage-gitops signer, then switch
   the compatibility dispatcher and exact OIDC subjects in one reviewed
   service-backend handoff. The old writer is removed before the new writer is
   dispatched.

## Ceph accepted baseline

The handoff preserves the live healthy digests until storage-gitops publishes
replacement bundles with identical locked inputs and its own keyless signer:

- `rook-ceph`: `sha256:3c7f536d6f9e5dc799a97998c7e4643b65853f796917748753338d4e990f1856`
- `ceph-csi-drivers`: `sha256:be4732be7a612517deb37adea3dd733701968b2494de2baeb2ffcb7b61bbd716`
- `rook-ceph-cluster`: `sha256:032726de18cd2b7f0511f9631fd1fcbbfa032627f1144405c319e6f203c78b3f`

The field managers, namespaces, resource allowlists, protected Environments,
and audience split remain unchanged. Only repository/workflow/signer authority
moves.
