# Local storage context

- `AGENTS.md` is authoritative.
- Storage reconciliation uses its dedicated GitHub Actions OIDC identity and
  bounded cloud SSA executor; local Flux is not a recovery path.
- Follow `docs/GITHUB_OPS_RECONCILE_DEBUGGING.md`, preserve exact digests and
  namespace boundaries, and never substitute another domain's executor group.
- Keep credentials and decrypted material out of Git and logs.
