# Storage reconcile debugging

Use the service-backend [authoritative GitHub Actions to Kubernetes runbook](https://github.com/re8ch/service-backend/blob/main/docs/GITHUB_OPS_RECONCILE_DEBUGGING.md).

For `storage-reconcile.yml`, record the selected release, namespace, immutable
accepted digest, OIDC audience and first failed job. Verify the exact
`ssa-state-<release>` read and the dedicated
`re8ch:release-reconciler:data-storage` identity; never substitute a
service-backend or agent-runtime group. Validate the approved API endpoint and
CA before treating an `EOF` as RBAC evidence.

Do not restore local Flux, disable TLS validation, use local GitHub credentials,
rebuild an accepted artifact, or force shared SSA ownership. Dispatch through
the Re8ch Admin GitHub Governance service. Recovery requires a terminal-success
run and runtime read-back matching accepted state.
