# 🔍 CodeScan

Photograph a handwritten 11-digit code with your phone and look it up against a Google Sheet database — powered by **Gemini 3 Flash Preview**, Google's fastest frontier-class vision model.

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

## Model: `gemini-3-flash-preview`

This app uses **Gemini 3 Flash Preview** (`gemini-3-flash-preview`) — Google's latest generation model, offering Pro-level intelligence at Flash speed and cost. Key advantages for OCR:

- Significantly better handwriting recognition than Gemini 2.0/2.5 Flash
- Thinking set to `MINIMAL` mode for fast, low-latency OCR responses
- Free tier available via Google AI Studio API key
- Multimodal — handles images natively

The SDK used is `google-genai` (the new unified SDK), which replaces the older `google-generativeai` package.

---

## 🚀 Setup — Step by Step

### STEP 1 — Prepare your Google Sheet

1. Open [Google Sheets](https://sheets.google.com) and open or create your sheet
2. **Row 1 must be a header row** — first column = 11-digit codes:

   | code        | name      | status  | notes    |
   |-------------|-----------|---------|----------|
   | 12345678901 | Widget A  | active  | Shelf B3 |
   | 98765432100 | Widget B  | expired |          |

3. Share the sheet:
   - Click **Share** → **Change to anyone with the link** → set to **Viewer** → **Copy link**
   - Save this URL — you'll need it in Step 5

> ✅ Edit the sheet anytime. The app picks up changes within 5 minutes automatically.

---

### STEP 2 — Get a free Gemini API key

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API key**
4. Copy the key (`AIza...`) and store it safely

> `gemini-3-flash-preview` has a free tier — no billing needed for typical scan volumes.

---

### STEP 3 — Create a private GitHub repo

1. Go to [github.com](https://github.com) → **New repository**
2. Name it `codescan`, set to **Private**, click **Create**
3. Click **Add file → Upload files** and upload:
   - `app.py`
   - `requirements.txt`
   - `.gitignore`
   - `README.md`

   ⚠️ **Do NOT upload** `.streamlit/secrets.toml`

4. Click **Commit changes**

---

### STEP 4 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) → sign in with GitHub
2. Click **New app**
3. Select your `codescan` repo
4. Set **Main file path** → `app.py`
5. Click **Deploy** (takes ~1–2 minutes)

---

### STEP 5 — Add secrets to Streamlit Cloud

1. In the Streamlit Cloud dashboard → your app → **⋮ menu → Settings → Secrets**
2. Paste:

```toml
GEMINI_API_KEY = "AIza...your-key..."
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_ID/edit?usp=sharing"
```

3. Click **Save** — the app restarts with secrets loaded

---

### STEP 6 — Share the app URL

Your URL will look like `https://your-name-codescan-xxxx.streamlit.app`. Send it to any user — they never see the API key or Sheet URL.

---

## 💻 Run locally

```bash
pip install -r requirements.txt

# Fill in .streamlit/secrets.toml with your real values, then:
streamlit run app.py
```

---

## 📱 Using the App

1. Tap the camera button → point at the handwritten code → capture
2. Gemini 3 Flash reads the digits automatically
3. Edit the code in the text box if needed → hit **Search**
4. ✅ Green = found (shows all spreadsheet data), ❌ Red = not found
5. Last 20 scans shown in history at the bottom

---

## 🔄 Updating the database

Edit your Google Sheet anytime — no redeployment needed. The app re-fetches every 5 minutes. Reload the page for an instant refresh.

---

## 🔒 Security summary

| What             | Where it lives                    | Exposed to users? |
|------------------|-----------------------------------|-------------------|
| Gemini API key   | Streamlit Cloud encrypted secrets | ❌ Never          |
| Google Sheet URL | Streamlit Cloud encrypted secrets | ❌ Never          |
| Sheet data       | Fetched server-side at runtime    | Match results only|
| Scan history     | Browser session memory            | Current user only |

---

## SDK migration note

This app uses the **new `google-genai` SDK** (v1.5+), not the older `google-generativeai` package. The new SDK is required for Gemini 3 models. The import style has changed:

```python
# Old (Gemini 2.x)
import google.generativeai as genai

# New (Gemini 3)
from google import genai
from google.genai import types
```