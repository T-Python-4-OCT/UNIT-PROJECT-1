# 🤖 AgentOS - Autonomous AI Agent & System OS (CLI)

> An advanced, immersive command-line interface (CLI) platform designed for managing, purchasing, testing, and deploying autonomous AI agent clusters. Built with Python and Rich, featuring rich terminal UI, dynamic themes, cryptographic governance, and modular software architecture.

---

## 📌 Project Overview

**AgentOS** is a futuristic terminal-based operating system and marketplace simulation. It allows developers and administrators to browse, configure, purchase, test, and deploy autonomous artificial intelligence agents. The system features two distinct user roles: **Customers (Developers)** and **Managers (Administrators)**, supported by a cryptographic governance vault, secure wallet transactions, persistent shopping cart management, and interactive diagnostic modules.

---

## 🎯 Project Goals & Purpose

The primary objective of AgentOS is to deliver a comprehensive, robust, and visually stunning CLI application that demonstrates advanced software engineering principles:

- **Modular Architecture:** Clean separation of concerns across core logic, UI animations, database state management, and business services.
- **Cryptographic Security:** Fernet-encrypted receipts and immutable transaction governance for enterprise-grade auditability.
- **Immersive Developer Experience:** High-end cyberpunk terminal aesthetics with dynamic theme engines, progress indicators, and interactive mini-games.
- **Data Persistence:** Local JSON state management ensuring all user carts, registered agents, token balances, audit logs, and encrypted receipts persist across application restarts.

---

## ✨ Key Features

### 🛒 Marketplace & Persistent Shopping Cart

- **Browse AI Catalogue:** Explore available AI agents with real-time fluctuating market pricing and specializations.
- **Smart Search & Recommendations:** Search agents by keyword or receive tailored recommendations based on past purchase history.
- **Persistent Cart:** Items added to the shopping cart persist across application restarts until checked out or explicitly removed.
- **Secure Checkout:** Complete purchases using platform tokens (TC) with strict input validation for customer names, 10-digit mobile numbers, and 16-digit bank card numbers.

### 🧪 AI Model Sandbox & Benchmarking Suite

- **Performance Testing:** Launch interactive test suites for any AI model to measure Confidence, Accuracy, and Speed.
- **Report Exporting:** Save benchmark test reports directly to `benchmark_report.txt`.

### 🛡️ Cryptographic Governance Vault & Manager Portal

- **Administrator Command Center:** Secure PIN-protected manager login (PIN: `1234`, hidden behind hint prompt).
- **Encrypted Receipts Ledger:** View all immutable transaction records (Agent purchases, Token top-ups, Promo code redemptions, Mini-game rewards) securely protected via Fernet symmetric encryption (`receipts.json`).
- **Inventory & Stock Control:** Monitor stock quantities and register new custom AI agents to the live marketplace.
- **Data Reset & CSV Export:** Export telemetry data to CSV reports or securely reset system state when needed.

### 💳 Wallet, Finance & Promo System

- **Token Top-Up:** Recharge wallet balances with bank card validation and encrypted logging.
- **Promo Code Redemption:** Claim promotional discount coupons (e.g., `GRAD2026`, `CYBER100`, `VIP2026`) with user identification tracking.

### 🕹️ ASCII Glitch Restorer Mini-Game

- **Interactive Gameplay:** Restore corrupted artwork pixels using arrow keys within a 15-second timer.
- **Performance Rewards:** Automatically earn tokens based on restoration integrity percentage, recorded securely in the cryptographic vault.

### 🎨 Dynamic Terminal Theme Engine

- Switch between multiple visual themes (**Cyberpunk Neon**, **Matrix Hacker**, **Gold Luxury**) with instant UI updates across banners, panels, and borders.

---

## 📂 Project Architecture

```text
UNIT-PROJECT-1/
│
├── core/                   # Core system logic & security
│   ├── __init__.py
│   ├── crypto_receipts.py  # Fernet encryption & secure vault ledger
│   ├── database.py         # Local JSON state management & validation
│   └── logger.py           # System audit logging engine
│
├── ui/                     # Visual interface & themes
│   ├── __init__.py
│   ├── animations.py       # Terminal banners, spinners, and theme colors
│   ├── dashboard.py        # Live system dashboard & telemetry cards
│   ├── dashboard_matrix.py # Split-screen matrix monitoring
│   └── menus.py            # Questionary navigation menus & status panels
│
├── services/               # Business logic & operations
│   ├── checkout.py         # Payment processing & digital certificates
│   ├── manager.py          # Administrator portal & inventory control
│   ├── minigame.py         # ASCII Glitch Restorer interactive mini-game
│   ├── sandbox.py          # AI model testing suite & benchmarks
│   ├── store.py            # Marketplace, cart, recommendations & promo codes
│   └── synergy.py          # Operator ranking & tactical synergy reports
│
├── tests/                  # Automated test suite (pytest)
│   ├── test_crypto_receipts.py
│   ├── test_export.py
│   ├── test_logger.py
│   ├── test_market.py
│   ├── test_minigame.py
│   └── test_sandbox.py
│
├── main.py                 # Main application entry point
├── requirements.txt        # Project Python dependencies
└── README.md               # Comprehensive project documentation
```

---

## ⚙️ Installation & Setup Instructions

### Prerequisites

- Python 3.10 or higher installed on your system.

### Step 1: Clone or Navigate to Project Directory

Open your terminal and navigate to the project directory:

```bash
cd UNIT-PROJECT-1
```

### Step 2: Install Dependencies

Install all required Python packages (Rich, Questionary, Cryptography, Pytest):

```bash
pip install -r requirements.txt
```

### Step 3: Run the Application

Launch the AgentOS command-line interface:

```bash
python main.py
```

### Step 4: Run Automated Tests

To verify system integrity and execute the pytest test suite:

```bash
python -m pytest
```

---

## 🕹️ User Guide & Navigation

Upon running `python main.py`, use your keyboard **Arrow Keys** to navigate and **Enter** to select options:

1. **Marketplace & Store:** Browse agents, search catalogue, get AI recommendations, manage your persistent cart, and execute secure checkouts.
2. **AI Sandbox & Simulations:** Test AI models, run the split-screen matrix dashboard, or play the ASCII Glitch Restorer mini-game to earn wallet tokens.
3. **Wallet & Finance Hub:** Top-up wallet tokens or redeem promo codes.
4. **System Reports & Analytics:** View live system dashboards, audit logs, or export reports to CSV.
5. **Administration & Theme Engine:** Access the Manager Portal (PIN: `1234`) or switch terminal themes instantly.
