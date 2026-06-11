import streamlit as st
import json
import os
import hmac
import hashlib
import secrets
from datetime import date
import pandas as pd

st.set_page_config(
    page_title="The Hive",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Research groups → themes ─────────────────────────────────────────────────
# Each person's group (from the seating doc) gets its own look & critter.
GROUPS = {
    "H": {"name": "Holz",     "theme": "hive"},
    "L": {"name": "Lea",      "theme": "hive"},
    "T": {"name": "Thorsten", "theme": "forest"},
    "M": {"name": "Moe",      "theme": "sea"},
    "A": {"name": "Ali",      "theme": "cats"},
}

THEMES = {
    "hive": {
        "title": "The Hive",
        "tagline": "Find your cell · claim your buzz · do your work",
        "banner_icons": "🍯 🐝 🍯",
        "bg": "radial-gradient(ellipse at top left, #FFFDE7 0%, #FFE082 50%, #FFB300 100%)",
        "title_color": "#3E2000", "sub_color": "#7B4F00", "text_color": "#3E2000",
        "accent": "linear-gradient(135deg, #FFD600, #FFA000)",
        "accent_shadow": "rgba(255,160,0,0.40)", "accent_shadow2": "rgba(255,160,0,0.55)",
        "btn_text": "#3E2000",
        "card_border": "rgba(255,200,0,0.55)", "card_shadow": "rgba(180,110,0,0.18)",
        "input_bg": "rgba(255,255,255,0.85)", "placeholder": "#9C7A4A",
        "occupant_icon": "🐝", "free_icon": "⬡", "free_label": "Flex",
        "hex": {
            "free":     ("linear-gradient(160deg,#FFE859 0%,#FFBA00 100%)", "#5D3A00"),
            "mine":     ("linear-gradient(160deg,#AED581 0%,#558B2F 100%)", "#FFFFFF"),
            "taken":    ("linear-gradient(160deg,#FF7043 0%,#D84315 100%)", "#FFFFFF"),
            "fixed":    ("linear-gradient(160deg,#6D4C41 0%,#4E342E 100%)", "#FFCC80"),
            "released": ("linear-gradient(160deg,#80DEEA 0%,#00ACC1 100%)", "#00363D"),
        },
    },
    "forest": {
        "title": "The Forest",
        "tagline": "Find your clearing · claim your spot · roam the woods",
        "banner_icons": "🌲 🫎 🌲",
        "bg": "radial-gradient(ellipse at top left, #E8F5E9 0%, #A5D6A7 50%, #2E7D32 100%)",
        "title_color": "#1B3D1B", "sub_color": "#33691E", "text_color": "#1B3D1B",
        "accent": "linear-gradient(135deg, #66BB6A, #2E7D32)",
        "accent_shadow": "rgba(46,125,50,0.40)", "accent_shadow2": "rgba(46,125,50,0.55)",
        "btn_text": "#FFFFFF",
        "card_border": "rgba(46,125,50,0.45)", "card_shadow": "rgba(27,61,27,0.20)",
        "input_bg": "rgba(255,255,255,0.90)", "placeholder": "#6B8E6B",
        "occupant_icon": "🫎", "free_icon": "🌿", "free_label": "Spot",
        "shape": "polygon(50% 0%, 66% 22%, 57% 22%, 78% 48%, 66% 48%, 92% 80%, 58% 80%, 58% 100%, 42% 100%, 42% 80%, 8% 80%, 34% 48%, 22% 48%, 43% 22%, 34% 22%)",
        "w": 118, "h": 124, "pad": "40px 2px 6px",
        "hex": {
            "free":     ("linear-gradient(160deg,#C5E1A5 0%,#7CB342 100%)", "#1B3D1B"),
            "mine":     ("linear-gradient(160deg,#43A047 0%,#1B5E20 100%)", "#FFFFFF"),
            "taken":    ("linear-gradient(160deg,#A1887F 0%,#5D4037 100%)", "#FFFFFF"),
            "fixed":    ("linear-gradient(160deg,#4E342E 0%,#3E2723 100%)", "#D7CCC8"),
            "released": ("linear-gradient(160deg,#80DEEA 0%,#00ACC1 100%)", "#00363D"),
        },
    },
    "sea": {
        "title": "The Reef",
        "tagline": "Find your current · claim your spot · swim free",
        "banner_icons": "🌊 🐡 🌊",
        "bg": "radial-gradient(ellipse at top left, #E0F7FA 0%, #4DD0E1 50%, #00838F 100%)",
        "title_color": "#003B46", "sub_color": "#006978", "text_color": "#003B46",
        "accent": "linear-gradient(135deg, #26C6DA, #00838F)",
        "accent_shadow": "rgba(0,131,143,0.40)", "accent_shadow2": "rgba(0,131,143,0.55)",
        "btn_text": "#FFFFFF",
        "card_border": "rgba(0,131,143,0.45)", "card_shadow": "rgba(0,59,70,0.20)",
        "input_bg": "rgba(255,255,255,0.90)", "placeholder": "#5E97A0",
        "occupant_icon": "🐡", "free_icon": "🫧", "free_label": "Spot",
        "hex": {
            "free":     ("linear-gradient(160deg,#B3E5FC 0%,#4FC3F7 100%)", "#003B46"),
            "mine":     ("linear-gradient(160deg,#26A69A 0%,#00695C 100%)", "#FFFFFF"),
            "taken":    ("linear-gradient(160deg,#FF8A65 0%,#E64A19 100%)", "#FFFFFF"),
            "fixed":    ("linear-gradient(160deg,#37474F 0%,#263238 100%)", "#B0BEC5"),
            "released": ("linear-gradient(160deg,#CE93D8 0%,#8E24AA 100%)", "#FFFFFF"),
        },
    },
    "cats": {
        "title": "The Cattery",
        "tagline": "Find your cushion · claim your nap · purr away",
        "banner_icons": "🐾 🐈 🐾",
        "bg": "radial-gradient(ellipse at top left, #FFF3E0 0%, #F8BBD0 50%, #CE93D8 100%)",
        "title_color": "#4A2545", "sub_color": "#8E4585", "text_color": "#4A2545",
        "accent": "linear-gradient(135deg, #F48FB1, #AB47BC)",
        "accent_shadow": "rgba(171,71,188,0.40)", "accent_shadow2": "rgba(171,71,188,0.55)",
        "btn_text": "#FFFFFF",
        "card_border": "rgba(171,71,188,0.40)", "card_shadow": "rgba(74,37,69,0.18)",
        "input_bg": "rgba(255,255,255,0.90)", "placeholder": "#B07AA8",
        "occupant_icon": "🐈", "free_icon": "🐾", "free_label": "Cushion",
        "hex": {
            "free":     ("linear-gradient(160deg,#FCE4EC 0%,#F48FB1 100%)", "#4A2545"),
            "mine":     ("linear-gradient(160deg,#BA68C8 0%,#8E24AA 100%)", "#FFFFFF"),
            "taken":    ("linear-gradient(160deg,#F06292 0%,#C2185B 100%)", "#FFFFFF"),
            "fixed":    ("linear-gradient(160deg,#6D4C41 0%,#4E342E 100%)", "#D7CCC8"),
            "released": ("linear-gradient(160deg,#80DEEA 0%,#26A69A 100%)", "#00363D"),
        },
    },
    "neutral": {
        "title": "Desk Booking",
        "tagline": "Sign in to get started",
        "banner_icons": "🗓️ 🪑 📍",
        "bg": "radial-gradient(ellipse at top left, #F5F7FA 0%, #C3CFE2 55%, #8A97B5 100%)",
        "title_color": "#2A2F45", "sub_color": "#4A5170", "text_color": "#2A2F45",
        "accent": "linear-gradient(135deg, #7986CB, #3949AB)",
        "accent_shadow": "rgba(57,73,171,0.35)", "accent_shadow2": "rgba(57,73,171,0.50)",
        "btn_text": "#FFFFFF",
        "card_border": "rgba(120,130,160,0.40)", "card_shadow": "rgba(60,70,100,0.15)",
        "input_bg": "rgba(255,255,255,0.92)", "placeholder": "#8A93AD",
        "occupant_icon": "📌", "free_icon": "▢", "free_label": "Desk",
        "hex": {
            "free":     ("linear-gradient(160deg,#E8EAF6 0%,#9FA8DA 100%)", "#2A2F45"),
            "mine":     ("linear-gradient(160deg,#7986CB 0%,#3949AB 100%)", "#FFFFFF"),
            "taken":    ("linear-gradient(160deg,#B0BEC5 0%,#607D8B 100%)", "#FFFFFF"),
            "fixed":    ("linear-gradient(160deg,#546E7A 0%,#37474F 100%)", "#CFD8DC"),
            "released": ("linear-gradient(160deg,#80DEEA 0%,#00ACC1 100%)", "#00363D"),
        },
    },
}
DEFAULT_THEME = "neutral"

CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;900&display=swap');

html, body, [class*="css"], * { font-family: 'Nunito', 'Segoe UI', sans-serif; }

[data-testid="stAppViewContainer"] { background: @BG@; min-height: 100vh; }
[data-testid="stHeader"]         { background: transparent !important; }
[data-testid="stToolbar"]        { display: none; }
section[data-testid="stSidebar"] { display: none; }

/* ── Banner ── */
.hive-banner {
    text-align: center;
    padding: 30px 20px 22px;
    background: rgba(255,255,255,0.28);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 26px;
    margin-bottom: 22px;
    border: 2px solid @CARD_BORDER@;
    box-shadow: 0 8px 32px @CARD_SHADOW@;
}
.hive-banner .icons { font-size: 2.6rem; line-height: 1; margin-bottom: 6px; }
.hive-banner h1     { margin: 0; font-size: 2.5rem; font-weight: 900; color: @TITLE_COLOR@; letter-spacing: -0.5px; }
.hive-banner p      { margin: 6px 0 0; color: @SUB_COLOR@; font-size: 0.98rem; }

.room-title { text-align:center; font-size:1.2rem; font-weight:900; color:@TITLE_COLOR@; margin-bottom:2px; }
.room-sub   { text-align:center; font-size:0.7rem; color:@SUB_COLOR@; font-weight:700;
              letter-spacing:0.07em; text-transform:uppercase; margin-bottom:10px; }

/* Themed glass cards for rooms / forms */
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"] {
    background: rgba(255,255,255,0.30) !important;
    border: 2px solid @CARD_BORDER@ !important;
    border-radius: 22px !important;
    box-shadow: 0 6px 24px @CARD_SHADOW@ !important;
}

/* ── Pill buttons (login, logout, group, claim) ── */
div[data-testid="stButton"] > button {
    border-radius: 30px !important;
    font-weight: 800 !important;
    font-size: 0.82rem !important;
    padding: 6px 14px !important;
    border: none !important;
    background: @ACCENT@ !important;
    color: @BTN_TEXT@ !important;
    box-shadow: 0 3px 10px @ACCENT_SHADOW@ !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px @ACCENT_SHADOW2@ !important;
}

/* ── Summary table ── */
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }

/* ── Text contrast ── */
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
label, .stMarkdown p, .stMarkdown li, .stMarkdown strong,
[data-testid="stCaptionContainer"] { color: @TEXT_COLOR@ !important; }
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6 { color: @TITLE_COLOR@ !important; }
[data-testid="stRadio"] label, [data-testid="stRadio"] label * { color: @TEXT_COLOR@ !important; }
button[data-baseweb="tab"] p { color: @SUB_COLOR@ !important; font-weight: 800 !important; }
button[data-baseweb="tab"][aria-selected="true"] p { color: @TITLE_COLOR@ !important; }
input, textarea { color: @TEXT_COLOR@ !important; background: @INPUT_BG@ !important; }
input::placeholder, textarea::placeholder { color: @PLACEHOLDER@ !important; }
</style>
"""

def build_css(t):
    css = CSS_TEMPLATE
    for token, key in {
        "@BG@": "bg", "@CARD_BORDER@": "card_border", "@CARD_SHADOW@": "card_shadow",
        "@TITLE_COLOR@": "title_color", "@SUB_COLOR@": "sub_color", "@TEXT_COLOR@": "text_color",
        "@ACCENT@": "accent", "@ACCENT_SHADOW@": "accent_shadow", "@ACCENT_SHADOW2@": "accent_shadow2",
        "@BTN_TEXT@": "btn_text", "@INPUT_BG@": "input_bg", "@PLACEHOLDER@": "placeholder",
    }.items():
        css = css.replace(token, t[key])
    return css

def banner_html(t):
    return (
        '<div class="hive-banner">'
        f'<div class="icons">{t["banner_icons"]}</div>'
        f'<h1>{t["title"]}</h1>'
        f'<p>{t["tagline"]}</p>'
        '</div>'
    )

BOOKINGS_FILE = os.path.join(os.path.dirname(__file__), "bookings.json")

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE) as f:
            return json.load(f)
    return {}

def save_bookings(data):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Accounts ─────────────────────────────────────────────────────────────────
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Allowlist: only these emails may register / log in (admin-managed) ────────
ALLOWED_FILE = os.path.join(os.path.dirname(__file__), "allowed_users.json")
# First admin — seeded on first run so the app is never locked out.
SEED_ADMIN_EMAIL = "samiraabedini150@gmail.com"
SEED_ADMIN = {SEED_ADMIN_EMAIL: {"group": "L", "is_admin": True, "display_name": "Samira"}}

def load_allowed():
    if os.path.exists(ALLOWED_FILE):
        with open(ALLOWED_FILE) as f:
            data = json.load(f)
    else:
        data = {}
    if SEED_ADMIN_EMAIL not in {e.lower() for e in data}:
        data.update(SEED_ADMIN)
        save_allowed(data)
    return data

def save_allowed(data):
    with open(ALLOWED_FILE, "w") as f:
        json.dump(data, f, indent=2)

def allowed_entry(allowed, email):
    """Case-insensitive lookup of an allowlist entry by email."""
    email = (email or "").strip().lower()
    for e, info in allowed.items():
        if e.lower() == email:
            return info
    return None

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000)
    return salt, dk.hex()

def verify_password(password, salt, expected_hash):
    _, candidate = hash_password(password, salt)
    return hmac.compare_digest(candidate, expected_hash)

# ── Released fixed desks ─────────────────────────────────────────────────────
RELEASES_FILE = os.path.join(os.path.dirname(__file__), "releases.json")

def load_releases():
    if os.path.exists(RELEASES_FILE):
        with open(RELEASES_FILE) as f:
            return json.load(f)
    return {}

def save_releases(data):
    with open(RELEASES_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Time: bookings are stored per whole hour ("08", "09", … "19") ─────────────
DAY_START, DAY_END = 8, 20          # building hours: 08:00 → 20:00

def hour_range(start, end):
    """List of hour keys covering [start, end), e.g. 9→12 = ['09','10','11']."""
    return [f"{h:02d}" for h in range(start, end)]

# ── Desk + room model, transcribed from the 2nd-floor seating doc ─────────────
def _fixed(key, owner, group="", note=""):
    return {"key": key, "kind": "fixed", "owner": owner, "group": group, "note": note}

def _flex(key):
    return {"key": key, "kind": "flex", "owner": "", "group": "", "note": ""}

ROOMS = {
    "2.16": [
        [_fixed("d1", "Srishti", "L"),                          _flex("d2")],
        [_fixed("d3", "Donatella", "T", "07/26–12/26"),         _fixed("d4", "Mete", "L", "05/26–07/26")],
    ],
    "2.17 🏠": [
        [_fixed("d1", "Keno", "H"),                             _fixed("d2", "Addison", "H")],
        [_fixed("d3", "Jasper", "M"),                           _fixed("d4", "Florian", "H")],
        [_flex("d5"),                                           _fixed("d6", "Zhuohao / Ismael", "M", "Zhuohao 06–08 · Ismael 09–12")],
    ],
    "2.20": [
        [_fixed("d1", "Huzaifa", "T"),                          _fixed("d2", "Paweł", "T")],
        [_fixed("d3", "Devansh", "L"),                          _flex("d4")],
    ],
    "2.21 🐟": [
        [_fixed("d1", "David P.", "L"),                         _fixed("d2", "Sina", "L")],
        [_flex("d3"),                                           _fixed("d4", "Samira", "L")],
        [_fixed("d5", "Francesco", "L", "05/26–10/26"),         _flex("d6")],
    ],
    "2.01": [
        [_fixed("d1", "Pouya", "A"),                            _fixed("d2", "Pietro", "A")],
        [_fixed("d3", "Ulysse", "A"),                           _flex("d4")],
    ],
    "2.03": [
        [_fixed("d1", "Meng", "A"),                             _fixed("d2", "Pansilu", "A")],
        [_fixed("d3", "Matteo / Majid", "H/A"),                 _flex("d4")],
    ],
    "2.04": [
        [_fixed("d1", "Daniele", "A"),                          _fixed("d2", "Julian", "A")],
        [_fixed("d3", "Martin", "A"),                           _flex("d4")],
    ],
}

def layout_desks(layout):
    return [d for row in layout for d in row]

# Flat lookup: room -> desk_key -> desk
DESK_INDEX = {room: {d["key"]: d for d in layout_desks(layout)} for room, layout in ROOMS.items()}

# ── State helpers (nested: store[date][period][room][desk_key] = name) ─────────
def _set(store, date_key, periods, room, key, value):
    for p in periods:
        store.setdefault(date_key, {}).setdefault(p, {}).setdefault(room, {})[key] = value

def _clear(store, date_key, periods, room, key):
    for p in periods:
        room_d = store.get(date_key, {}).get(p, {}).get(room, {})
        room_d.pop(key, None)

def desk_booked_by(bookings, date_key, periods, room, key):
    for p in periods:
        n = bookings.get(date_key, {}).get(p, {}).get(room, {}).get(key)
        if n:
            return n
    return None

def desk_released(releases, date_key, periods, room, key):
    return all(releases.get(date_key, {}).get(p, {}).get(room, {}).get(key) for p in periods)

def same_person(a, b):
    return bool(a) and bool(b) and a.strip().lower() == b.strip().lower()

def owns(display, desk):
    """A logged-in user owns a fixed desk when their first name matches an owner's."""
    if desk["kind"] != "fixed" or not display.strip():
        return False
    me = display.strip().lower().split()[0]
    for part in desk["owner"].replace(",", "/").split("/"):
        part = part.strip()
        if part and part.split()[0].lower() == me:
            return True
    return False

def _short(name, n=8):
    return name[:n] + ("…" if len(name) > n else "")

def desk_view(desk, booked_by, released, your_name, theme):
    """Return (state, button_label, action). action=None ⇒ not clickable."""
    mine = same_person(booked_by, your_name)
    own  = owns(your_name, desk)
    occ  = theme["occupant_icon"]

    if desk["kind"] == "fixed" and not released:
        owner = _short(desk["owner"])
        return ("fixed", f"🔒\n{owner}", "release" if own else None)

    if booked_by:
        if mine:
            return ("mine", f"{occ}\n{_short(booked_by)}", "leave")
        return ("taken", f"{occ}\n{_short(booked_by)}", None)

    if desk["kind"] == "fixed" and released:
        if own:
            return ("released", "🔓\nReclaim", "reclaim")
        return ("released", "🔓\nFree!", "claim")

    return ("free", f'{theme["free_icon"]}\n{theme["free_label"]}', "claim")

HEX_SHAPE = "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)"

def hex_button_css(class_name, state, theme):
    bg, fg = theme["hex"][state]
    shape  = theme.get("shape", HEX_SHAPE)
    w      = theme.get("w", 86)
    h      = theme.get("h", 96)
    pad    = theme.get("pad", "2px")          # extra top padding seats text in wide base
    # doubled class raises specificity so it beats the global pill-button rule
    sel = f".{class_name}.{class_name} button"
    return f"""
{sel} {{
    width: {w}px !important; height: {h}px !important; min-height: {h}px !important;
    padding: {pad} !important; margin: 0 auto !important;
    border: none !important; border-radius: 0 !important;
    clip-path: {shape};
    background: {bg} !important; color: {fg} !important;
    font-size: 0.62rem !important; font-weight: 800 !important;
    line-height: 1.25 !important; white-space: pre-line !important;
    box-shadow: inset 0 -6px 0 rgba(0,0,0,0.14) !important;
    transition: transform 0.15s ease !important;
}}
{sel} p {{ white-space: pre-line !important; font-size: 0.95rem !important; }}
{sel}:hover {{ transform: scale(1.06) !important; }}
{sel}:disabled {{ opacity: 1 !important; cursor: default !important; }}
{sel}:disabled:hover {{ transform: none !important; }}"""


# ════════════════════════════════════════════════════════════════════════════
def current_theme():
    # Admins can preview any theme via the account bar (view_theme override).
    vt = st.session_state.get("view_theme")
    if vt in THEMES:
        return THEMES[vt]
    g = st.session_state.get("group")
    return THEMES[GROUPS[g]["theme"] if g in GROUPS else DEFAULT_THEME]

THEME = current_theme()
st.markdown(build_css(THEME), unsafe_allow_html=True)
st.markdown(banner_html(THEME), unsafe_allow_html=True)

def group_card(letter, info):
    """Visual preview of a group's theme — used on the welcome page."""
    t = THEMES[info["theme"]]
    st.markdown(
        "<div style='text-align:center'>"
        f"<div style='font-size:2.1rem;line-height:1'>{t['banner_icons']}</div>"
        f"<div style='font-weight:900;font-size:1.0rem;color:{t['title_color']}'>Group {info['name']}</div>"
        f"<div style='font-size:0.7rem;color:{t['sub_color']}'>{t['title']}</div>"
        "</div>",
        unsafe_allow_html=True)

# ── Welcome page: neutral, combines log in / sign up (access by allowlist) ────
def render_auth():
    users   = load_users()
    allowed = load_allowed()

    st.markdown("##### ")
    cols = st.columns(len(GROUPS))
    for col, (letter, info) in zip(cols, GROUPS.items()):
        with col:
            with st.container(border=True):
                group_card(letter, info)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        login_tab, signup_tab = st.tabs(["Log in", "Create account"])

        with login_tab:
            with st.form("login_form"):
                u = st.text_input("Username").strip()
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Log in", use_container_width=True):
                    rec = users.get(u.lower())
                    if not (rec and verify_password(p, rec["salt"], rec["hash"])):
                        st.error("Wrong username or password.")
                    elif allowed_entry(allowed, rec.get("email")) is None:
                        st.error("Your access has been removed. Contact an admin.")
                    else:
                        st.session_state["user"] = rec["display"]
                        st.session_state["group"] = rec.get("group") or "L"
                        st.rerun()

        with signup_tab:
            st.caption("Only people an admin has added can register. Ask to be added if you can't.")
            with st.form("signup_form"):
                u  = st.text_input("Choose a username").strip()
                e  = st.text_input("Email (must be the one your admin added)").strip()
                p1 = st.text_input("Password", type="password")
                p2 = st.text_input("Confirm password", type="password")
                if st.form_submit_button("Create account", use_container_width=True):
                    entry  = allowed_entry(allowed, e)
                    emails = {r.get("email", "").lower() for r in users.values()}
                    if not u or not e or not p1:
                        st.error("Username, email and password are all required.")
                    elif "@" not in e or "." not in e.split("@")[-1]:
                        st.error("Please enter a valid email.")
                    elif entry is None:
                        st.error("This email isn't on the allowed list. Contact an admin.")
                    elif u.lower() in users:
                        st.error("That username is taken — pick another.")
                    elif e.lower() in emails:
                        st.error("That email already has an account.")
                    elif p1 != p2:
                        st.error("Passwords don't match.")
                    elif len(p1) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        salt, h = hash_password(p1)
                        users[u.lower()] = {"display": u, "email": e.strip(),
                                            "group": entry.get("group", "L"),
                                            "salt": salt, "hash": h}
                        save_users(users)
                        st.session_state["user"]  = u
                        st.session_state["group"] = entry.get("group", "L")
                        st.rerun()

if "user" not in st.session_state:
    render_auth()
    st.stop()

your_name = st.session_state["user"]
# Live admin status + current email, looked up from the allowlist each run.
_users_now = load_users()
my_email   = (_users_now.get(your_name.lower(), {}) or {}).get("email", "")
my_entry   = allowed_entry(load_allowed(), my_email)
is_admin   = bool(my_entry and my_entry.get("is_admin"))

# Group/theme is set by the admin (in the allowlist) — never chosen by the user.
group_letter = (my_entry or {}).get("group") or st.session_state.get("group") or "L"
if group_letter not in GROUPS:
    group_letter = "L"
st.session_state["group"] = group_letter
group_info = GROUPS[group_letter]

# ── Admin panel ───────────────────────────────────────────────────────────────
def render_admin_panel():
    st.markdown("## 🛠️ Admin panel")
    allowed = load_allowed()
    users   = load_users()
    tab_access, tab_bookings = st.tabs(["👥 Access", "📅 All bookings"])

    with tab_access:
        st.markdown("#### Allowed people")
        # email -> the username chosen at signup (if they've registered)
        username_by_email = {r.get("email", "").lower(): r.get("display", "")
                             for r in users.values()}
        st.dataframe(pd.DataFrame([
            {"Email": e,
             "Username": username_by_email.get(e.lower(), "—"),
             "Group": GROUPS.get(i.get("group", ""), {}).get("name", i.get("group", "?")),
             "Admin": "✅" if i.get("is_admin") else "",
             "Registered": "✅" if e.lower() in username_by_email else "—"}
            for e, i in allowed.items()
        ]), use_container_width=True, hide_index=True)

        st.markdown("#### Add or update a person")
        with st.form("add_allowed", clear_on_submit=True):
            ne = st.text_input("Email").strip()
            cgrp, cadm = st.columns([2, 1])
            with cgrp:
                ng = st.selectbox("Group", list(GROUPS.keys()),
                                  format_func=lambda L: f"Group {GROUPS[L]['name']}")
            with cadm:
                nadmin = st.checkbox("Admin")
            if st.form_submit_button("Add / update", use_container_width=True):
                if "@" not in ne or "." not in ne.split("@")[-1]:
                    st.error("Enter a valid email.")
                else:
                    allowed[ne] = {"group": ng, "is_admin": nadmin}
                    save_allowed(allowed)
                    st.success(f"{ne} can now register as Group {GROUPS[ng]['name']}.")
                    st.rerun()

        st.markdown("#### Remove access")
        removable = [e for e in allowed if e.lower() != my_email.lower()]
        if removable:
            with st.form("remove_allowed"):
                target = st.selectbox("Person", removable)
                also_acct = st.checkbox("Also delete their account & log them out", value=True)
                if st.form_submit_button("Remove access", use_container_width=True):
                    allowed.pop(target, None)
                    save_allowed(allowed)
                    if also_acct:
                        u2 = load_users()
                        for un, r in list(u2.items()):
                            if r.get("email", "").lower() == target.lower():
                                u2.pop(un, None)
                        save_users(u2)
                    st.success(f"Removed access for {target}.")
                    st.rerun()
        else:
            st.caption("No one else to remove. (You can't remove yourself.)")

    with tab_bookings:
        bk = load_bookings()
        rows, options = [], {}
        for d, hours in sorted(bk.items()):
            for hr, rooms in sorted(hours.items()):
                for room, desks in rooms.items():
                    for dk, person in desks.items():
                        dd = DESK_INDEX.get(room, {}).get(dk, {})
                        desk_lbl = f"{dd.get('owner')}'s desk" if dd.get("kind") == "fixed" else "Flex"
                        rows.append({"Date": d, "Time": f"{hr}:00", "Room": room,
                                     "Desk": desk_lbl, "Person": person})
                        options[f"{d}  {hr}:00 · {room} · {desk_lbl} · {person}"] = (d, hr, room, dk)
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            with st.form("cancel_bookings"):
                picks = st.multiselect("Cancel bookings", list(options.keys()))
                if st.form_submit_button("Cancel selected", use_container_width=True) and picks:
                    for p in picks:
                        d, hr, room, dk = options[p]
                        try:
                            del bk[d][hr][room][dk]
                        except KeyError:
                            pass
                    save_bookings(bk)
                    st.success(f"Cancelled {len(picks)} booking(s).")
                    st.rerun()
        else:
            st.caption("No bookings yet.")

# ── Account bar (always visible) ──────────────────────────────────────────────
if is_admin:
    ac1, ac2, ac3 = st.columns([3, 1.4, 1])
else:
    ac1, ac3 = st.columns([4, 1])
with ac1:
    badge = " · 🛠️ admin" if is_admin else ""
    st.markdown(
        f"<div style='padding-top:4px;font-weight:800;color:{THEME['title_color']}'>"
        f"{THEME['occupant_icon']} <b>{your_name}</b> "
        f"<span style='font-size:0.78rem;color:{THEME['sub_color']}'>· Group {group_info['name']}{badge}</span></div>",
        unsafe_allow_html=True)
if is_admin:
    with ac2:
        theme_keys = ["hive", "forest", "sea", "cats", "neutral"]
        own_theme  = group_info["theme"]
        labels     = {"hive": "🍯 Hive", "forest": "🌲 Forest", "sea": "🌊 Reef",
                      "cats": "🐾 Cattery", "neutral": "🗓️ Neutral"}
        cur = st.session_state.get("view_theme") or own_theme
        idx = theme_keys.index(cur) if cur in theme_keys else theme_keys.index(own_theme)
        picked = st.selectbox("👁 View theme", theme_keys, index=idx,
                              format_func=lambda k: labels[k], label_visibility="collapsed")
        # Selecting your own group's theme clears the override.
        new_override = None if picked == own_theme else picked
        if new_override != st.session_state.get("view_theme"):
            st.session_state["view_theme"] = new_override
            st.rerun()
with ac3:
    if st.button("🚪  Log out", use_container_width=True):
        st.session_state.pop("user", None)
        st.session_state.pop("group", None)
        st.session_state.pop("view_theme", None)
        st.rerun()

view = "📋 Booking"
if is_admin:
    view = st.radio("view", ["📋 Booking", "🛠️ Admin panel"],
                    horizontal=True, label_visibility="collapsed")

if view == "🛠️ Admin panel":
    render_admin_panel()
    st.stop()

# ── Booking view ──────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1.6, 1, 1])
with c1:
    selected_date = st.date_input("📅 Date", value=date.today(), min_value=date.today())
with c2:
    from_hour = st.selectbox("⏰ From", list(range(DAY_START, DAY_END)),
                             index=1, format_func=lambda h: f"{h:02d}:00")
with c3:
    to_options = [h for h in range(DAY_START + 1, DAY_END + 1) if h > from_hour]
    to_hour = st.selectbox("⏰ To", to_options,
                           index=min(8, len(to_options) - 1),
                           format_func=lambda h: f"{h:02d}:00")

date_key = str(selected_date)
periods  = hour_range(from_hour, to_hour)
bookings = load_bookings()
releases = load_releases()

def my_booking_in_periods(bk, date_key, periods, name):
    """If the user already holds a desk during any of these hours, return (room, key)."""
    for p in periods:
        for room, desks in bk.get(date_key, {}).get(p, {}).items():
            for dk, person in desks.items():
                if same_person(person, name):
                    return room, dk
    return None

def do_action(act, room, key, desk):
    booked_by = desk_booked_by(bookings, date_key, periods, room, key)
    if act == "claim" and not booked_by:
        clash = my_booking_in_periods(bookings, date_key, periods, your_name)
        if clash and clash != (room, key):
            cr, ck = clash
            cd = DESK_INDEX.get(cr, {}).get(ck, {})
            cd_lbl = f"{cd.get('owner')}'s desk" if cd.get("kind") == "fixed" else "a flex desk"
            st.session_state["flash"] = (
                f"You already have {cd_lbl} in {cr} booked for that time. ")
        else:
            _set(bookings, date_key, periods, room, key, your_name)
            save_bookings(bookings)
    elif act == "leave" and same_person(booked_by, your_name):
        _clear(bookings, date_key, periods, room, key)
        save_bookings(bookings)
    elif act == "release" and owns(your_name, desk):
        _set(releases, date_key, periods, room, key, your_name)
        save_releases(releases)
    elif act == "reclaim" and owns(your_name, desk) and not booked_by:
        _clear(releases, date_key, periods, room, key)
        save_releases(releases)
    st.rerun()

_flash = st.session_state.pop("flash", None)
if _flash:
    st.warning(_flash, icon="⚠️")

st.caption(f"👆 Click a hexagon to claim it · one desk per person · 🔒 fixed desks can be released by their owner · {THEME['occupant_icon']} green is yours")

# Per-desk hexagon styling is injected as one stylesheet, then the buttons render.
hex_css = []
room_items = list(ROOMS.items())
for r_idx, (room_name, layout) in enumerate(room_items):
    for desk in layout_desks(layout):
        key       = desk["key"]
        booked_by = desk_booked_by(bookings, date_key, periods, room_name, key)
        released  = desk["kind"] == "fixed" and desk_released(releases, date_key, periods, room_name, key)
        state, _, _ = desk_view(desk, booked_by, released, your_name, THEME)
        hex_css.append(hex_button_css(f"st-key-hx_{r_idx}_{key}", state, THEME))

st.markdown("<style>" + "\n".join(hex_css) + "</style>", unsafe_allow_html=True)

for start in range(0, len(room_items), 3):
    cols = st.columns(3)
    for col, (room_name, layout) in zip(cols, room_items[start:start + 3]):
        r_idx = room_items.index((room_name, layout))
        n_fixed = sum(1 for d in layout_desks(layout) if d["kind"] == "fixed")
        n_flex  = sum(1 for d in layout_desks(layout) if d["kind"] == "flex")
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<div class='room-title'>{room_name}</div>"
                    f"<div class='room-sub'>{n_flex} flex · {n_fixed} fixed</div>",
                    unsafe_allow_html=True)
                for i, row in enumerate(layout):
                    # offset odd rows to get the honeycomb interlock
                    if i % 2 == 1:
                        spec, cells_at = [0.5, 1, 1, 0.5], (1, 2)
                    else:
                        spec, cells_at = [1, 1, 1], (0, 1)
                    rcols = st.columns(spec)
                    for desk, ci in zip(row, cells_at):
                        key       = desk["key"]
                        booked_by = desk_booked_by(bookings, date_key, periods, room_name, key)
                        released  = desk["kind"] == "fixed" and desk_released(releases, date_key, periods, room_name, key)
                        _, label, action = desk_view(desk, booked_by, released, your_name, THEME)
                        with rcols[ci]:
                            clicked = st.button(label, key=f"hx_{r_idx}_{key}",
                                                disabled=action is None,
                                                help=desk["owner"] or None)
                        if clicked:
                            do_action(action, room_name, key, desk)

# ── Colony summary ───────────────────────────────────────────────────────────
def desk_label(room, key):
    d = DESK_INDEX.get(room, {}).get(key, {})
    return f"{d['owner']}'s desk" if d.get("kind") == "fixed" else "Flex desk"

seen = set()
rows = []
for period in periods:
    for room, desks in bookings.get(date_key, {}).get(period, {}).items():
        for key, person in desks.items():
            tag = (room, key, person)
            if tag in seen:
                continue
            seen.add(tag)
            rows.append({"Room": room, "Desk": desk_label(room, key), "Bee": person})

if rows:
    st.markdown("---")
    st.markdown(f"### 🍯 Colony — {from_hour:02d}:00–{to_hour:02d}:00 on {date_key}")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
