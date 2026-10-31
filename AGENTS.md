# Storage GitOps agent instructions

- GitHub `main` is the desired-state authority; use signed commits and pull requests.
- Do not add kubeconfig files, credentials, decrypted SOPS content or runner tokens.
- Do not add a Kubernetes-writing workflow until the corresponding authority entry is `cutover-approved`.
- During inventory and shadow phases, `re8ch/service-backend` remains the sole writer.
- Preserve exact release digests, namespaces, field managers and accepted state during migration.
- One resource may never have writers from both repositories.
- Runtime Anatomy belongs here only when the probe is storage-specific.
