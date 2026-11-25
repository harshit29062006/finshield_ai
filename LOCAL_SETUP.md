# FinShield AI — Local Setup Guide

> Step-by-step instructions to run the full project on your own laptop.

---

## What You Will Be Running

| Part | Technology | URL after startup |
|------|-----------|-------------------|
| **Backend API** | Python / FastAPI | http://localhost:8000 |
| **Frontend** | React / Vite | http://localhost:5173 |
| **Database** | PostgreSQL | localhost:5432 |

---

## Prerequisites

Install these once. Skip anything you already have.

### 1. Python 3.11 or 3.12
Download from https://www.python.org/downloads/  
During installation, **tick "Add Python to PATH"**.

Verify in a new terminal:
```
python --version
```

### 2. Node.js 20 (LTS)
Download from https://nodejs.org/  
The installer includes `npm` automatically.

Verify:
```
node --version
npm --version
```

### 3. PostgreSQL 16
Download from https://www.postgresql.org/download/windows/  
Run the installer. When it asks for a **superuser password**, choose something you will remember (e.g. `postgres`). Keep the default port **5432**.

Verify (open **SQL Shell (psql)** from the Start menu, press Enter for every prompt, type the password):
```
\q
```
If that opens and closes without error, PostgreSQL is working.

### 4. Git (optional, only needed to clone)
Download from https://git-scm.com/download/win

---

## Step 1 — Get the Code

If you received a ZIP file, extract it. You should have a folder called `finshield_ai` with this layout:

```
finshield_ai/
├── code/
│   ├── backend/
│   ├── frontend/
│   └── ml/
└── LOCAL_SETUP.md   ← this file
```

> **If you have Git**, you can clone instead:
> ```
> git clone <repo-url>
> cd finshield_ai
> ```

---

## Step 2 — Create the Database

Open **SQL Shell (psql)** from the Start menu (or any terminal where `psql` is on the PATH) and run:

```sql
CREATE DATABASE finshield;
```

Then type `\q` and press Enter to exit.

> **Tip:** If you set a PostgreSQL password other than `postgres`, note it down — you will need it in Step 4.

---

## Step 3 — Set Up the Backend

Open a terminal (Windows Terminal, PowerShell, or Command Prompt) and navigate to the backend folder:

```
cd finshield_ai\code\backend
```

### 3a. Create a virtual environment

```
python -m venv venv
```

### 3b. Activate it

**PowerShell / Windows Terminal:**
```
venv\Scripts\Activate.ps1
```

**Command Prompt:**
```
venv\Scripts\activate.bat
```

You should see `(venv)` at the start of your prompt.

### 3c. Install Python packages

```
pip install -r requirements.txt
```

This may take a few minutes the first time.

---

## Step 4 — Configure the Backend

Still inside `code\backend`, copy the example environment file:

```
copy .env.example .env
```

Open the new `.env` file in Notepad (or any text editor). It looks like this:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/finshield
SECRET_KEY=replace-with-any-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=120
ML_MODEL_NAME=xgboost
```

**Only two things to change:**

1. **`DATABASE_URL`** — replace the second `postgres` (after the colon) with your PostgreSQL password.  
   Example: if your password is `mypassword`:
   ```
   DATABASE_URL=postgresql+psycopg2://postgres:mypassword@localhost:5432/finshield
   ```

2. **`SECRET_KEY`** — replace `replace-with-any-long-random-string` with any long random text.  
   Example: `SECRET_KEY=finshield-local-secret-2024`

Save and close the file.

---

## Step 5 — Create Demo Users

Still in `code\backend` with the virtual environment active:

```
python seed.py
```

This creates four demo accounts:

| Username   | Password       | Role               |
|------------|----------------|--------------------|
| `admin`    | `Admin@123`    | Admin              |
| `analyst`  | `Analyst@123`  | Fraud Analyst      |
| `officer`  | `Officer@123`  | Compliance Officer |
| `customer` | `Customer@123` | Customer           |

---

## Step 6 — Start the Backend

```
uvicorn app.main:app --reload
```

Leave this terminal open. You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

You can visit http://localhost:8000/docs to explore the API (optional).  
Check http://localhost:8000/health to confirm the ML models loaded.

---

## Step 7 — Set Up and Start the Frontend

Open a **second terminal** (keep the first one running the backend).

Navigate to the frontend folder:

```
cd finshield_ai\code\frontend
```

### 7a. Install Node packages

```
npm install
```

### 7b. Start the development server

```
npm run dev
```

You should see:

```
  VITE v5.x.x  ready in ...ms

  ➜  Local:   http://localhost:5173/
```

---

## Step 8 — Open the App

Go to **http://localhost:5173** in your browser.

Log in with any of the demo accounts from Step 5. The recommended account for exploring everything is **admin / Admin@123**.

---

## Stopping the App

- Press **Ctrl + C** in each terminal to stop the backend and frontend servers.
- PostgreSQL runs as a Windows service in the background — you do not need to do anything to stop it.

---

## Starting Again Next Time

You do not need to repeat the installation steps. Next time, just:

1. **Terminal 1 — Backend:**
   ```
   cd finshield_ai\code\backend
   venv\Scripts\Activate.ps1
   uvicorn app.main:app --reload
   ```

2. **Terminal 2 — Frontend:**
   ```
   cd finshield_ai\code\frontend
   npm run dev
   ```

3. Open http://localhost:5173

---

## Troubleshooting

### "python is not recognized"
Python was not added to PATH. Reinstall Python and tick **"Add Python to PATH"** on the first screen.

### "pip install" fails with a long error about psycopg2
Make sure PostgreSQL is installed. The `psycopg2-binary` package needs PostgreSQL's libraries.

### Backend shows `could not connect to server`
PostgreSQL is not running. Open **Services** (search in Start menu), find **postgresql-x64-16**, right-click → **Start**.

### Backend health check shows `ml_load_error`
The `.pkl` model files inside `code\ml\models\` are missing or the path is wrong. Make sure you have the full project folder including the `ml` subfolder.

### "CORS error" in the browser
Make sure the backend is running on port **8000** and the frontend on port **5173**. Do not change the port numbers.

### PowerShell says "execution of scripts is disabled"
Run this once in PowerShell as Administrator:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating the virtual environment again.

---

## Project Structure (for reference)

```
finshield_ai/
├── code/
│   ├── backend/              ← FastAPI backend (Python)
│   │   ├── app/              ← Application source code
│   │   ├── requirements.txt  ← Python dependencies
│   │   ├── .env.example      ← Environment variable template
│   │   ├── seed.py           ← Creates demo users
│   │   └── demo.py           ← Scripted API walkthrough
│   ├── frontend/             ← React frontend
│   │   ├── src/              ← React source code
│   │   ├── package.json      ← Node dependencies
│   │   └── vite.config.js    ← Dev server config
│   └── ml/
│       ├── models/           ← Trained .pkl model files
│       └── src/              ← ML and AML source modules
└── LOCAL_SETUP.md            ← This file
```

---

*FinShield AI — UCS503P Software Engineering Project, Thapar Institute of Engineering & Technology*
