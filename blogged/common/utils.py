import os


def get_secret(key):
    value = os.getenv(key)

    if os.path.isfile(value):
        with open(value) as f:
            return f.read()
    else:
        raise IOError(f"Secret file for {key} not found at {value}")

    return value
