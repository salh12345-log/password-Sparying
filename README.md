# Authentication Server with Login Monitoring (Simulation)

This project is a simple authentication server built using Python and Flask.  
It is designed for educational purposes to demonstrate how login systems work,
how login attempts are logged, and how basic account lockout mechanisms can be applied.

The project runs in a safe local environment (localhost only) and does not interact
with any external systems.

---

## Project Goals

- Implement a basic authentication server
- Handle user login requests using a REST API
- Log all login attempts with timestamps
- Apply temporary account lockout after repeated failed attempts
- Demonstrate defensive security concepts in practice

---

## Project Files

```
password-spraying-main/
│
├── server.py           Authentication server (Flask)
├── users_db.json       Local users database
├── login_logs.json     Log file for login attempts
├── requirements.txt    Required Python libraries
└── README.md           Project documentation
```

---

## How the System Works

1. The server receives login requests through an API endpoint.
2. The username and password are validated against a local JSON database.
3. Every login attempt is recorded in a log file.
4. If a user fails to log in multiple times, the account is temporarily locked.
5. Only requests from localhost are allowed to ensure a safe testing environment.

---

## Security Rules Applied

- Maximum failed login attempts: **5**
- Account lock duration: **3 minutes**
- Access restricted to localhost only (`127.0.0.1`)

---

## Installation and Running

### Requirements

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Server

```bash
python server.py
```

After running, the server will be available at:

```
http://127.0.0.1:5000
```

---

## API Endpoints

### Login

**POST** `/login`

Request example:
```json
{
  "username": "admin",
  "password": "Password123!"
}
```

Possible responses:
- `200` Login successful
- `401` Invalid username or password
- `423` Account temporarily locked
- `400` Missing username or password

---

### Health Check

**GET** `/health`

Response example:
```json
{
  "status": "running",
  "time": "2026-01-22T22:00:00"
}
```

---

## Logging

All login attempts are stored in the file:

```
login_logs.json
```

Each record contains:
- Date and time
- IP address
- Username
- Login status
- Reason for failure or success

This allows analysis of login behavior and testing of security controls.

---

## Usage Notes

- This project is for learning and testing only.
- All data is stored locally.
- No real user accounts or real passwords are used.
- The system is not intended for production environments.

---

## Conclusion

This project demonstrates the basic structure of an authentication server and shows
how simple security measures such as logging and account lockout can help protect
systems from repeated unauthorized access attempts.
