#  Password Spraying Attack Simulator with Intelligent Detection

![Python]
![Flask]
![Status]

A comprehensive security project that simulates a **Password Spraying** attack and implements an intelligent detection system. Built for educational purposes to understand modern authentication threats and defense mechanisms.

##  Key Features

*   **Realistic Attack Simulation**: Mimics real-world password spraying tactics with time delays and common password lists.
*   **Intelligent Detection Engine**: Advanced heuristics to identify spray patterns based on IP, time windows, and unique user targeting.
*   **Safety-First Design**: All attacks are confined to `localhost` with automatic account lockout protections.
*   **Interactive Dashboard**: A live web dashboard to visualize attack attempts, statistics, and detection alerts.
*   **Full Logging & Analysis**: Comprehensive JSON logging for post-attack analysis and reporting.

##  Quick Start

### Prerequisites
*   Python 3.8 or higher
*   pip (Python package installer)

### Installation & Run
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/password-spraying-simulator.git
    cd password-spraying-simulator
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the complete project:**
    ```bash
    python run_project.py
    ```
    *Follow the on-screen menu to launch all components.*

##  Project Architecture

The simulator is built from four core components that work together:

*   **`create_db.py`**: Creates a local JSON database of sample users and passwords.
*   **`server.py`**: The target authentication server (Flask app) with a `/login` endpoint.
*   **`client.py`**: The attacker client that performs the password spraying simulation.
*   **`detection.py`**: The detection engine that analyzes logs and identifies spray patterns.
*   **`dashboard.py`**: A web-based dashboard to monitor activity in real-time.
*   **`run_project.py`**: The main controller script to orchestrate all components.

##  How It Works

### 1. The Attack (Password Spraying)
Unlike brute-force attacks, the client (`client.py`) takes a **single common password** (e.g., `Winter2024!`) and tries it against a **list of many usernames**. It introduces random delays (2-5 seconds) between attempts to evade traditional, per-account lockout policies.

### 2. The Defense (Intelligent Detection)
The detection system (`detection.py`) monitors login attempts and flags suspicious activity not caught by simple thresholds. It triggers an alert if a single IP address attempts to log into **more than 5 different user accounts** within a short time window (e.g., 10 minutes).

### 3. The Dashboard
The live dashboard (`http://127.0.0.1:5001`) provides a visual overview, showing metrics like total attempts, active IPs, locked accounts, and detected threats with color-coded risk indicators.

## 🔧 Usage Details

### Running Components Individually
For development or testing, you can run each part separately (in order):

1.  **Set up the user database:**
    ```bash
    python create_db.py
    ```
2.  **Start the target authentication server:**
    ```bash
    python server.py
    ```
    *Server runs at: `http://127.0.0.1:5000`*
3.  **Launch the monitoring dashboard (new terminal):**
    ```bash
    python dashboard.py
    ```
    *Dashboard runs at: `http://127.0.0.1:5001`*
4.  **Execute the attack simulation (new terminal):**
    ```bash
    python client.py
    ```
5.  **Run the detection analysis:**
    ```bash
    python detection.py
    ```

### Key Project URLs
*   **Dashboard**: `http://127.0.0.1:5001`
*   **Server API**: `http://127.0.0.1:5000`
    *   `POST /login` - Main login endpoint
    *   `GET /logs` - View attempt logs
    *   `GET /stats` - Get server statistics

##  Example Output & Detection