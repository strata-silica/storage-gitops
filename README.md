# storage-gitops

Reviewed GitOps authority for RE8CH storage infrastructure.

GitHub authority: `strata-silica/storage-gitops`.

This repository is in the **inventory** phase. It does not currently own or
apply Kubernetes resources. `re8ch/service-backend` remains the execution
authority until a reviewed cutover records exact accepted digests, field
managers, GitHub Environments, OIDC subjects, and Flux source ownership.

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
