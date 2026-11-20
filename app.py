import html as _html
import io

import pandas as pd
import streamlit as st

from logic import (
    REQUIRED_COLUMNS,
    prepare_dataframe,
    validate_dataframe,
    summarize_dataframe,
    create_message,
)

st.set_page_config(
    page_title="ACTIVE LIFE – Vận động thể chất và thói quen ngồi",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PAGES = ["Trang chủ", "Tự kiểm tra thói quen", "Phân tích khảo sát", "Kiến thức & an toàn"]
PAGE_HOME, PAGE_CHECK, PAGE_ANALYSIS, PAGE_KNOWLEDGE = PAGES


# ---------------------------------------------------------------------------
# GIAO DIỆN: CSS + SVG (toàn bộ nằm trong app.py, không dùng tài nguyên ngoài
# ngoại trừ phông chữ Google Fonts có phương án dự phòng)
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

:root{
  --bg:#080D18; --bg2:#101827; --card:#151F30; --card-hi:#1A2639;
  --neon:#A3FF5F; --green:#65E89B; --text:#F4F7FC; --muted:#8D9AAF; --line:#263247;
  --neon-soft:rgba(163,255,95,.14); --neon-line:rgba(163,255,95,.45);
  --shadow:0 10px 30px rgba(0,0,0,.35);
  --font:'Be Vietnam Pro','Segoe UI',system-ui,-apple-system,Roboto,Arial,sans-serif;
}

/* ---------- Nền & khung chung ---------- */
.stApp{
  background:
    radial-gradient(900px 500px at 85% -10%, rgba(163,255,95,.09), transparent 60%),
    radial-gradient(800px 480px at -10% 30%, rgba(101,232,155,.06), transparent 60%),
    linear-gradient(180deg, var(--bg) 0%, #0a1120 100%);
  color:var(--text);
  font-family:var(--font);
}
.stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div{font-family:var(--font);}
header[data-testid="stHeader"]{background:transparent;}
[data-testid="stToolbar"], footer, #MainMenu{visibility:hidden;}
.block-container{max-width:1200px; padding:1.4rem 1.6rem 3rem;}
.stMarkdown, .stMarkdown p, .stMarkdown li, [data-testid="stWidgetLabel"] p, .stCaption, [data-testid="stCaptionContainer"]{color:var(--text);}
[data-testid="stCaptionContainer"], .stCaption{color:var(--muted);}
h1,h2,h3,h4{color:var(--text); letter-spacing:-.01em; font-family:var(--font);}
hr{border-color:var(--line);}
a{color:var(--neon);}
:focus-visible{outline:2px solid var(--neon); outline-offset:2px;}

/* ---------- Header ---------- */
div[data-testid="stHorizontalBlock"]:has(.brand-marker){
  align-items:center; padding:.35rem 0 1rem; margin-bottom:1.1rem;
  border-bottom:1px solid var(--line); gap:1rem;
}
.brand{display:flex; align-items:center; gap:.8rem;}
.brand-logo{
  width:46px; height:46px; border-radius:14px; display:grid; place-items:center; flex:none;
  background:linear-gradient(145deg,#1b2a14,#0f1a12); border:1px solid var(--neon-line);
  box-shadow:0 0 22px rgba(163,255,95,.22);
}
.brand-logo svg{width:28px; height:28px;}
.brand-name{font-weight:800; font-size:1.2rem; letter-spacing:.14em; line-height:1.1; color:var(--text);}
.brand-sub{font-size:.66rem; letter-spacing:.2em; color:var(--muted); margin-top:.25rem; font-weight:500;}

/* Thanh điều hướng (st.radio ngang) */
div[data-testid="stRadio"] > div[role="radiogroup"]{
  display:flex; flex-wrap:wrap; gap:.35rem; justify-content:flex-end;
  background:var(--bg2); border:1px solid var(--line); border-radius:999px; padding:.3rem; width:fit-content; margin-left:auto;
}
div[data-testid="stRadio"] label{
  margin:0; padding:.5rem 1rem; border-radius:999px; cursor:pointer;
  border:1px solid transparent; transition:background .2s ease, color .2s ease, border-color .2s ease;
}
div[data-testid="stRadio"] label > div:first-child{display:none;}
div[data-testid="stRadio"] label p{color:var(--muted); font-weight:600; font-size:.9rem; margin:0;}
div[data-testid="stRadio"] label:hover p{color:var(--text);}
div[data-testid="stRadio"] label:has(input:checked){background:var(--neon); border-color:var(--neon);}
div[data-testid="stRadio"] label:has(input:checked) p{color:#0a1208;}
div[data-testid="stRadio"] label:has(input:focus-visible){outline:2px solid var(--neon); outline-offset:2px;}

/* ---------- Hero ---------- */
div[data-testid="stHorizontalBlock"]:has(.hero-marker){
  position:relative; overflow:hidden; align-items:center; gap:1.5rem;
  padding:2.4rem 2.6rem; border-radius:28px; border:1px solid var(--line);
  background:
    radial-gradient(520px 340px at 88% 40%, rgba(163,255,95,.16), transparent 65%),
    radial-gradient(420px 300px at 0% 100%, rgba(101,232,155,.08), transparent 65%),
    linear-gradient(135deg,#111b2e 0%, #0b1424 100%);
  box-shadow:var(--shadow), inset 0 1px 0 rgba(255,255,255,.04);
}
.hero-chip{
  display:inline-flex; align-items:center; gap:.5rem; padding:.35rem .8rem; border-radius:999px;
  border:1px solid var(--neon-line); background:var(--neon-soft); color:var(--neon);
  font-size:.74rem; font-weight:600; letter-spacing:.06em; margin-bottom:1.1rem;
}
.hero-chip i{width:7px; height:7px; border-radius:50%; background:var(--neon); display:inline-block;}
.hero-title{
  font-weight:800; font-size:clamp(2.1rem, 5vw, 3.6rem); line-height:1.02; letter-spacing:-.025em;
  margin:0 0 1.1rem; color:var(--text);
}
.hero-title span{display:block; color:var(--neon);}
.hero-text{color:#c3ccdb; font-size:1.02rem; line-height:1.7; max-width:34rem; margin:0 0 .6rem;}
.hero-text strong{color:var(--text);}
.hero-art{width:100%; max-width:430px; margin:0 auto; display:block;}
.hero-art svg{width:100%; height:auto; display:block;}

/* ---------- Nút ---------- */
.stButton > button, .stDownloadButton > button{
  border-radius:12px; font-weight:700; font-family:var(--font); padding:.6rem 1.15rem;
  background:var(--card); color:var(--text); border:1px solid var(--line);
  transition:background .2s ease, color .2s ease, border-color .2s ease, box-shadow .2s ease, transform .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover{
  border-color:var(--neon-line); color:var(--neon); background:var(--card-hi); box-shadow:0 0 18px rgba(163,255,95,.14);
}
.stButton > button:active, .stDownloadButton > button:active{transform:translateY(1px);}
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"]{
  background:var(--neon); color:#0a1208; border-color:var(--neon); box-shadow:0 8px 24px rgba(163,255,95,.25);
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover{
  background:var(--green); border-color:var(--green); color:#07120b; box-shadow:0 10px 28px rgba(101,232,155,.32);
}
.stButton > button p, .stDownloadButton > button p{color:inherit;}

/* ---------- Tiêu đề khu vực ---------- */
.sec-head{margin:2.4rem 0 1rem;}
.sec-head h2{font-size:1.35rem; font-weight:700; margin:0 0 .25rem;}
.sec-head p{color:var(--muted); margin:0; font-size:.93rem;}
.src-badge{
  display:inline-flex; align-items:center; gap:.45rem; margin-top:.7rem; padding:.3rem .75rem;
  border-radius:999px; border:1px solid var(--line); background:var(--bg2); color:var(--muted); font-size:.78rem;
}
.src-badge i{width:7px; height:7px; border-radius:50%; background:var(--green); display:inline-block;}
.src-badge.wait i{background:var(--muted);}

/* ---------- KPI ---------- */
.kpi-grid{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem;}
.kpi{
  background:linear-gradient(160deg,var(--card) 0%, #121b2b 100%); border:1px solid var(--line);
  border-radius:20px; padding:1.2rem 1.25rem; box-shadow:var(--shadow);
  transition:transform .25s ease, border-color .25s ease, box-shadow .25s ease;
  animation:fadeUp .55s ease both;
}
.kpi:nth-child(2){animation-delay:.06s;} .kpi:nth-child(3){animation-delay:.12s;} .kpi:nth-child(4){animation-delay:.18s;}
.kpi:hover{transform:translateY(-4px); border-color:var(--neon-line); box-shadow:0 14px 36px rgba(0,0,0,.45), 0 0 26px rgba(163,255,95,.12);}
.kpi-top{display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;}
.kpi-label{color:var(--muted); font-size:.86rem; font-weight:500; line-height:1.35;}
.ico{width:40px; height:40px; border-radius:12px; display:grid; place-items:center; flex:none;
     background:var(--neon-soft); color:var(--neon); border:1px solid rgba(163,255,95,.25);}
.ico svg{width:20px; height:20px;}
.ico.g{background:rgba(101,232,155,.12); color:var(--green); border-color:rgba(101,232,155,.28);}
.ico.s{background:rgba(244,247,252,.07); color:var(--text); border-color:var(--line);}
.kpi-value{font-size:2.4rem; font-weight:800; line-height:1; letter-spacing:-.02em; color:var(--text);}
.kpi-sub{color:var(--muted); font-size:.8rem; margin-top:.55rem;}

/* ---------- Quick access ---------- */
.qa{
  background:var(--card); border:1px solid var(--line); border-radius:20px; padding:1.3rem; box-shadow:var(--shadow);
  transition:transform .25s ease, border-color .25s ease, box-shadow .25s ease, background .25s ease; min-height:176px;
}
.qa:hover{transform:translateY(-4px); border-color:var(--neon-line); background:var(--card-hi);
          box-shadow:0 14px 36px rgba(0,0,0,.45), 0 0 26px rgba(163,255,95,.12);}
.qa .ico{margin-bottom:1rem;}
.qa h3{font-size:1.05rem; font-weight:700; margin:0 0 .4rem;}
.qa p{color:var(--muted); font-size:.9rem; line-height:1.55; margin:0;}

/* ---------- Insight ---------- */
.insight-grid{display:grid; grid-template-columns:1fr 1fr 1.25fr; gap:1rem;}
.ins{background:var(--card); border:1px solid var(--line); border-radius:20px; padding:1.3rem; box-shadow:var(--shadow);
     transition:border-color .25s ease, box-shadow .25s ease;}
.ins:hover{border-color:var(--neon-line); box-shadow:0 14px 36px rgba(0,0,0,.45), 0 0 26px rgba(163,255,95,.10);}
.ins h4{font-size:.92rem; font-weight:600; color:var(--muted); margin:0 0 1rem; line-height:1.4;}
.ins .big{font-size:2.2rem; font-weight:800; letter-spacing:-.02em; line-height:1;}
.ins .sub{color:var(--muted); font-size:.82rem; margin-top:.7rem;}
.ring{--p:0; width:112px; height:112px; border-radius:50%; display:grid; place-items:center; position:relative;
      background:conic-gradient(var(--neon) calc(var(--p) * 1%), #223048 0);}
.ring::before{content:""; position:absolute; inset:11px; border-radius:50%; background:var(--card);}
.ring span{position:relative; font-weight:800; font-size:1.5rem;}
.ring-row{display:flex; align-items:center; gap:1.1rem;}
.bar{height:10px; border-radius:999px; background:#223048; overflow:hidden; margin-top:1rem;}
.bar > i{display:block; height:100%; border-radius:999px; background:linear-gradient(90deg,var(--green),var(--neon));
         width:calc(var(--p) * 1%); transition:width .6s ease;}
.ins.msg{background:linear-gradient(150deg,#16240f 0%, var(--card) 70%); border-color:rgba(163,255,95,.28);}
.ins.msg .quote{font-size:1.25rem; font-weight:700; line-height:1.4; color:var(--text);}
.note{color:var(--muted); font-size:.82rem; margin-top:1rem; line-height:1.6;}

/* ---------- Trạng thái chờ ---------- */
.wait-card{background:var(--card); border:1px dashed var(--neon-line); border-radius:20px; padding:1.2rem 1.4rem; color:var(--muted);
           margin-top:1rem; line-height:1.6;}
.wait-card strong{color:var(--text);}

/* ---------- Thành phần Streamlit ở các trang con ---------- */
[data-testid="stMetric"]{background:var(--card); border:1px solid var(--line); border-radius:16px; padding:1rem 1.1rem; box-shadow:var(--shadow);}
[data-testid="stMetricLabel"] p{color:var(--muted);}
[data-testid="stMetricValue"]{color:var(--neon); font-weight:800;}
[data-testid="stExpander"]{border:1px solid var(--line); border-radius:16px; background:var(--bg2);}
[data-testid="stAlert"]{border-radius:14px;}
[data-testid="stFileUploader"] section{background:var(--bg2); border:1px dashed var(--line); border-radius:14px;}
[data-testid="stDataFrame"]{border:1px solid var(--line); border-radius:14px; overflow:hidden;}
div[data-baseweb="input"], div[data-baseweb="select"] > div{border-radius:10px;}

/* ---------- Hiệu ứng xuất hiện (chạy một lần) ---------- */
@keyframes fadeUp{from{opacity:0; transform:translateY(10px);} to{opacity:1; transform:none;}}
@keyframes fadeIn{from{opacity:0;} to{opacity:1;}}
div[data-testid="stHorizontalBlock"]:has(.hero-marker){animation:fadeIn .6s ease both;}
.ins, .qa{animation:fadeUp .55s ease both;}

/* ---------- Responsive ---------- */
@media (max-width:1000px){
  .kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));}
  .insight-grid{grid-template-columns:1fr 1fr;}
  .ins.msg{grid-column:1 / -1;}
}
@media (max-width:640px){
  .block-container{padding:1rem .9rem 2.5rem;}
  div[data-testid="stHorizontalBlock"]:has(.hero-marker){padding:1.4rem 1.2rem; border-radius:22px;}
  .kpi-grid, .insight-grid{grid-template-columns:1fr;}
  .kpi-value{font-size:2rem;}
  div[data-testid="stRadio"] > div[role="radiogroup"]{border-radius:18px; width:100%; justify-content:flex-start;}
  div[data-testid="stRadio"] label{padding:.45rem .8rem;}
}

/* ---------- Tôn trọng prefers-reduced-motion ---------- */
@media (prefers-reduced-motion:reduce){
  *, *::before, *::after{animation:none !important; transition:none !important; scroll-behavior:auto !important;}
}
</style>
"""


def _clean(markup: str) -> str:
    """Bỏ thụt đầu dòng để Markdown không biến HTML thành khối mã."""
    return "\n".join(line.strip() for line in markup.strip().splitlines() if line.strip())


def render_html(markup: str) -> None:
    st.markdown(_clean(markup), unsafe_allow_html=True)


def icon(paths: str) -> str:
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + paths + "</svg>"
    )


ICON_USERS = icon(
    '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
    '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
)
ICON_DOWN = icon('<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/>')
ICON_TARGET = icon('<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>')
ICON_CLOCK = icon('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>')
ICON_CHECK = icon(
    '<rect x="8" y="2" width="8" height="4" rx="1"/>'
    '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>'
)
ICON_CHART = icon('<line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/>')
ICON_SHIELD = icon('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>')

LOGO = (
    '<svg viewBox="0 0 32 32" fill="none" stroke="#A3FF5F" stroke-width="2.6" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true"><polyline points="2 17 8 17 11 8 16 26 20 12 23 17 30 17"/></svg>'
)

HERO_ART = """
<svg viewBox="0 0 420 400" role="img" aria-label="Minh họa vòng vận động và người đang chạy">
  <defs>
    <radialGradient id="glow" cx="50%" cy="45%" r="55%">
      <stop offset="0%" stop-color="#A3FF5F" stop-opacity=".22"/>
      <stop offset="100%" stop-color="#A3FF5F" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="ng" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#A3FF5F"/><stop offset="100%" stop-color="#65E89B"/>
    </linearGradient>
  </defs>
  <circle cx="210" cy="180" r="190" fill="url(#glow)"/>
  <g fill="none" stroke-linecap="round" transform="rotate(-90 210 180)">
    <circle cx="210" cy="180" r="150" stroke="#1d2a40" stroke-width="16"/>
    <circle cx="210" cy="180" r="150" stroke="url(#ng)" stroke-width="16" stroke-dasharray="720 943"/>
    <circle cx="210" cy="180" r="120" stroke="#1d2a40" stroke-width="16"/>
    <circle cx="210" cy="180" r="120" stroke="#65E89B" stroke-width="16" stroke-dasharray="500 754"/>
    <circle cx="210" cy="180" r="90" stroke="#1d2a40" stroke-width="16"/>
    <circle cx="210" cy="180" r="90" stroke="#A3FF5F" stroke-opacity=".75" stroke-width="16" stroke-dasharray="360 566"/>
  </g>
  <g fill="none" stroke="#F4F7FC" stroke-width="8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M208 152 L194 198"/>
    <path d="M205 164 L228 180 L246 166"/>
    <path d="M205 164 L184 178 L168 164"/>
    <path d="M194 198 L220 218 L214 248"/>
    <path d="M194 198 L176 224 L148 226"/>
  </g>
  <circle cx="214" cy="136" r="12" fill="#A3FF5F"/>
  <polyline points="30,372 120,372 140,350 160,392 188,340 208,372 392,372" fill="none" stroke="#A3FF5F"
            stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <g>
    <rect x="288" y="18" width="124" height="48" rx="14" fill="#151F30" stroke="#263247"/>
    <text x="304" y="40" fill="#A3FF5F" font-size="15" font-weight="700">60 phút/ngày</text>
    <text x="304" y="57" fill="#8D9AAF" font-size="11">mốc vận động tham khảo</text>
    <rect x="8" y="236" width="136" height="48" rx="14" fill="#151F30" stroke="#263247"/>
    <text x="24" y="258" fill="#F4F7FC" font-size="14" font-weight="700">Ngồi &gt; 60 phút</text>
    <text x="24" y="275" fill="#8D9AAF" font-size="11">nhắc đứng dậy, đi lại</text>
  </g>
</svg>
"""


# ---------------------------------------------------------------------------
# DỮ LIỆU: giữ nguyên cách đọc/xử lý của bản gốc
# ---------------------------------------------------------------------------
@st.cache_data
def load_sample():
    return pd.read_csv("data/du_lieu_mo_phong_30_HS.csv")


def read_uploaded(file):
    name = file.name.lower()
    try:
        file.seek(0)
    except Exception:
        pass
    if name.endswith(".csv"):
        return pd.read_csv(file)
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file, sheet_name="Du_lieu_khao_sat", skiprows=2)
    raise ValueError("Chỉ hỗ trợ tệp CSV hoặc Excel (.xlsx, .xls).")


def load_active_data():
    """Đọc dữ liệu đang được chọn (tệp tải lên hoặc dữ liệu mô phỏng) đúng một lần cho mỗi lượt chạy.

    Trang chủ và trang Phân tích dùng chung kết quả này nên số liệu luôn thống nhất.
    """
    # Widget không còn được vẽ khi người dùng đổi trang -> lưu bản sao để không mất tệp đã nạp.
    current = st.session_state.get("survey_file")
    if current is not None:
        st.session_state["_saved_file"] = current
    if "use_sample" in st.session_state:
        st.session_state["_saved_use_sample"] = st.session_state["use_sample"]

    uploaded = st.session_state.get("_saved_file")
    use_sample = st.session_state.get("_saved_use_sample", True)

    result = {"source": "none", "name": "", "raw": None, "data": None,
              "issues": [], "summary": None, "error": None}
    try:
        if uploaded is not None:
            result["source"] = "upload"
            result["name"] = uploaded.name
            raw = read_uploaded(uploaded)
        elif use_sample:
            result["source"] = "sample"
            raw = load_sample()
        else:
            raw = pd.DataFrame(columns=REQUIRED_COLUMNS)
        result["raw"] = raw
        if len(raw) > 0:
            data = prepare_dataframe(raw)
            result["data"] = data
            result["issues"] = validate_dataframe(data)
            result["summary"] = summarize_dataframe(data)
    except Exception as e:  # giữ hành vi báo lỗi như bản gốc
        result["error"] = e
    return result


def show_table(df):
    try:
        st.dataframe(df, width="stretch", hide_index=True)
    except Exception:
        st.dataframe(df, use_container_width=True, hide_index=True)


def go_to(page):
    st.session_state["nav"] = page


def clear_saved_file():
    st.session_state["_saved_file"] = None


# ---------------------------------------------------------------------------
# TRANG CHỦ
# ---------------------------------------------------------------------------
def kpi_card(ico, tone, label, value, sub):
    return (
        '<div class="kpi"><div class="kpi-top"><div class="kpi-label">' + label + "</div>"
        '<div class="ico ' + tone + '">' + ico + "</div></div>"
        '<div class="kpi-value">' + value + '</div><div class="kpi-sub">' + sub + "</div></div>"
    )


def render_home(ds):
    # ----- Hero -----
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        render_html("""
        <span class="hero-marker"></span>
        <div class="hero-chip"><i></i>Sản phẩm STEM Tin học 9</div>
        <h1 class="hero-title">MOVE MORE.<span>LIVE BETTER.</span></h1>
        <p class="hero-text">ACTIVE LIFE giúp học sinh phân tích dữ liệu khảo sát ẩn danh về
        <strong>vận động thể chất</strong> và <strong>thói quen ngồi</strong>.
        Bớt ngồi lâu – tăng vận động – sống khỏe mỗi ngày.</p>
        """)
        b1, b2 = st.columns(2)
        b1.button("Bắt đầu tự kiểm tra", type="primary", key="cta_check", on_click=go_to, args=(PAGE_CHECK,))
        b2.button("Xem phân tích khảo sát", key="cta_analysis", on_click=go_to, args=(PAGE_ANALYSIS,))
    with right:
        render_html('<div class="hero-art">' + HERO_ART + "</div>")

    # ----- Dashboard tổng quan -----
    ok = ds["summary"] is not None
    if ok:
        s = ds["summary"]
        total = s["total"]

        def pct(n):
            return f"{n / total * 100:.0f}% tổng số bản ghi" if total else "—"

        values = [str(total), str(s["activity_below_60"]), str(s["activity_at_least_60"]), str(s["sitting_over_60"])]
        subs = ["Số bản ghi trong dữ liệu", pct(s["activity_below_60"]), pct(s["activity_at_least_60"]), pct(s["sitting_over_60"])]
        if ds["source"] == "sample":
            badge = '<span class="src-badge"><i></i>Dữ liệu mô phỏng 30 học sinh – không phải kết quả khảo sát thực tế</span>'
        else:
            badge = '<span class="src-badge"><i></i>Dữ liệu từ tệp: ' + _html.escape(ds["name"]) + "</span>"
    else:
        values = ["—", "—", "—", "—"]
        subs = ["Đang chờ dữ liệu"] * 4
        badge = '<span class="src-badge wait"><i></i>Chưa có dữ liệu</span>'

    render_html(
        '<div class="sec-head"><h2>Tổng quan khảo sát</h2>'
        "<p>Các chỉ số được tính trực tiếp từ dữ liệu khảo sát đang nạp trong ứng dụng.</p>" + badge + "</div>"
    )
    render_html(
        '<div class="kpi-grid">'
        + kpi_card(ICON_USERS, "s", "Số học sinh trong dữ liệu", values[0], subs[0])
        + kpi_card(ICON_DOWN, "g", "Vận động dưới 60 phút/ngày", values[1], subs[1])
        + kpi_card(ICON_TARGET, "", "Vận động từ 60 phút/ngày", values[2], subs[2])
        + kpi_card(ICON_CLOCK, "s", "Ngồi liên tục trên 60 phút", values[3], subs[3])
        + "</div>"
    )

    if not ok:
        if ds["error"] is not None:
            reason = "Không đọc được dữ liệu: " + _html.escape(str(ds["error"]))
        else:
            reason = "Chưa có dữ liệu khảo sát nào được chọn."
        render_html(
            '<div class="wait-card"><strong>Đang chờ dữ liệu.</strong> ' + reason +
            " Vào mục <strong>Phân tích khảo sát</strong> để tải tệp Excel/CSV hoặc bật dữ liệu mô phỏng.</div>"
        )
    elif ds["issues"]:
        render_html(
            '<div class="wait-card"><strong>Lưu ý:</strong> dữ liệu có điểm cần kiểm tra. '
            "Xem chi tiết tại mục <strong>Phân tích khảo sát</strong> trước khi sử dụng kết quả.</div>"
        )

    # ----- Quick access -----
    render_html(
        '<div class="sec-head"><h2>Truy cập nhanh</h2><p>Chọn một mục để bắt đầu.</p></div>'
    )
    cards = [
        (PAGE_CHECK, ICON_CHECK, "", "Tự kiểm tra thói quen",
         "Nhập thời gian vận động và thời gian ngồi để nhận thông điệp gợi ý phù hợp.", "Mở tự kiểm tra"),
        (PAGE_ANALYSIS, ICON_CHART, "g", "Phân tích khảo sát",
         "Nạp tệp Excel/CSV, kiểm tra dữ liệu, xem thống kê, biểu đồ và xuất kết quả.", "Mở phân tích"),
        (PAGE_KNOWLEDGE, ICON_SHIELD, "s", "Kiến thức & an toàn",
         "Mốc tham khảo, quy ước của dự án và các nguyên tắc bảo vệ thông tin cá nhân.", "Đọc nguyên tắc"),
    ]
    cols = st.columns(3, gap="medium")
    for i, (page, ico, tone, title, desc, label) in enumerate(cards):
        with cols[i]:
            render_html(
                '<div class="qa"><div class="ico ' + tone + '">' + ico + "</div><h3>" + title + "</h3><p>" + desc + "</p></div>"
            )
            st.button(label, key="qa_" + str(i), on_click=go_to, args=(page,), use_container_width=True)

    # ----- Insight -----
    if ok:
        s = ds["summary"]
        total = s["total"]
        p_active = s["activity_at_least_60"] / total * 100
        p_sit = s["sitting_over_60"] / total * 100
        render_html(
            '<div class="sec-head"><h2>Điểm nổi bật</h2>'
            "<p>Tính từ dữ liệu đang nạp, trên tổng số bản ghi.</p></div>"
        )
        render_html(
            '<div class="insight-grid">'
            '<div class="ins"><h4>Học sinh đạt mốc tham khảo 60 phút vận động/ngày</h4>'
            '<div class="ring-row"><div class="ring" style="--p:' + f"{p_active:.1f}" + '"><span>' + f"{p_active:.0f}%" + "</span></div>"
            '<div class="sub">' + str(s["activity_at_least_60"]) + " / " + str(total) + " học sinh</div></div></div>"
            '<div class="ins"><h4>Học sinh ngồi liên tục trên 60 phút</h4>'
            '<div class="big">' + f"{p_sit:.0f}%" + "</div>"
            '<div class="bar"><i style="--p:' + f"{p_sit:.1f}" + '"></i></div>'
            '<div class="sub">' + str(s["sitting_over_60"]) + " / " + str(total) + " học sinh</div></div>"
            '<div class="ins msg"><h4>Thông điệp khuyến khích</h4>'
            '<div class="quote">Bớt ngồi lâu – tăng vận động – sống khỏe mỗi ngày.</div>'
            '<div class="sub">Trung bình ' + f"{s['average_activity']:.0f}" + " phút vận động/ngày (tự khai báo).</div></div>"
            "</div>"
        )
        render_html(
            '<div class="note">Mốc 60 phút vận động/ngày là mốc tham khảo giáo dục cho lứa tuổi học sinh. '
            "Mốc ngồi liên tục trên 60 phút là quy ước của dự án nhằm nhắc nghỉ giải lao. "
            "Cả hai không phải ngưỡng y tế và không dùng để chẩn đoán sức khỏe cá nhân.</div>"
        )

    with st.expander("Mục tiêu và cách sử dụng", expanded=False):
        st.markdown("""
        1. Tải tệp Excel/CSV khảo sát hoặc dùng dữ liệu mẫu.
        2. Kiểm tra dữ liệu, xem thống kê và biểu đồ.
        3. Đọc thông điệp gợi ý để thảo luận về thói quen vận động và ngồi lâu.

        **Lưu ý:** Mốc 60 phút vận động/ngày là mốc tham khảo giáo dục cho lứa tuổi học sinh, không dùng để chẩn đoán sức khỏe cá nhân. Mốc ngồi liên tục trên 60 phút là quy ước của dự án nhằm nhắc nhở nghỉ giải lao, không phải ngưỡng y tế.
        """)


# ---------------------------------------------------------------------------
# TRANG 2: TỰ KIỂM TRA THÓI QUEN (giữ nguyên chức năng)
# ---------------------------------------------------------------------------
def render_check():
    st.subheader("Tự xem lại thói quen của em")
    c1, c2 = st.columns(2)
    with c1:
        activity = st.number_input("Phút vận động vừa–mạnh trong một ngày", min_value=0, max_value=1440, value=45, step=5)
        days = st.slider("Số ngày có vận động trong tuần", 0, 7, 4)
    with c2:
        sitting = st.number_input("Thời gian ngồi liên tục lâu nhất (phút/lần)", min_value=0, max_value=1440, value=75, step=5)
        activity_type = st.selectbox("Hoạt động thường tham gia", ["Đi bộ", "Chạy bộ", "Đạp xe", "Bóng đá", "Cầu lông", "Bơi", "Thể dục/thể thao khác", "Ít vận động"])
    st.info(create_message(activity, sitting))
    st.caption(f"Hoạt động đã chọn: {activity_type} · Số ngày vận động: {days}/7 ngày. Đây là công cụ tự phản ánh, không phải đánh giá y tế.")


# ---------------------------------------------------------------------------
# TRANG 3: PHÂN TÍCH KHẢO SÁT (giữ nguyên chức năng)
# ---------------------------------------------------------------------------
def render_analysis(ds):
    st.subheader("Nạp dữ liệu khảo sát")
    uploaded_now = st.file_uploader("Chọn tệp Excel hoặc CSV", type=["xlsx", "xls", "csv"], key="survey_file")
    if uploaded_now is None and st.session_state.get("_saved_file") is not None:
        n1, n2 = st.columns([3, 1])
        n1.info("Đang dùng tệp đã nạp trước đó: " + st.session_state["_saved_file"].name + ". Chọn tệp mới để thay thế.")
        n2.button("Gỡ tệp đã nạp", key="clear_file", on_click=clear_saved_file, use_container_width=True)
    st.checkbox(
        "Dùng dữ liệu mô phỏng 30 học sinh để xem thử",
        value=st.session_state.get("_saved_use_sample", True),
        key="use_sample",
    )
    try:
        if ds["error"] is not None:
            raise ds["error"]
        raw = ds["raw"]
        if len(raw) == 0:
            st.warning("Chưa có dữ liệu. Hãy tải tệp khảo sát hoặc chọn dữ liệu mô phỏng.")
        else:
            data = ds["data"]
            issues = ds["issues"]
            if issues:
                st.warning("Cần kiểm tra dữ liệu trước khi sử dụng kết quả:")
                for issue in issues:
                    st.write("• " + issue)
            else:
                st.success(f"Dữ liệu hợp lệ về cấu trúc: {len(data)} bản ghi.")
            summary = ds["summary"]
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Số học sinh", summary["total"])
            k2.metric("Vận động dưới 60 phút", summary["activity_below_60"])
            k3.metric("Vận động từ 60 phút", summary["activity_at_least_60"])
            k4.metric("Ngồi liên tục trên 60 phút", summary["sitting_over_60"])

            st.markdown("**Bảng dữ liệu đã xử lý**")
            show_table(data)

            chart_data = pd.DataFrame({
                "Nhóm": ["Vận động dưới 60 phút", "Vận động từ 60 phút", "Ngồi liên tục trên 60 phút"],
                "Số học sinh": [summary["activity_below_60"], summary["activity_at_least_60"], summary["sitting_over_60"]]
            }).set_index("Nhóm")
            st.markdown("**Biểu đồ thống kê**")
            try:
                st.bar_chart(chart_data, color="#A3FF5F")
            except Exception:
                st.bar_chart(chart_data)

            st.markdown("**Liên hệ kiến thức Tin học 9**")
            st.write(f"- COUNTIF: đếm {summary['activity_below_60']} học sinh có thời gian vận động dưới 60 phút/ngày.")
            st.write(f"- COUNTIF: đếm {summary['sitting_over_60']} học sinh có thời gian ngồi liên tục trên 60 phút/lần.")
            st.write(f"- SUMIF: tổng số phút vận động của nhóm dưới 60 phút là {summary['sum_minutes_below_60']:.0f} phút.")
            st.write("- IF kết hợp OR: tạo thông điệp khi vận động dưới 60 phút hoặc ngồi liên tục trên 60 phút.")

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                data.to_excel(writer, index=False, sheet_name="Ket_qua_phan_tich")
            st.download_button("Tải bảng kết quả Excel", data=output.getvalue(),
                               file_name="Ket_qua_phan_tich_nhom_C.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        st.error(f"Không thể đọc hoặc xử lý tệp: {e}")
        st.info("Kiểm tra tên cột và cấu trúc tệp theo mẫu khảo sát đi kèm trong thư mục data.")


# ---------------------------------------------------------------------------
# TRANG 4: KIẾN THỨC & AN TOÀN (giữ nguyên nội dung)
# ---------------------------------------------------------------------------
def render_knowledge():
    st.subheader("Kiến thức và nguyên tắc an toàn")
    st.markdown("""
    **Thông điệp dự án:** *Bớt ngồi lâu – tăng vận động – sống khỏe mỗi ngày.*

    - WHO khuyến nghị trẻ em và thanh thiếu niên 5–17 tuổi nên có trung bình ít nhất 60 phút/ngày hoạt động thể chất mức vừa đến mạnh trong tuần.
    - Trong Mini App, ngưỡng ngồi liên tục trên 60 phút là quy ước truyền thông do nhóm dự án lựa chọn để khuyến khích nghỉ giải lao và vận động nhẹ.
    - Dữ liệu khảo sát do học sinh tự khai báo nên có thể có sai số; kết quả chỉ phản ánh tập thể khảo sát.
    - Không nhập họ tên, số điện thoại, địa chỉ hoặc thông tin nhận dạng cá nhân. Chỉ sử dụng mã học sinh đã ẩn danh.
    - Ứng dụng không chẩn đoán, không đưa ra chỉ định điều trị và không thay thế tư vấn của nhân viên y tế.
    - AI được dùng để hỗ trợ nhóm trong quá trình tìm ý tưởng, tạo và giải thích mã nguồn; ứng dụng không gọi API AI trả phí khi vận hành.
    """)


# ---------------------------------------------------------------------------
# KHUNG CHÍNH
# ---------------------------------------------------------------------------
st.markdown(_clean(CSS), unsafe_allow_html=True)
st.session_state.setdefault("nav", PAGE_HOME)

ds = load_active_data()

h_left, h_right = st.columns([1, 1.7], gap="medium")
with h_left:
    render_html(
        '<span class="brand-marker"></span><div class="brand"><div class="brand-logo">' + LOGO + "</div>"
        '<div><div class="brand-name">ACTIVE LIFE</div><div class="brand-sub">HEALTH &amp; MOVEMENT TRACKER</div></div></div>'
    )
with h_right:
    st.radio("Điều hướng", PAGES, key="nav", horizontal=True, label_visibility="collapsed")

page = st.session_state["nav"]
if page == PAGE_HOME:
    render_home(ds)
elif page == PAGE_CHECK:
    render_check()
elif page == PAGE_ANALYSIS:
    render_analysis(ds)
else:
    render_knowledge()

st.divider()
st.caption("Sản phẩm minh họa phục vụ học tập STEM – Tin học 9. Dữ liệu mẫu là dữ liệu mô phỏng, không phải kết quả khảo sát thực tế.")
