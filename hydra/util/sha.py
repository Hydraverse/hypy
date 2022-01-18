from Crypto.Hash import keccak


def to_bytes(value):
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return bytes(value, 'utf-8')
    if isinstance(value, int):
        return bytes(str(value), 'utf-8')


def sha3(value: [str, bytes, int]):
    return keccak.new(digest_bits=256, data=to_bytes(value)).digest()
