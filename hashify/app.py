from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os

from hash_utils import (
    generate_hash,
    identify_hash_type,
)

from crypto_utils import (
    encrypt_text,
    decrypt_text,
    encrypt_image_aes,
    decrypt_image_aes,
    rot13_cipher,
    rail_fence_encrypt,
    rail_fence_decrypt,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this"
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def index():
    return render_template("base.html")


# ---------- Hash generator ----------

@app.route("/api/hash/generate", methods=["POST"])
def api_hash_generate():
    algo = request.form.get("algorithm")
    text = request.form.get("text", "")




    data_bytes = b""

    try:
        digest = generate_hash(data_bytes, algo)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "algorithm": algo,
        "hash": digest,
        "warning": "Hashes like MD5, NTLM and CRC32 are not reversible."
    })


# ---------- Hash identifier ----------

@app.route("/api/hash/identify", methods=["POST"])
def api_hash_identify():
    value = request.form.get("hash", "").strip()
    if not value:
        return jsonify({"error": "Hash value required"}), 400
    result = identify_hash_type(value)
    return jsonify(result)


# ---------- Text encryption / decryption ----------

@app.route("/api/crypto/text/encrypt", methods=["POST"])
def api_text_encrypt():
    scheme = request.form.get("scheme")  # ROT13 or RAILFENCE
    text = request.form.get("text", "")
    rails = request.form.get("rails")

    if not text:
        return jsonify({"error": "Text required"}), 400

    try:
        if scheme == "ROT13":
            return jsonify({"ciphertext": rot13_cipher(text)})

        elif scheme == "RAILFENCE":
            if not rails:
                return jsonify({"error": "Rails required"}), 400
            rails = int(rails)
            return jsonify({"ciphertext": rail_fence_encrypt(text, rails)})

        else:
            return jsonify({"error": "Unsupported scheme"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/crypto/text/decrypt", methods=["POST"])
def api_text_decrypt():
    scheme = request.form.get("scheme")
    text = request.form.get("text", "")
    rails = request.form.get("rails")

    if not text:
        return jsonify({"error": "Ciphertext required"}), 400

    try:
        if scheme == "ROT13":
            return jsonify({"plaintext": rot13_cipher(text)})

        elif scheme == "RAILFENCE":
            if not rails:
                return jsonify({"error": "Rails required"}), 400
            rails = int(rails)
            return jsonify({"plaintext": rail_fence_decrypt(text, rails)})

        else:
            return jsonify({"error": "Unsupported scheme"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ---------- Image encryption / decryption ----------

@app.route("/api/crypto/image/encrypt", methods=["POST"])
def api_image_encrypt():
    scheme = request.form.get("scheme")  # AES or DES
    key = request.form.get("key", "")
    file = request.files.get("file")

    if scheme not in ("AES"):
        return jsonify({"error": "Image encryption only for AES"}), 400
    if not key:
        return jsonify({"error": "Key required"}), 400
    if not file:
        return jsonify({"error": "Image file required"}), 400

    filename = secure_filename(file.filename)
    in_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(in_path)

    out_path = os.path.join(
        app.config["UPLOAD_FOLDER"], f"encrypted_{scheme.lower()}_{filename}"
    )

    try:
        if scheme == "AES":
            encrypt_image_aes(in_path, out_path, key)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return send_file(
        out_path,
        as_attachment=True,
        download_name=os.path.basename(out_path),
    )


@app.route("/api/crypto/image/decrypt", methods=["POST"])
def api_image_decrypt():
    scheme = request.form.get("scheme")
    key = request.form.get("key", "")
    file = request.files.get("file")

    if scheme not in ("AES"):
        return jsonify({"error": "Image decryption only for AES"}), 400
    if not key:
        return jsonify({"error": "Key required"}), 400
    if not file:
        return jsonify({"error": "Encrypted file required"}), 400

    filename = secure_filename(file.filename)
    in_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(in_path)

    out_path = os.path.join(
        app.config["UPLOAD_FOLDER"], f"decrypted_{scheme.lower()}_{filename}"
    )

    try:
        if scheme == "AES":
            decrypt_image_aes(in_path, out_path, key)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return send_file(
        out_path,
        as_attachment=True,
        download_name=os.path.basename(out_path),
    )


if __name__ == "__main__":
    app.run(debug=True)
