# domain_management

A Python-based toolkit to automate and manage domains — including A record updates, domain forwarding, and pulling stats from EmailBison.

## ✨ Overview

This project is designed to help you:
- Automate domain tasks such as adding A records, setting up forwarding, and more.
- Integrate with [EmailBison](https://emailbison.com) to retrieve domain lists and calculate usage stats.
- Output data to CSV for easy viewing and reporting.

## 📁 Features

- 🔧 Add or update A records
- 🌐 Set up and manage domain forwarding
- 📊 Pull domain usage stats from EmailBison
- 🧮 Generate and export stats to CSV
- ⚙️ Fully configurable via `.env` and `config.py`

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `pip` installed

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/domain_management.git
   cd domain_management
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a .env file:

   ```bash
   cp .env.example .env
   ```

4. Edit the .env file and config.py with your settings.

5. Run the script you want to run.