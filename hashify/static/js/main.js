// Tab switching
const buttons = document.querySelectorAll(".nav-tabs button");
const tabs = document.querySelectorAll(".tab");

buttons.forEach(btn => {
  btn.addEventListener("click", () => {
    const target = btn.getAttribute("data-tab");
    tabs.forEach(t => t.classList.remove("active"));
    document.getElementById("tab-" + target).classList.add("active");
  });
});

// Drag & drop helper
function setupDropZone(wrapperId, inputId) {
  const zone = document.getElementById(wrapperId);
  const input = document.getElementById(inputId);
  if (!zone || !input) return; // prevents JS crash


  zone.addEventListener("click", () => input.click());

  ["dragenter", "dragover"].forEach(evt =>
    zone.addEventListener(evt, e => {
      e.preventDefault();
      e.stopPropagation();
      zone.classList.add("dragover");
    })
  );

  ["dragleave", "drop"].forEach(evt =>
    zone.addEventListener(evt, e => {
      e.preventDefault();
      e.stopPropagation();
      zone.classList.remove("dragover");
    })
  );

  zone.addEventListener("drop", e => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      input.files = files;
    }
  });
}

setupDropZone("hash-gen-drop", "hash-gen-file");
setupDropZone("hash-ver-drop", "hash-ver-file");
setupDropZone("crypto-img-drop", "crypto-img-file");

// Copy to clipboard
document.querySelectorAll(".copy-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const targetId = btn.getAttribute("data-target");
    const el = document.getElementById(targetId);
    navigator.clipboard.writeText(el.value || "").then(() => {
      btn.textContent = "Copied!";
      setTimeout(() => (btn.textContent = "Copy"), 1500);
    });
  });
});

// Hash generator
document.getElementById("hash-gen-btn").addEventListener("click", () => {
  const algo = document.getElementById("hash-gen-algo").value;
  const text = document.getElementById("hash-gen-text").value;
  const fileInput = document.getElementById("hash-gen-file");

  const form = new FormData();
  form.append("algorithm", algo);
  form.append("text", text);
  if (fileInput.files[0]) {
    form.append("file", fileInput.files[0]);
  }

  fetch("/api/hash/generate", {
    method: "POST",
    body: form,
  })
    .then(r => r.json())
    .then(data => {
      const out = document.getElementById("hash-gen-output");
      if (data.error) {
        out.value = "Error: " + data.error;
      } else {
        out.value = data.hash;
      }
    });
});

// Hash identifier
document.getElementById("hash-id-btn").addEventListener("click", () => {
  const hash = document.getElementById("hash-id-input").value;
  const form = new FormData();
  form.append("hash", hash);

  fetch("/api/hash/identify", {
    method: "POST",
    body: form,
  })
    .then(r => r.json())
    .then(data => {
      const out = document.getElementById("hash-id-output");
      if (data.error) {
        out.value = "Error: " + data.error;
      } else {
        out.value =
          "Candidates: " + (data.candidates || []).join(", ") +
          "\nNote: " + (data.note || "");
      }
    });
});

// Hash verifier

// Crypto text
function getRailsOrKey(scheme, keyField) {
  const schemeVal = scheme.value;
  const raw = keyField.value;
  if (schemeVal === "RAILFENCE") {
    return { rails: raw };
  }
  return { key: raw };
}

document.getElementById("crypto-text-encrypt").addEventListener("click", () => {
  const scheme = document.getElementById("crypto-text-scheme");
  const keyField = document.getElementById("crypto-text-key");
  const text = document.getElementById("crypto-text-input").value;
  const out = document.getElementById("crypto-text-output");

  const form = new FormData();
  form.append("scheme", scheme.value);
  form.append("text", text);

  const extra = getRailsOrKey(scheme, keyField);
  if (extra.key !== undefined) form.append("key", extra.key);
  if (extra.rails !== undefined) form.append("rails", extra.rails);

  fetch("/api/crypto/text/encrypt", { method: "POST", body: form })
    .then(r => r.json())
    .then(data => {
      out.value = data.error ? "Error: " + data.error : (data.ciphertext || "");
    });
});

document.getElementById("crypto-text-decrypt").addEventListener("click", () => {
  const scheme = document.getElementById("crypto-text-scheme");
  const keyField = document.getElementById("crypto-text-key");
  const text = document.getElementById("crypto-text-input").value;
  const out = document.getElementById("crypto-text-output");

  const form = new FormData();
  form.append("scheme", scheme.value);
  form.append("text", text);

  const extra = getRailsOrKey(scheme, keyField);
  if (extra.key !== undefined) form.append("key", extra.key);
  if (extra.rails !== undefined) form.append("rails", extra.rails);

  fetch("/api/crypto/text/decrypt", { method: "POST", body: form })
    .then(r => r.json())
    .then(data => {
      out.value = data.error ? "Error: " + data.error : (data.plaintext || "");
    });
});

// Crypto image
function downloadBlobFromResponse(response) {
  return response.blob().then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "hashify_file";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  });
}

document.getElementById("crypto-img-encrypt").addEventListener("click", () => {
  const scheme = document.getElementById("crypto-img-scheme").value;
  const key = document.getElementById("crypto-img-key").value;
  const fileInput = document.getElementById("crypto-img-file");

  const form = new FormData();
  form.append("scheme", scheme);
  form.append("key", key);
  if (fileInput.files[0]) {
    form.append("file", fileInput.files[0]);
  }

  fetch("/api/crypto/image/encrypt", { method: "POST", body: form })
    .then(resp => {
      if (!resp.ok) {
        return resp.json().then(d => {
          alert("Error: " + (d.error || "Unknown"));
        });
      }
      downloadBlobFromResponse(resp);
    });
});

document.getElementById("crypto-img-decrypt").addEventListener("click", () => {
  const scheme = document.getElementById("crypto-img-scheme").value;
  const key = document.getElementById("crypto-img-key").value;
  const fileInput = document.getElementById("crypto-img-file");

  const form = new FormData();
  form.append("scheme", scheme);
  form.append("key", key);
  if (fileInput.files[0]) {
    form.append("file", fileInput.files[0]);
  }

  fetch("/api/crypto/image/decrypt", { method: "POST", body: form })
    .then(resp => {
      if (!resp.ok) {
        return resp.json().then(d => {
          alert("Error: " + (d.error || "Unknown"));
        });
      }
      downloadBlobFromResponse(resp);
    });
});