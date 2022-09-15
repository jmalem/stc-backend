import hashlib


def hash_password(password: str, salt: str) -> str:
    combined = str(password) + str(salt)
    return hashlib.sha512(combined.encode("utf-8")).hexdigest()


def verify_password(password: str, salt: bytes, existing_hash: str) -> bool:
    new_hash = hash_password(password, salt)
    if existing_hash == new_hash:
        return True
    return False
