import base64
from dotenv import set_key


def base64_encode(string: str):
    return base64.encode(string)


def base64_decode(string: str):
    return base64.decode(string)


def set_env(env_path: str, key: str, value: str):
    set_key(env_path, key_to_set=key, value_to_set=value)
