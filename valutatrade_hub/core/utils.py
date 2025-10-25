from hashlib import sha256


def get_hashed_password(password: str, salt: str) -> str:
    salted_password = salt.encode() + password.encode()
    return sha256(salted_password).hexdigest()
