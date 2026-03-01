# Hashify 🔐

**Hashify** is a modern web application for secure hashing, hash identification, verification, and cryptographic encryption/decryption of text and files. Built as a cybersecurity learning tool, it helps explore how modern protections safeguard data in transit and at rest. 🛡️

## ✨ Features

- **🔐 Hash Generator** - Compute SHA-256, MD5, BLAKE2b, NTLM & more for text/files
- **🔍 Hash Identifier** - Auto-detect hash algorithms from input strings  
- **✅ Hash Verifier** - Compare computed vs provided hashes for integrity
- **🛡️ Encrypt/Decrypt** - AES, DES, ROT-13 ciphers with file support
- **🖱️ Drag & Drop** - Intuitive single-page dark cybersecurity theme
- **⚡ Loading Animations** - Smooth UX with hashes.gif centerpiece

## 🛠️ Tech Stack

| Component | Technologies |
|-----------|--------------|
| Backend | `Python 3.10+`, `Flask`, `hashlib`, `PyCryptodome` |
| Frontend | `HTML5`, `CSS3`, `Vanilla JS` (no frameworks) |
| Deployment | Local Flask dev server + `venv` |

## 📁 Project Structure

hashify/
├── app.py # 🚀 Main Flask app & routes
├── requirements.txt # 📦 Dependencies
├── README.md # 📖 This file!
├── hash_utils.py # 🔑 Hashing logic
├── crypto_utils.py # 🧬 Encryption functions
├── templates/
│ └── base.html # 📄 Single-page tabs layout
├── static/
│ ├── css/style.css # 🎨 Dark cybersecurity theme
│ ├── js/main.js # ⚡ Tab switching & drag-drop
│ └── img/hashes.gif # 🔄 Central animation

## Future Features: Hash comparison tool, downloadable reports, light/dark toggle, hash verifier
