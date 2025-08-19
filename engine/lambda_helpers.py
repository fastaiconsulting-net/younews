

import os
import json
import boto3

_secrets_cache = {}
def get_secret(name: str) -> str:
    if name in _secrets_cache:
        return _secrets_cache[name]
    sm = boto3.client("secretsmanager")
    resp = sm.get_secret_value(SecretId=name)
    val = resp.get("SecretString") or resp["SecretBinary"].decode()
    _secrets_cache[name] = val
    return val
