import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


# ---------- Key preparation ----------

def _prepare_key(key: str, scheme: str) -> bytes:
    k = key.encode("utf-8")
    scheme = scheme.upper()

    if scheme == "AES":
        if len(k) not in (16, 24, 32):
            raise ValueError("AES key must be 16/24/32 bytes")
        return k


    raise ValueError("Unsupported scheme")


# ---------- Text AES/ROT13/RailFence (unchanged) ----------

def encrypt_text(plaintext: str, key: str, scheme: str) -> str:
    scheme = scheme.upper()
    k = _prepare_key(key, scheme)
    data = plaintext.encode("utf-8")

    if scheme == "AES":
        iv = get_random_bytes(16)
        cipher = AES.new(k, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(data, AES.block_size))
        return base64.b64encode(iv + ct).decode("utf-8")

    raise ValueError("Text encryption supports only AES now")


def decrypt_text(ciphertext_b64: str, key: str, scheme: str) -> str:
    scheme = scheme.upper()
    k = _prepare_key(key, scheme)
    raw = base64.b64decode(ciphertext_b64)

    if scheme == "AES":
        iv_len = 16
        iv, ct = raw[:iv_len], raw[iv_len:]
        cipher = AES.new(k, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode("utf-8")

    raise ValueError("Text decryption supports only AES now")


# ---------- Image AES (unchanged) ----------

def encrypt_image_aes(in_path: str, out_path: str, key: str) -> None:
    k = _prepare_key(key, "AES")
    iv = get_random_bytes(16)

    with open(in_path, "rb") as f:
        data = f.read()

    cipher = AES.new(k, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(data, AES.block_size))

    with open(out_path, "wb") as f:
        f.write(iv + ct)


def decrypt_image_aes(in_path: str, out_path: str, key: str) -> None:
    k = _prepare_key(key, "AES")

    with open(in_path, "rb") as f:
        raw = f.read()

    iv, ct = raw[:16], raw[16:]
    cipher = AES.new(k, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)

    with open(out_path, "wb") as f:
        f.write(pt)


# ---------- Image 2DES (EDE mode) ----------

def encrypt_image_2des(in_path: str, out_path: str, key: str) -> None:
    k = _prepare_key(key, "2DES")
    k1 = k[:8]
    k2 = k[8:]
    iv = get_random_bytes(8)

    with open(in_path, "rb") as f:
        data = f.read()

    cipher1 = DES.new(k1, DES.MODE_CBC, iv)
    c1 = cipher1.encrypt(pad(data, DES.block_size))

    cipher2 = DES.new(k2, DES.MODE_CBC, iv)
    c2 = cipher2.decrypt(c1)

    cipher3 = DES.new(k1, DES.MODE_CBC, iv)
    c3 = cipher3.encrypt(c2)

    with open(out_path, "wb") as f:
        f.write(iv + c3)


def decrypt_image_2des(in_path: str, out_path: str, key: str) -> None:
    k = _prepare_key(key, "2DES")
    k1 = k[:8]
    k2 = k[8:]

    with open(in_path, "rb") as f:
        raw = f.read()

    iv, ct = raw[:8], raw[8:]

    cipher1 = DES.new(k1, DES.MODE_CBC, iv)
    d1 = cipher1.decrypt(ct)

    cipher2 = DES.new(k2, DES.MODE_CBC, iv)
    e = cipher2.encrypt(d1)

    cipher3 = DES.new(k1, DES.MODE_CBC, iv)
    final = unpad(cipher3.decrypt(e), DES.block_size)

    with open(out_path, "wb") as f:
        f.write(final)


# ---------- Simple ciphers (unchanged) ----------

def rot13_cipher(text: str) -> str:
    result = []
    for ch in text:
        if "a" <= ch <= "z":
            result.append(chr((ord(ch) - ord("a") + 13) % 26 + ord("a")))
        elif "A" <= ch <= "Z":
            result.append(chr((ord(ch) - ord("A") + 13) % 26 + ord("A")))
        else:
            result.append(ch)
    return "".join(result)


def rail_fence_encrypt(text: str, rails: int) -> str:
    if rails < 2:
        return text
    fence = [[] for _ in range(rails)]
    row, step = 0, 1
    for ch in text:
        fence[row].append(ch)
        if row == 0:
            step = 1
        elif row == rails - 1:
            step = -1
        row += step
    return "".join("".join(r) for r in fence)


def rail_fence_decrypt(cipher: str, rails: int) -> str:
    if rails < 2:
        return cipher
    pattern = list(range(rails)) + list(range(rails - 2, 0, -1))
    idxs = [pattern[i % len(pattern)] for i in range(len(cipher))]
    counts = [idxs.count(r) for r in range(rails)]
    rails_chars = []
    pos = 0
    for c in counts:
        rails_chars.append(list(cipher[pos:pos + c]))
        pos += c
    result = []
    rail_pos = [0] * rails
    for r in idxs:
        result.append(rails_chars[r][rail_pos[r]])
        rail_pos[r] += 1
    return "".join(result)
