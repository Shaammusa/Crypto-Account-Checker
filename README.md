<div align="center">
   <h2 align="center">Crypto.com Account Checker</h2>
   <p align="center">
      Automated checker that queries Crypto.com support chat to validate email+phone combinations.
      <br />
      <br />
      <a href="https://discord.cyberious.xyz">💬 Discord</a>
      ·
      <a href="#-changelog">📜 ChangeLog</a>
   </p>
</div>

---

### ⚙️ Requirements & Installation

- Requires: Python 3.10+ (project uses modern typing and libraries)
- Create a virtual environment and activate it:

```powershell
python -m venv venv
venv\Scripts\Activate
```

- Install dependencies (add packages to a requirements file if needed):

```powershell
pip install -r requirements.txt
```

---

### � Configuration

Edit `input/config.toml` to control behavior. Example:

```toml
[dev]
Debug = false
Proxyless = false
Threads = 4

[data]
# optional
password = "optional_custom_password"
```

- Add accounts to `input/accounts.txt` with one account per line in the format:

```
email@example.com:+1234567890
```

- Optional: add proxies to `input/proxies.txt` (one per line, format `ip:port` or `user:pass@ip:port`).

---

### 🔥 Features

- Reads `input/accounts.txt` (email:phone) and validates accounts concurrently.
- Proxy support via `input/proxies.txt` or proxyless mode controlled by `config.toml`.
- ThreadPool-based parallelism controlled by `Threads` setting.
- Retries failed checks up to 3 times and records exhausted failures to `output/error.txt`.
- Writes successful/invalid results to `output/valid.txt` and `output/invalid.txt`.
- Tolerant remote user-agent fetch (handles some malformed JSON).
- Phone region extraction using `phonenumbers` and `pycountry`.

---

### �️ Inputs & Outputs

- Inputs:

  - `input/accounts.txt` (required) — lines of `email:phone`
  - `input/proxies.txt` (optional)
  - `input/config.toml` (required)

- Outputs (in `output/`):
  - `valid.txt` — accounts marked valid (email:phone)
  - `invalid.txt` — accounts marked invalid (email:phone)
  - `error.txt` — accounts that failed after 3 retries (email:phone)

---

### � Usage

Run the script from the project root:

```powershell
python main.py
```

Press Ctrl+C to stop.

---

### ⚠️ Notes & Troubleshooting

- If you see "Failed to parse remote user agents", the remote file contains malformed JSON; the script will fall back to a default user-agent. You can avoid this by adding a local UA or removing the remote fetch.
- If you get authentication errors, ensure your network and proxies allow requests to `alfred-gateway.crypto.com` and that `input/config.toml` is configured correctly.

---

### 📜 ChangeLog

```
v0.1.0 - 2025-10-21
- Initial Crypto.com account checker implementation
```

<p align="center">
   <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="license"/>
</p>
