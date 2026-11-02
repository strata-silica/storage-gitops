#!/usr/bin/env python3
"""Renew the current executor credential without passing secrets in process argv."""
import os
import argparse
import base64
from pathlib import Path
import tempfile

import yaml

from ssa_executor import Executor, Rejected


def refresh() -> None:
    path = Path(os.environ['KUBECONFIG'])
    if path.is_symlink() or not path.is_file():
        raise Rejected('expected one regular executor kubeconfig')
    config = yaml.safe_load(path.read_text())
    matches = [entry for entry in config.get('users', []) if entry.get('name') == 'release-executor']
    if len(matches) != 1:
        raise Rejected('expected exactly one release-executor credential')
    required = ('ACTIONS_ID_TOKEN_REQUEST_URL', 'ACTIONS_ID_TOKEN_REQUEST_TOKEN', 'EXECUTOR_AUDIENCE')
    if any(not os.environ.get(name) for name in required):
        raise Rejected('incomplete Actions OIDC refresh configuration')
    token = Executor().actions_kube_token()
    if token is None:
        # The executor deliberately returns None while the credential acquired by
        # the workflow is still fresh. Keep that credential instead of turning a
        # safe reuse decision into a second, failure-prone OIDC exchange.
        existing = matches[0].get('user', {}).get('token')
        if not isinstance(existing, str) or not existing:
            raise Rejected('fresh Actions OIDC credential is absent from kubeconfig')
        return
    if not isinstance(token, str) or not token:
        raise Rejected('Actions OIDC returned an invalid executor credential')
    matches[0]['user'] = {'token': token}
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w') as handle:
            yaml.safe_dump(config, handle, sort_keys=False)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def initialize() -> None:
    """Initialize only the fixed API endpoint with a private guarded OIDC credential."""
    path = Path(os.environ['KUBECONFIG'])
    ca = os.environ['KUBE_API_CA']
    if not ca.strip():
        raise Rejected('missing Kubernetes CA')
    server = os.environ.get('KUBE_API_SERVER', 'https://kube-api.re8ch.com')
    if server not in {'https://kube-api.re8ch.com', 'https://10.181.22.147:6443'}:
        raise Rejected('unexpected Kubernetes API endpoint')
    cluster = {'server': server,
               'certificate-authority-data': base64.b64encode(ca.encode()).decode()}
    if server == 'https://10.181.22.147:6443':
        cluster['tls-server-name'] = 'kube-api.re8ch.com'
    config = {'apiVersion': 'v1', 'kind': 'Config',
              'clusters': [{'name': 're8ch-main', 'cluster': cluster}],
              'users': [{'name': 'release-executor', 'user': {}}],
              'contexts': [{'name': 'release-executor', 'context': {
                  'cluster': 're8ch-main', 'user': 'release-executor'}}],
              'current-context': 'release-executor'}
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as handle:
        yaml.safe_dump(config, handle, sort_keys=False)
    refresh()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--initialize', action='store_true')
    args = parser.parse_args()
    initialize() if args.initialize else refresh()
