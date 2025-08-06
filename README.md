# 🐍 Reverse Shell Backdoor

A feature-rich Python-based reverse shell that establishes a remote connection between a client and a server.

> ⚠️ **Disclaimer:** This tool is for educational and ethical cybersecurity research only. Misuse is strictly prohibited. See [disclaimer.md](./disclaimer.md) for full legal notice.

---

## 🧠 Overview

This tool enables full remote control over a target machine through a reverse shell connection. Key functionalities include command execution, file transfer, screen capture, keystroke monitoring, and persistence.

The project is divided into two parts:
- **Client** — the payload running on the target system
- **Server** — command & control interface to manage the client

---

## ✨ Features

| Feature           | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| 💻 Remote Shell   | Execute OS commands directly on the client machine                         |
| 🔁 File Transfer   | Upload and download files from/to the target system                        |
| 📸 Screenshot      | Capture screenshots of the client screen                                   |
| ⌨️ Keylogger      | Log keystrokes and retrieve logs remotely                                   |
| 🔒 Persistence     | Adds itself to Windows startup registry for persistence                    |
| 🔌 Reconnection    | Automatically reconnects if the connection drops                           |

---

## 📁 File Structure

- `server.py` — The control center for interacting with infected machines  
- `reverse_shell.py` — The reverse shell payload  
- `keylogger.py` — Lightweight keylogger module  
- `cutecat.ico` — Optional icon disguise  
- `disclaimer.md` — Legal notice for ethical usage

---

## ⚙️ Usage

### Server
```bash
python server.py
```

### Client
```bash
python reverse_shell.py
```

## 🚫 Legal & Ethical Use
This project is intended **strictly for educational purposes**, ethical hacking, and cybersecurity research in controlled environments.

**⚠️ Unauthorized use of this tool on systems you do not own or have explicit permission to test is illegal and strictly prohibited.**

By using this code, you agree that:
- You are solely responsible for how you use it
- The author is not liable for any misuse or damage
- You will use it **only** in compliance with local laws and regulations

See [disclaimer.md](./disclaimer.md) for the full legal disclaimer.