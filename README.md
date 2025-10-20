<div align="center">
  <h2 align="center">Crypto.com Account Checker</h2>
  <p align="center">
    An automated tool for checking Crypto.com accounts with proxy handling and multi-threading capabilities.
    <br />
    <br />
    <a href="https://discord.cyberious.xyz">💬 Discord</a>
    ·
    <a href="#-changelog">📜 ChangeLog</a>
    ·
    <a href="https://github.com/sexfrance/Crypto-Account-Checker/issues">⚠️ Report Bug</a>
    ·
    <a href="https://github.com/sexfrance/Crypto-Account-Checker/issues">💡 Request Feature</a>
  </p>
</div>

---

### ⚙️ Installation

- Requires: `Python 3.7+`
- Make a python virtual environment: `python -m venv venv`
- Source the environment: `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (macOS, Linux)
- Install the requirements: `pip install -r requirements.txt`

---

### 🔥 Features

- Proxy support for avoiding rate limits
- Multi-threaded account checking
- Real-time checking tracking with console title updates
- Configurable thread count
- Debug mode for troubleshooting
- Proxy/Proxyless mode support
- Automatic token handling
- Detailed logging system
- Account data saving (email:phone format)
- Full account capture with region and country details

---

### 📝 Usage

1. **Configuration**:
   Edit `input/config.toml`:

   ```toml
   [dev]
   Debug = false
   Proxyless = false
   Threads = 1

   [data]
   password = "optional_custom_password"
   email_verified = true
   ```

2. **Proxy Setup** (Optional):

   - Add proxies to `input/proxies.txt` (one per line)
   - Format: `ip:port` or `user:pass@ip:port`

3. **Running the script**:

   ```bash
   python main.py
   ```

4. **Output**:
   - Checked accounts are saved to `output/valid.txt` (email:phone)
   - Invalid accounts saved to `output/invalid.txt`
   - Errors recorded in `output/error.txt`

---

### 📹 Preview

![Preview](https://i.imgur.com/c7yeYrQ.gif)

---

### ❗ Disclaimers

- This project is for educational purposes only
- The author is not responsible for any misuse of this tool
- Use responsibly and in accordance with Crypto.com's terms of service

---

### 📜 ChangeLog

```diff
v0.0.1 ⋮ 10/21/2025
! Initial release with proxy support and multi-threading
```

<p align="center">
  <img src="https://img.shields.io/github/license/sexfrance/Crypto-Account-Checker.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/stars/sexfrance/Crypto-Account-Checker.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/languages/top/sexfrance/Crypto-Account-Checker.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=python"/>
</p>
