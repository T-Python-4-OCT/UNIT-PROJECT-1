Markdown
# Cybercrime SOC Management Console

A professional, terminal-based Security Operations Center (SOC) Console developed in Python. This interactive application empowers security analysts and administrators to manage cyber incident cases, execute analytical threat tracking, apply Role-Based Access Control (RBAC), and trigger dynamic notification responses.

---

## 📁 Repository & Project Directory Structure

```text
UNIT-PROJECT-1/
│
├── main.py                    # Application entry point & interactive CLI workflow
├── cyber_cases.json           # Persistent JSON storage for incident cases
├── requirements.txt           # External Python package dependencies
├── .gitignore                 # Tracked files and directory exclusion rules
├── README.md                  # Comprehensive project documentation
│
└── services/                  # Core application logic package
    ├── __init__.py            # Package initialization marker
    └── storage.py             # Data handling, RBAC, password hashing & alert logic

🔑 Default Credentials (RBAC Testing)For evaluation and testing purposes, use the following pre-configured account credentials:
Role                        Username          PasswordSOC

SOCAdministratoradmin       admin              123

  Security Analystanalyst   analyst            456



🛠️ Features & User Stories
As a Security Analyst or SOC Administrator, I can:
Authentication & Access Control: Securely authenticate using SHA-256 hashed password verification and role enforcement (Admin vs. Analyst).

Browse & Query Incidents: Display all stored security incidents in styled, interactive table formats and query specific cases by ID or keyword.

Synthetic Incident Generation: Dynamically generate realistic mock cybersecurity incidents leveraging the Faker library (Admin privilege required).

Dashboard Threat Analytics: Access real-time analytics displaying total case counts, severity distributions (High / Medium / Low), and investigation states.

Incident Lifecycle Management: Update case investigation statuses (Open, Under Investigation, Closed) with input validation.

Automated Alerting System: Dispatch HTML-formatted email alerts upon detecting or escalating critical security threats.

💡 Technologies & Dependencies Used
Python 3.x: Primary development language.

rich: Interactive terminal rendering, color styling, and dynamic tables.

faker: Synthetic data generation for incident titles, threat vectors, and case severities.

hashlib (Built-in): SHA-256 cryptographic password hashing for user authentication.

json (Built-in): Persistent file-based storage for case records and user state.

💻 Installation & Usage Instructions
1. Requirements Setup
Ensure all required Python packages are installed:

Bash
pip install -r requirements.txt
2. Launching the Application
Execute the application entry point from the root directory:

Bash
python main.py
3. Application Workflow & Navigation:
Login: Authenticate using pre-configured user credentials (e.g., username admin or analyst).

List Cases: View all active security cases rendered in formatted tables.

Search: Search cases by entering a target Case ID or incident keyword.

Generate Cases: (Admin Only) Specify the quantity of mock security incidents to auto-generate using Faker.

Update Case Status: Modify the investigation phase of any case record.

View Analytics: Access the dashboard panel for aggregate metrics and threat breakdowns.

Exit: Safely persist all modified data to cyber_cases.json and terminate the session.