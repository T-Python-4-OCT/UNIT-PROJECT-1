# 🔐 CLI Password Manager

A secure, lightweight, and interactive command-line interface (CLI) password manager built with Python. It allows users to securely store, manage, and generate strong credentials locally with environment configuration security.

---

## ✨ Features

- **Interactive CLI Menu**: Easy-to-navigate terminal interface powered by `colorama` for clean visual styling.
- **Popular Sites Quick Selection**: Pre-configured menu options for popular platforms (Gmail, GitHub, Twitter, etc.) to prevent spelling errors and maintain data consistency.
- **Secure Masking**: Displays masked passwords in summary views while preserving actual data integrity.
- **Strong Password Generator**: Automatically generates robust, randomized passwords containing letters, numbers, and special symbols.
- **Vault Statistics & Dashboard**: View summary analytics regarding total accounts and unique managed sites.
- **Environment Security (`.env`)**: Uses `python-dotenv` and sensitive configuration management adhering to academic best practices.
- **Version Control Safety**: Protected via `.gitignore` to prevent secret leaks on GitHub.

---

## 🛠️ Project Architecture

- `main.py`: The entry point and core controller handling the CLI loop and user interactions[cite: 1, 2].
- `file_manager.py`: Manages JSON I/O operations and reads configurations safely from environment variables[cite: 1, 2].
- `models.py`: Defines the `VaultItem` class structure and serialization methods[cite: 1, 2].
- `.env`: Stores confidential environment variables (Ignored by Git)[cite: 1, 2].

---