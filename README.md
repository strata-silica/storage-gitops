# storage-gitops

Reviewed GitOps authority for RE8CH storage infrastructure.

GitHub authority: `strata-silica/storage-gitops`.

This repository is in the **cutover-approved** phase and owns the bounded
data-storage release contracts. Ceph compiler and executor declarations are
also cutover-approved for the three locked Ceph releases. Cluster mutation
remains gated by protected Environments, exact GitHub OIDC claims and contract
allowlists.

## Intended scope

- Rook and Ceph control-plane declarations, CSI, pools, filesystems and object stores
- storage classes, snapshots, backup and recovery declarations
- bucket and object-storage provisioning controllers
- data-storage domain release contracts and reconciliation
- storage-specific Runtime Anatomy probes and profiles

Cross-domain catalog metadata and the generic Runtime Anatomy framework remain
in `re8ch/service-backend`.

See [docs/migration-inventory.md](docs/migration-inventory.md) for the staged
handoff and [governance/authority.yaml](governance/authority.yaml) for the
machine-readable ownership boundary.

GitHub-native governance is declared under `governance/github/`. Effective
repository settings must be applied with `gh api` after review and read back
from GitHub; committing the declarations alone does not enforce them.
