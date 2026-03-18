#!/usr/bin/python
# -*- coding: utf-8 -*-
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
import hvac
import os

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        openbao_url = os.getenv('OPENBAO_URL')
        role_id = os.getenv('OPENBAO_ROLE_ID')
        secret_id = os.getenv('OPENBAO_SECRET_ID')

        if not openbao_url or not role_id or not secret_id:
            raise AnsibleError(
                "Environment variables OPENBAO_URL, OPENBAO_ROLE_ID, and OPENBAO_SECRET_ID must be set."
            )

        # Authentification wiuth AppRole
        client = hvac.Client(url=openbao_url)
        client.auth.approle.login(role_id=role_id, secret_id=secret_id)

        if not client.is_authenticated():
            raise AnsibleError("OpenBao AppRole authentication failed")

        results = []
        for term in terms:
            if '=' not in term:
                raise AnsibleError(
                    f"Invalid format: '{term}'. Expected 'secret=path/to/secret'"
                )
            _, secret_path = term.split('=', 1)
            try:
                secret = client.secrets.kv.v2.read_secret_version(
                    path=secret_path
                )
                results.append(secret['data']['data'])
            except Exception as e:
                raise AnsibleError(
                    f"Error reading {secret_path}: {str(e)}"
                )
        return results
