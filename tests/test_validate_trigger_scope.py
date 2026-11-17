from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"


def test_static_context_paths_are_the_only_main_push_exclusions():
    workflow = yaml.load(WORKFLOW.read_text(), Loader=yaml.BaseLoader)
    triggers = workflow["on"]
    ignored = set(triggers["push"]["paths-ignore"])

    assert "pull_request" in triggers
    assert {
        "site/**",
        "docs/CROSS-ORG-CONTEXT.md",
        "governance/cross-org-context.json",
        ".github/workflows/pages.yml",
    } <= ignored
    assert not {
        "contracts/**",
        "releases/**",
        "operations/**",
        "policies/**",
        ".github/workflows/validate.yml",
        ".github/workflows/storage-reconcile.yml",
    } & ignored
    assert "docs/**" not in ignored
    assert ".github/**" not in ignored
