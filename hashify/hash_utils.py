import hashlib
import binascii
import zlib
from Crypto.Hash import MD4

SUPPORTED_HASHES = ["MD5", "SHA256", "SHA512", "NTLM", "CRC32"]


def generate_hash(data: bytes, algo: str) -> str:
    algo = algo.upper()
    if algo == "MD5":
        return hashlib.md5(data).hexdigest()
    if algo == "SHA256":
        return hashlib.sha256(data).hexdigest()
    if algo == "SHA512":
        return hashlib.sha512(data).hexdigest()
    if algo == "NTLM":
        md4 = MD4.new()
        md4.update(data.decode("utf-8").encode("utf-16le"))
        return md4.hexdigest()
    if algo == "CRC32":
        return format(zlib.crc32(data) & 0xFFFFFFFF, "08x")
    raise ValueError("Unsupported algorithm")


def identify_hash_type(hash_str: str) -> dict:
    h = hash_str.lower()
    length = len(h)

    candidates = []
    if length == 32:
        candidates.append("MD5")
    if length == 64:
        candidates.append("SHA256")
    if length == 128:
        candidates.append("SHA512")
    if length == 32:
        candidates.append("NTLM")
    if length == 8:
        candidates.append("CRC32")

    return {
        "input": hash_str,
        "candidates": list(set(candidates)),
        "note": "Length-based guess only. Not guaranteed.",
    }



