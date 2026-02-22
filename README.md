# 🔍 CodeScan

Photograph a handwritten 11-digit code with your phone and look it up against a Google Sheet database — powered by Gemini Vision AI. No CSV upload needed; the sheet is the single source of truth and refreshes automatically every 5 minutes.

---

## File structure

```
codescan/
├── app.py                    ← Streamlit app
├── requirements.txt          ← Python dependencies
├── .gitignore                ← Keeps secrets off GitHub
├── .streamlit/
│   └── secrets.toml          ← Local secrets (never committed)
└── README.md
```

---

## 🚀 Full Setup — Step by Step

---

### STEP 1 — Prepare your Google Sheet

1. Open [Google Sheets](https://sheets.google.com) and create a new sheet (or open your existing one)
2. Make sure **Row 1 is a header row** — the first column must contain the 11-digit codes:

   | code        | name      | status  | notes     |
   |-------------|-----------|---------|-----------|
   | 12345678901 | Widget A  | active  | Shelf B3  |
   | 98765432100 | Widget B  | expired |           |

3. Share the sheet publicly:
   - Click **Share** (top right)
   - Click **Change to anyone with the link**
   - Set permission to **Viewer**
   - Click **Copy link** — save this URL, you'll need it in Step 4

> ✅ You can update the sheet at any time. The app picks up changes within 5 minutes automatically.

---

### STEP 2 — Get a free Gemini API key

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API key**
4. Copy the key (starts with `AIza...`) — keep it safe

> The free Gemini tier gives ~1,500 requests/day — plenty for a scanning tool.

---

### STEP 3 — Create a GitHub repository

1. Go to [github.com](https://github.com) and sign in (create a free account if needed)
2. Click the **+** icon → **New repository**
3. Name it `codescan`, set visibility to **Private**, click **Create repository**
4. Upload these files using **Add file → Upload files**:
   - `app.py`
   - `requirements.txt`
   - `.gitignore`
   - `README.md`

   ⚠️ **Do NOT upload** `.streamlit/secrets.toml` — the `.gitignore` protects you,
   but visually confirm it's not in your selection before committing.

5. Click **Commit changes**

---

### STEP 4 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **New app**
4. Choose your `codescan` repository
5. Set **Main file path** → `app.py`
6. Click **Deploy**

Streamlit will install dependencies and start the app. It takes about 1–2 minutes on first deploy.

---

### STEP 5 — Add secrets to Streamlit Cloud

This is where you securely store your API key and Sheet URL — they never touch GitHub.

1. In the Streamlit Cloud dashboard, find your deployed app
2. Click the **⋮ (three dots)** menu → **Settings**
3. Click the **Secrets** tab
4. Paste the following, replacing the placeholder values:

```toml
GEMINI_API_KEY = "AIza...your-key-here..."
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit?usp=sharing"
```

5. Click **Save** — the app restarts automatically with the secrets loaded

---

### STEP 6 — Share the app

Your app URL will look like:
```
https://your-username-codescan-app-xxxx.streamlit.app
```

Find it on your [share.streamlit.io](https://share.streamlit.io) dashboard. Send it to anyone — they just open the link and scan. They never see or interact with the API key or Sheet URL.

---

## 💻 Run locally (optional)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Edit .streamlit/secrets.toml with your real values
#    (this file is gitignored so it stays local)

# 3. Run
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📱 Using the App

1. **Tap the camera button** — point at the handwritten code, capture
2. **Review the detected digits** — edit in the text box if Gemini missed a digit
3. **Hit Search** — green card = found with full row data, red = not found
4. **Scan history** — last 20 scans shown at the bottom; tap any to re-search

---

## 🔄 Updating the database

Just edit your Google Sheet. No redeployment needed — the app re-fetches the sheet every 5 minutes automatically. If you need an instant refresh during a session, you can reload the page.

---

## 🔒 Security summary

| What            | Where it lives                        | Exposed to users? |
|-----------------|---------------------------------------|-------------------|
| Gemini API key  | Streamlit Cloud encrypted secrets     | ❌ Never          |
| Google Sheet URL| Streamlit Cloud encrypted secrets     | ❌ Never          |
| Sheet data      | Fetched server-side at runtime        | Only match results|
| Scan history    | Browser session memory only           | Current user only |
