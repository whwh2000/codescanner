import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import re
from PIL import Image
import requests
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CodeScan",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.block-container { max-width: 520px; padding-top: 1.5rem; }

.result-found {
    background: rgba(0,229,160,0.08);
    border: 1px solid rgba(0,229,160,0.35);
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 12px;
}
.result-notfound {
    background: rgba(255,77,109,0.08);
    border: 1px solid rgba(255,77,109,0.35);
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 12px;
}
.result-title-found { color: #00e5a0; font-size: 1.1rem; font-weight: 800; margin-bottom: 6px; }
.result-title-nf    { color: #ff4d6d; font-size: 1.1rem; font-weight: 800; margin-bottom: 6px; }
.code-display {
    font-family: 'DM Mono', monospace;
    font-size: 1.5rem;
    letter-spacing: 4px;
    color: #e8e8f0;
    margin: 8px 0;
}
.data-row  { font-size: 0.85rem; margin: 3px 0; color: #c0c0d0; }
.data-key  { color: #6b6b8a; font-family: 'DM Mono', monospace; font-size: 0.78rem; }
.hist-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 12px;
    background: #1c1c28;
    border-radius: 8px;
    margin-bottom: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    color: #e8e8f0;
}
.dot-found    { color: #00e5a0; }
.dot-notfound { color: #ff4d6d; }
.model-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #6b6b8a;
    background: #1c1c28;
    border: 1px solid #2a2a3d;
    border-radius: 20px;
    padding: 2px 10px;
    margin-left: 8px;
    vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '## 🔍 CodeScan '
    '<span class="model-badge">gemini-3-flash-preview</span>',
    unsafe_allow_html=True,
)
st.markdown("Photograph a handwritten 11-digit code to look it up instantly.")
st.divider()

# ── Model ID ──────────────────────────────────────────────────────────────────
MODEL_ID = "gemini-3-flash-preview"

# ── Load secrets ──────────────────────────────────────────────────────────────
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    gemini_key = None

try:
    sheet_url_raw = st.secrets["GOOGLE_SHEET_URL"]
except Exception:
    sheet_url_raw = None

if not gemini_key:
    st.error("❌ `GEMINI_API_KEY` not found in Streamlit secrets.")
    st.stop()

if not sheet_url_raw:
    st.error("❌ `GOOGLE_SHEET_URL` not found in Streamlit secrets.")
    st.stop()

# ── Gemini client (new google-genai SDK) ──────────────────────────────────────
client = genai.Client(api_key=gemini_key)

# ── Google Sheet loader ───────────────────────────────────────────────────────
def sheet_to_csv_url(url: str) -> str:
    """Convert any Google Sheets sharing URL to a direct CSV export URL."""
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError("Could not find a spreadsheet ID in the URL.")
    sheet_id = match.group(1)
    gid_match = re.search(r"[#&?]gid=(\d+)", url)
    gid = gid_match.group(1) if gid_match else "0"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


@st.cache_data(ttl=300)  # refresh every 5 minutes
def load_sheet(url: str) -> pd.DataFrame:
    csv_url = sheet_to_csv_url(url)
    response = requests.get(csv_url, timeout=15)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text), dtype=str).fillna("")
    return df


with st.spinner(""):
    try:
        db = load_sheet(sheet_url_raw)
    except Exception as e:
        st.error(
            f"❌ Could not load Google Sheet: {e}\n\n"
            "Check that the sheet is shared as **Anyone with the link can view**."
        )
        st.stop()

# ── Session state ─────────────────────────────────────────────────────────────
if "history"   not in st.session_state: st.session_state.history   = []
if "last_code" not in st.session_state: st.session_state.last_code = ""

# ── Camera / image input ──────────────────────────────────────────────────────
st.markdown("### 📷 Scan Code")
img_file = st.camera_input("Point at the handwritten code and capture")

if img_file is None:
    img_file = st.file_uploader(
        "Or upload a photo", type=["jpg", "jpeg", "png"], key="photo_upload"
    )

# ── OCR with Gemini 3 Flash Preview ──────────────────────────────────────────
if img_file:
    image = Image.open(img_file)
    st.image(image, caption="Captured image", use_column_width=True)

    with st.spinner(f"Reading code with {MODEL_ID}..."):
        try:
            # Convert PIL image to bytes for the new SDK
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            prompt = (
                "This image contains a handwritten alphanumeric code. "
                "The code is exactly 11 characters long and contains uppercase letters and digits (e.g. MMYQ6KD4D96). "
                "Extract the full code exactly as written - preserve every letter and digit. "
                "Return ONLY the 11-character code with no spaces, dashes, punctuation, or explanation. "
                "If you see multiple codes return the most prominent one. If unsure about a character make your best guess."
            )

            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[
                    types.Part.from_bytes(
                        data=img_bytes.read(),
                        mime_type="image/jpeg",
                    ),
                    prompt,
                ],
                # "minimal" thinking — fast OCR doesn't need deep reasoning
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_level="minimal"
                    )
                ),
            )

            raw    = response.text.strip()
            digits = re.sub(r"[^A-Za-z0-9]", "", raw).upper()  # keep letters too

        except Exception as e:
            st.error(f"Gemini OCR error: {e}")
            digits = ""

    st.markdown(f"**Detected code:** `{digits or '(nothing detected)'}`")
    st.session_state.last_code = digits

# ── Lookup ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 🔎 Lookup")

col1, col2 = st.columns([3, 1])
with col1:
    search_code = st.text_input(
        "code",
        value=st.session_state.last_code,
        max_chars=20,
        placeholder="Edit or enter 11-digit code",
        label_visibility="collapsed",
    )
with col2:
    search_btn = st.button("Search", use_container_width=True, type="primary")


def do_lookup(code_raw: str):
    code = re.sub(r"[^A-Za-z0-9]", "", code_raw).upper()
    if not code:
        st.warning("No code to search.")
        return

    first_col = db.columns[0]
    db_clean  = db[first_col].str.replace(r"[^A-Za-z0-9]", "", regex=True).str.upper()
    matches   = db[db_clean == code]

    if not matches.empty:
        row  = matches.iloc[0]
        html = (
            '<div class="result-found">'
            f'<div class="result-title-found">✅ Code Found!</div>'
            f'<div class="code-display">{code}</div>'
        )
        for k, v in row.items():
            if v:
                html += f'<div class="data-row"><span class="data-key">{k}:</span> {v}</div>'
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
        st.session_state.history.insert(0, {"code": code, "found": True})
    else:
        st.markdown(
            f'<div class="result-notfound">'
            f'<div class="result-title-nf">❌ Code Not Found</div>'
            f'<div class="code-display">{code}</div>'
            f'<div class="data-row">No record found in the database.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.session_state.history.insert(0, {"code": code, "found": False})

    st.session_state.history = st.session_state.history[:20]


if search_btn and search_code:
    do_lookup(search_code)

# ── History ───────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.divider()
    st.markdown("### 🕐 Scan History")
    for item in st.session_state.history:
        dot = '<span class="dot-found">●</span>' if item["found"] else '<span class="dot-notfound">●</span>'
        st.markdown(
            f'<div class="hist-item">{dot}&nbsp;&nbsp;{item["code"]}</div>',
            unsafe_allow_html=True,
        )