# -*- coding: utf-8 -*-
"""
DASHBOARD REGIONAL SOLO RAYA — SELL IN & SELL OUT
Dibangun dengan Streamlit + Plotly.

CARA UPDATE DATA HARIAN:
Cukup timpa (replace) file "SELL_IN.xlsx" dan "SELLOUT.xlsx" di folder yang sama
dengan file app.py ini menggunakan file baru bernama PERSIS SAMA.
Dashboard akan otomatis membaca ulang data (auto-refresh via cache-busting
berdasarkan waktu modifikasi file) tanpa perlu mengubah satu baris kode pun.
"""

import os
import re
import difflib
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ======================================================================================
# 0. KONFIGURASI HALAMAN & KONSTANTA
# ======================================================================================
st.set_page_config(
    page_title="Dashboard Regional Solo Raya — Sell In & Sell Out",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SELL_IN_FILE = os.path.join(BASE_DIR, "SELL_IN.xlsx")
SELLOUT_FILE = os.path.join(BASE_DIR, "SELLOUT.xlsx")

BULAN_FULL = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
              7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}
BULAN_SINGKAT = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
                 7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"}
QUARTER_BULAN = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}
QUARTER_LABEL = {1: "Q1 (Jan–Mar)", 2: "Q2 (Apr–Jun)", 3: "Q3 (Jul–Sep)", 4: "Q4 (Okt–Des)"}

SALES_LIST = ["Liza", "Fanny", "Yoga"]

# --- Palet warna "Gen Z" (vibrant / neon-pastel) ---
PALETTE = ["#7C3AED", "#EC4899", "#06B6D4", "#F59E0B", "#22C55E", "#F43F5E", "#8B5CF6", "#14B8A6"]
BRAND_COLORS = {
    "Y.O.U": "#7C3AED",
    "DAZZLE ME": "#EC4899",
    "GLAMFIX": "#06B6D4",
    "lavojoy": "#F59E0B",
    "barenbliss": "#22C55E",
    "HUED": "#F43F5E",
}
SALES_COLORS = {"Liza": "#EC4899", "Fanny": "#06B6D4", "Yoga": "#7C3AED"}
CAT_COLORS = {"Skincare": "#22C55E", "Make Up": "#EC4899", "Personal Care": "#06B6D4",
              "Tools": "#F59E0B", "Lainnya": "#94A3B8"}
HERO_COLORS = {"Hero Product": "#F43F5E", "Basic Product": "#94A3B8"}

# ======================================================================================
# 1. DAFTAR PRODUK HERO (selain daftar ini otomatis dianggap Basic Product)
# ======================================================================================
HERO_PRODUCTS_RAW = [
    "Y.O.U ACNEPLUS SPOT CARE PRO SERUM 15G",
    "Y.O.U HY! AMINO AC-TTACK ANTI-ACNE FACIAL WASH",
    "Y.O.U HY! AMINO AC-TTACK ANTI-ACNE FACIAL WASH 50g",
    "Y.O.U HY! AMINO GLO-WIN BRIGHTENING FACIAL WASH",
    "Y.O.U HY! AMINO GLO-WIN BRIGHTENING FACIAL WASH 50G",
    "Y.O.U HY! AMINO GLOWING GENTLE CLEANSING FACIAL WASH 100G",
    "Y.O.U HY! AMINO GLOWING GENTLE CLEANSING FACIAL WASH 50G",
    "Y.O.U HY! AMINO+ 1.5% BHA FIGHT ACNE GEL CLEANSER 100G",
    "Y.O.U HY! AMINO+ 2% NIACINAMIDE BRIGHTENING GENTLE CLEANSER 100G",
    "Y.O.U HY! AMINO+ 20% CENTELLA BARRIER LOW PH GEL CLEANSER 100G",
    "Y.O.U RADIANCE UP! SPOTLESS BRIGHTENING SERUM 20ML",
    "Y.O.U SUNBRELLA TONE UP UV ELIXIR SUNSCREEN 40ml",
    "Y.O.U SUNBRELLA Triple UV Elixir Sunscreen 30ml",
    "Y.O.U SUNBRELLA ACNE SHIELD LIGHT SUNSCREEN 30ML",
    "Y.O.U SUNBRELLA 2% NIACINAMIDE BRIGHTENING SUNSCREEN 30ML",
    "Y.O.U CLOUD TOUCH 3% NIACINAMIDE ACNE DEFENSE SKIN TINT",
    "Y.O.U CLOUD TOUCH 3% NIACINAMIDE BRIGHTENING SKIN TINT",
    "Y.O.U CLOUD TOUCH GLASTING GLOW SERUM CUSHION",
    "BARENBLISS BLACK ECLIPSE EYELINER 0.5G",
    "BARENBLISS ROLL TO CLEAN MASCARA REMOVER 8G",
    "BARENBLISS ROLL TO DEFINER STEEL MASCARA 6G",
    "BARENBLISS ROLL TO HIGH MASCARA 8G",
    "BARENBLISS ROLL TO LENGTH STEEL MASCARA 6G",
    "BARENBLISS ROLL TO VOLUME MASCARA",
    "BARENBLISS BLOOMATTE PERFECT ZOOM COVER CUSHION",
    "BARENBLISS AURA MOOD TRANSFERPROOF MATTE LIP CREAM",
    "BARENBLISS AURA MOOD TRANSFERPROOF VINYL LIP CREAM",
    "BARENBLISS PEACH MAKES PERFECT LIP TINT",
    "BARENBLISS LILY MAKES LUMINOUS GLOW TINT",
    "LAVOJOY HOLD ME TIGHT PRO CONDITIONER SPRING WONDER 280ML",
    "LAVOJOY HOLD ME TIGHT PRO SCALP ESSENCE SPRING WONDER 60ml",
    "Lavojoy Hold Me Tight Pro Shampoo Spring Wonder 280ml",
    "LAVOJOY LET IT GLOW DAILY SHINE BODY SERUM 180ML",
    "LAVOJOY LET IT GLOW DAILY SHINE BODY SERUM 03 GOLDEN HONEY 180ML",
    "LAVOJOY LET IT GLOW DAILY SHINE BODY SERUM DELICATE ROSE 01 CREAM BEIGE 180ML",
    "LAVOJOY LET IT GLOW DAILY SHINE BODY SERUM DELICATE ROSE 02 WARM SAND 180ML",
    "LAVOJOY LET IT GLOW DAILY SHINE BODY SERUM DELICATE ROSE 00 SILK WHITE 180ML",
    "LAVOJOY SOLVE IT NOW BODY SERUM 180ML",
    "LAVOJOY KEEP IT CHILL BODY SERUM 180ML",
    "LAVOJOY LET IT GLOW BODY SERUM 180ML",
    "LAVOJOY LET IT GLOW BODY SERUM BLACK OPIUM 180ML",
    "LAVOJOY LET IT GLOW BODY SERUM ORANGE BLOSSOM 180ML",
    "LAVOJOY LET IT GLOW BODY SERUM SUMMERTRAIN 180ML",
    "LAVOJOY LET IT GLOW 10% NIACINAMIDE DAYLIGHT BRIGHTENING SERUM GEL SERENE BLUSH 180ML",
    "LAVOJOY LET IT GLOW 10% NIACINAMIDE SUNSCREEN SERUM GEL SPF 50+ PA++++ PEAR FROST & FREESIA 170ML",
    "LAVOJOY LET IT GLOW BODY SCRUB DELICATE ROSE 180G",
    "GLAMFIX Eyelash Curler",
    "GLAMFIX GLAM MY LASH CURLER - BOUNDLESS CURL 1PC/BOX",
    "GLAMFIX GLAM MY LASH CURLER - COMB-IN 1PC/BOX",
    "GLAMFIX GLAM MY LASH CURLER - MAXI CURL - BARBIE COLLECTION 1PC/BOX",
    "GLAMFIX Maxi Curl Lash Curler",
    "GLAMFIX WINK ERA ALLURING BLINK MAGNETIC EYELASHES",
    "GLAMFIX WINK ERA ALLURING BLINK MAGNETIC EYELASHES 0",
    "GLAMFIX WINK ERA POPPIN' GLUE-FREE CLUSTER EYELASHES",
    "GLAMFIX WINK ERA PRESS-ON FALSE EYELASHES",
    "GLAMFIX Flawless Aircushion Puff",
    "GLAMFIX PROFESSIONAL AIRCUSHION PUFF 2PCS/BAG",
    "GLAMFIX Excellent Brush Set",
    "GLAMFIX Excellent Brush Set Lake Blue",
    "DAZZLE ME Lock & Wing! Hyper Stay Eyeliner",
    "DAZZLE ME Lock & Pop! Hyper CURL-ing Mascara",
    "DAZZLE ME Lock & Pop! Hyper BOLD-ing Mascara",
    "DAZZLE ME Lock & Wing! Hyper Slim Eyeliner",
    "DAZZLE ME LOCK & POP! VOLUMAX-ING MASCARA 7G",
    "DAZZLE ME LOCK & POP! LONGLASH-TING MASCARA 7G",
    "DAZZLE ME GET A GRIP! MAKEUP SETTING SPRAY ACNE SOOTHING 60ML",
    "DAZZLE ME GET A GRIP! MAKEUP SETTING SPRAY DEWY FIX 60ML",
    "DAZZLE ME GET A GRIP! MAKEUP SETTING SPRAY HYDRO FIX 60ML",
    "DAZZLE ME GET A GRIP! MAKEUP SETTING SPRAY MATTE FIX 60ML",
    "DAZZLE ME GET A GRIP! MAKEUP SETTING SPRAY PRIME+SET ANTI-POLLUTION 100ML",
    "DAZZLE ME GET A GRIP! MAKEUP SETTING SPRAY PRIME+SET ANTI-POLLUTION 50ML",
    "DAZZLE ME BETTER THAN FILTER HD INVISIBLE POWDER 5G",
    "DAZZLE ME COVER ME MATTE SERUM CUSHION",
    "DAZZLE ME INK-GLOSS LIP TINT",
    "DAZZLE ME INK-MATTE LIP CREAM",
    "DAZZLE ME INK-VINYL LIP LACQUER",
]

# ======================================================================================
# 2. MAPPING GRUP TOKO (Sell In & Sell Out tahunan)
# ======================================================================================
STORE_GROUPS = {
    "NELA RIOKE, S.E.": ["NELA RIOKE"],
    "Sinar Group": [
        "TITIN RIBKAH", "CV. SINAR PUTRA JAYA", "JOKO SIHMAWANTO", "AZKA CHILMA SAYYIDA",
        "LAILY NIDAUL HURRIYYAH", "ATIKA KHOIRUNNISA", "DIVA ALIFAH RIZKY", "MUHAMAD ARIF WIBAWANTO",
    ],
    "Laris Group": ["CV. LARIS ADINATA SEJATI", "CV LARIS ADI SEJATI"],
    "CV. RAJAWALI NIAGA SEJATI": ["CV. RAJAWALI NIAGA SEJATI"],
}

# ======================================================================================
# 3. FUNGSI-FUNGSI BANTUAN (helper)
# ======================================================================================

def norm(s):
    """Normalisasi teks: uppercase, hilangkan karakter non alfanumerik."""
    if pd.isna(s):
        return ""
    s = str(s).upper()
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def strip_size(s):
    """Hilangkan token ukuran (15G, 30ML, dst) di akhir nama produk agar mudah dicocokkan."""
    return re.sub(r"\s*\d+(\.\d+)?\s?(G|GR|GRAM|ML|KG|L|PC|PCS|BOX)\s*$", "", s).strip()


HERO_SET = set(strip_size(norm(p)) for p in HERO_PRODUCTS_RAW)


def is_hero(product_name):
    key = strip_size(norm(product_name))
    if key in HERO_SET:
        return "Hero Product"
    # fallback: cek exact match tanpa strip size juga
    if norm(product_name) in HERO_SET:
        return "Hero Product"
    return "Basic Product"


def extract_sales(bp):
    """Ekstrak nama Sales (Liza/Fanny/Yoga) dari kolom Business Personnel."""
    if pd.isna(bp):
        return "Lainnya"
    u = str(bp).upper()
    if "LIZA" in u:
        return "Liza"
    if "FANNY" in u:
        return "Fanny"
    if "YOGA" in u:
        return "Yoga"
    return "Lainnya"


_group_cache = {}


def match_group(customer_name):
    """Mapping nama customer/toko ke grup (Sinar Group, Laris Group, dst) — toleran typo ringan."""
    if pd.isna(customer_name):
        return customer_name
    if customer_name in _group_cache:
        return _group_cache[customer_name]
    cu = norm(customer_name)
    result = customer_name
    for group, members in STORE_GROUPS.items():
        for m in members:
            nm = norm(m)
            if nm == cu or nm in cu or cu in nm:
                result = group
                _group_cache[customer_name] = result
                return result
            ratio = difflib.SequenceMatcher(None, nm, cu).ratio()
            if ratio >= 0.88:
                result = group
                _group_cache[customer_name] = result
                return result
    _group_cache[customer_name] = result
    return result


CATEGORY_MAP = {
    "SKIN CARE": "Skincare",
    "MAKEUP": "Make Up",
    "PERSONAL CARE": "Personal Care",
    "TOOLS": "Tools",
    "EYE": "Make Up",
    "CLEAN MAKEUP": "Make Up",
    "LIP": "Make Up",
    "FACE": "Make Up",
    "EYEBROW": "Make Up",
}


def map_category(x):
    if pd.isna(x):
        return "Lainnya"
    return CATEGORY_MAP.get(str(x).upper().strip(), "Lainnya")


def format_rp(value):
    """Format penuh: Rp1.000.000"""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "Rp0"
    sign = "-" if v < 0 else ""
    v = abs(v)
    return f"{sign}Rp{v:,.0f}".replace(",", ".")


def format_short(value):
    """Format singkat ala Indonesia: Rb (ribu), Jt (juta), M (miliar), T (triliun)."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "Rp0"
    sign = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1e12:
        num, suf = v / 1e12, "T"
    elif v >= 1e9:
        num, suf = v / 1e9, "M"
    elif v >= 1e6:
        num, suf = v / 1e6, "Jt"
    elif v >= 1e3:
        num, suf = v / 1e3, "Rb"
    else:
        return f"{sign}Rp{v:,.0f}".replace(",", ".")
    s = f"{num:,.1f}".replace(".", ",")
    return f"{sign}Rp{s} {suf}"


def growth_pct(curr, prev):
    if prev is None or prev == 0 or pd.isna(prev):
        return None
    return (curr - prev) / prev * 100.0


def growth_label(g):
    if g is None:
        return "Baru"
    sign = "+" if g >= 0 else ""
    return f"{sign}{g:,.1f}%".replace(".", ",")


# ======================================================================================
# 4. MEMUAT & MEMBERSIHKAN DATA (dengan cache berbasis waktu modifikasi file)
# ======================================================================================

@st.cache_data(show_spinner="🔄 Memuat data Sell In...")
def load_sell_in(_mtime):
    df = pd.read_parquet("SELL_IN.parquet")
    st.write("Daftar kolom di SELL_IN:", df.columns.tolist())
    df = df.rename(columns={
        "order time": "Tanggal", 
        "Nama Merek": "Brand", 
        "Amount(Rp)": "Amount",
        "Customer": "Customer", 
        "Store Name": "Store", 
        "Business Personnel": "BP",
        "product name": "Product", 
        "Quantity": "Qty",
    })
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    df = df.dropna(subset=["Tanggal"]).copy()
    df["Year"] = df["Tanggal"].dt.year
    df["Month"] = df["Tanggal"].dt.month
    df["Quarter"] = df["Tanggal"].dt.quarter
    df["Sales"] = df["BP"].apply(extract_sales)
    df["Brand"] = df["Brand"].fillna("Lainnya")
    df["Kategori Produk"] = df["Product"].apply(is_hero)
    df["Customer Group"] = df["Customer"].apply(match_group)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    return df


@st.cache_data(show_spinner="🔄 Memuat data Sell Out...")
def load_sellout(_mtime):
    df = pd.read_parquet("SELLOUT.parquet")
    df = df.rename(columns={
        "Date": "Tanggal", "Nama Merek": "Brand", "Sales Amount": "Amount",
        "Customer Name": "Customer", "Store Name": "Store", "Business Personnel": "BP",
        "Nama Bahan": "Product", "Nama Seri": "CategoryRaw", "Sales": "Qty",
    })
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    df = df.dropna(subset=["Tanggal"]).copy()
    df["Year"] = df["Tanggal"].dt.year
    df["Month"] = df["Tanggal"].dt.month
    df["Quarter"] = df["Tanggal"].dt.quarter
    df["Sales"] = df["BP"].apply(extract_sales)
    df["Brand"] = df["Brand"].fillna("Lainnya")
    df["Kategori Produk"] = df["Product"].apply(is_hero)
    df["Kategori"] = df["CategoryRaw"].apply(map_category)
    df["Customer Group"] = df["Customer"].apply(match_group)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    return df


# ---- Cek keberadaan file kembali ke asal ----
if not os.path.exists("SELL_IN.parquet") or not os.path.exists("SELLOUT.parquet"):
    st.error("⚠️ File data .parquet tidak ditemukan. Pastikan SELL_IN.parquet dan SELLOUT.parquet ada.")
    st.stop()

# Memanggil fungsi dengan variabel file yang sudah didefinisikan di atas
# Memanggil fungsi pemuatan data
df_in_raw = load_sell_in(os.path.getmtime("SELL_IN.parquet"))
df_out_raw = load_sell_out(os.path.getmtime("SELLOUT.parquet"))

# ======================================================================================
# 5. CSS TEMA "GEN Z" (dark mode vibrant)
# ======================================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.main { background: radial-gradient(circle at top left, #1a1033 0%, #0d0d1a 55%); }
.block-container { padding-top: 1.5rem; }
h1, h2, h3 { color: #F8FAFC !important; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(236,72,153,0.10));
    border: 1px solid rgba(236,72,153,0.35);
    border-radius: 18px;
    padding: 14px 18px;
}
[data-testid="stMetricLabel"] { color: #E9D5FF !important; font-weight: 600; }
[data-testid="stMetricValue"] { color: #FFFFFF !important; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1033 0%, #0d0d1a 100%);
    border-right: 1px solid rgba(236,72,153,0.25);
}
.hero-title {
    font-size: 2.1rem; font-weight: 800;
    background: linear-gradient(90deg, #EC4899, #7C3AED, #06B6D4);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero-sub { color: #C4B5FD; font-size: 0.95rem; margin-top: -8px;}
.section-badge {
    display:inline-block; padding: 3px 14px; border-radius: 999px;
    background: linear-gradient(90deg,#7C3AED,#EC4899); color:white; font-weight:700; font-size:0.8rem;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

PLOT_TEMPLATE = "plotly_dark"


def style_fig(fig, height=430):
    fig.update_layout(
        template=PLOT_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#E5E7EB"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40, l=10, r=10),
        height=height,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.15)")
    return fig


# ======================================================================================
# 6. HEADER
# ======================================================================================
st.markdown('<div class="hero-title">✨ Dashboard Regional Solo Raya</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Sell In & Sell Out — real-time insight buat kamu yang gercep ambil keputusan 🚀</div>', unsafe_allow_html=True)
st.write("")

# ======================================================================================
# 7. SIDEBAR — FILTER GLOBAL
# ======================================================================================
st.sidebar.markdown("## 🎛️ Filter Global")

all_years = sorted(set(df_in_raw["Year"].unique()) | set(df_out_raw["Year"].unique()))
sel_year = st.sidebar.selectbox("📅 Tahun", all_years, index=len(all_years) - 1)

months_available = sorted(set(df_in_raw.loc[df_in_raw.Year == sel_year, "Month"].unique()) |
                           set(df_out_raw.loc[df_out_raw.Year == sel_year, "Month"].unique()))
if not months_available:
    months_available = [1]
sel_month = st.sidebar.selectbox(
    "🗓️ Bulan (bulan berjalan)", months_available,
    index=len(months_available) - 1, format_func=lambda m: BULAN_FULL[m],
)

all_brands = sorted(set(df_in_raw["Brand"].dropna().unique()) | set(df_out_raw["Brand"].dropna().unique()))
sel_brands = st.sidebar.multiselect("🏷️ Brand", all_brands, default=all_brands)

sel_sales = st.sidebar.multiselect("🧑‍💼 Sales", SALES_LIST, default=SALES_LIST)

st.sidebar.markdown("---")
st.sidebar.caption(
    f"📁 SELL_IN.parquet — update terakhir: {datetime.fromtimestamp(os.path.getmtime(SELL_IN_FILE)):%d %b %Y %H:%M}"
)
st.sidebar.caption(
    f"📁 SELLOUT.parquet — update terakhir: {datetime.fromtimestamp(os.path.getmtime(SELLOUT_FILE)):%d %b %Y %H:%M}"
)

if not sel_brands:
    sel_brands = all_brands
if not sel_sales:
    sel_sales = SALES_LIST

sel_quarter = (sel_month - 1) // 3 + 1

# ---- Dataset dasar setelah filter Brand & Sales (tanpa filter tahun/bulan dulu) ----
df_in_bs = df_in_raw[df_in_raw["Brand"].isin(sel_brands) & df_in_raw["Sales"].isin(sel_sales)]
df_out_bs = df_out_raw[df_out_raw["Brand"].isin(sel_brands) & df_out_raw["Sales"].isin(sel_sales)]

# ---- Dataset per tahun terpilih ----
df_in_year = df_in_bs[df_in_bs["Year"] == sel_year]
df_out_year = df_out_bs[df_out_bs["Year"] == sel_year]

# ---- Dataset bulan terpilih (bulan berjalan) ----
df_in_month = df_in_year[df_in_year["Month"] == sel_month]
df_out_month = df_out_year[df_out_year["Month"] == sel_month]

# ======================================================================================
# 8. KPI RINGKAS
# ======================================================================================
k1, k2, k3, k4 = st.columns(4)
k1.metric(f"Total Sell In {BULAN_FULL[sel_month]} {sel_year}", format_short(df_in_month["Amount"].sum()))
k2.metric(f"Total Sell Out {BULAN_FULL[sel_month]} {sel_year}", format_short(df_out_month["Amount"].sum()))
k3.metric(f"Total Sell In {sel_year} (YTD)", format_short(df_in_year["Amount"].sum()))
k4.metric(f"Total Sell Out {sel_year} (YTD)", format_short(df_out_year["Amount"].sum()))

st.write("")

tabs = st.tabs([
    "📊 Ringkasan Brand", "🧑‍💼 Performa Sales", "🥧 Kategori & Perbandingan YoY",
    "🏆 Top 10 Toko", "📚 Rekap Toko Tahunan", "💎 Hero vs Basic Product",
])

# ======================================================================================
# TAB 1 — RINGKASAN BRAND (Poin 1 & 7)
# ======================================================================================
with tabs[0]:
    st.markdown('<span class="section-badge">Poin 1 & 7</span>', unsafe_allow_html=True)
    st.subheader(f"Sell In per Brand — {sel_year}")

    g = df_in_year.groupby(["Month", "Brand"], as_index=False)["Amount"].sum()
    if g.empty:
        st.info("Belum ada data untuk kombinasi filter ini.")
    else:
        g["Bulan"] = g["Month"].map(BULAN_SINGKAT)
        order_bulan = [BULAN_SINGKAT[m] for m in sorted(g["Month"].unique())]
        fig = px.bar(
            g, x="Bulan", y="Amount", color="Brand", barmode="group",
            category_orders={"Bulan": order_bulan}, color_discrete_map=BRAND_COLORS,
            labels={"Amount": "Sell In (Rp)"},
        )
        fig.update_traces(hovertemplate="%{x}<br>%{fullData.name}: Rp%{y:,.0f}<extra></extra>")
        st.plotly_chart(style_fig(fig, 460), use_container_width=True)

    st.divider()
    st.subheader(f"Sell In per Brand — {BULAN_FULL[sel_month]} {sel_year} (per Sales)")
    st.caption("Poin 5 — grafik ini otomatis mengikuti filter bulan di sidebar")
    g5 = df_in_month.groupby(["Brand", "Sales"], as_index=False)["Amount"].sum()
    if g5.empty:
        st.info("Belum ada data untuk kombinasi filter ini.")
    else:
        fig5 = px.bar(g5, x="Brand", y="Amount", color="Sales", barmode="group",
                      color_discrete_map=SALES_COLORS, labels={"Amount": "Sell In (Rp)"})
        fig5.update_traces(hovertemplate="%{x} — %{fullData.name}: Rp%{y:,.0f}<extra></extra>")
        st.plotly_chart(style_fig(fig5, 420), use_container_width=True)

    st.subheader(f"Sell Out per Brand — {BULAN_FULL[sel_month]} {sel_year} (per Sales)")
    st.caption("Poin 6 — grafik ini otomatis mengikuti filter bulan di sidebar")
    g6 = df_out_month.groupby(["Brand", "Sales"], as_index=False)["Amount"].sum()
    if g6.empty:
        st.info("Belum ada data untuk kombinasi filter ini.")
    else:
        fig6 = px.bar(g6, x="Brand", y="Amount", color="Sales", barmode="group",
                      color_discrete_map=SALES_COLORS, labels={"Amount": "Sell Out (Rp)"})
        fig6.update_traces(hovertemplate="%{x} — %{fullData.name}: Rp%{y:,.0f}<extra></extra>")
        st.plotly_chart(style_fig(fig6, 420), use_container_width=True)


# ======================================================================================
# FUNGSI CHART KUARTAL PER SALES (Poin 2, 3, 4)
# ======================================================================================
def quarterly_chart(sales_name):
    months_in_q = QUARTER_BULAN[sel_quarter]
    df_in_s = df_in_bs[(df_in_bs["Year"] == sel_year) & (df_in_bs["Sales"] == sales_name)]
    df_out_s = df_out_bs[(df_out_bs["Year"] == sel_year) & (df_out_bs["Sales"] == sales_name)]

    sin_full = df_in_s.groupby("Month")["Amount"].sum()
    sout_full = df_out_s.groupby("Month")["Amount"].sum()

    labels, sell_in_vals, sell_out_vals, growth_in, growth_out = [], [], [], [], []
    for m in months_in_q:
        labels.append(BULAN_SINGKAT[m])
        cur_in = sin_full.get(m, 0)
        cur_out = sout_full.get(m, 0)
        prev_in = sin_full.get(m - 1, None) if (m - 1) in sin_full.index else None
        prev_out = sout_full.get(m - 1, None) if (m - 1) in sout_full.index else None
        sell_in_vals.append(cur_in)
        sell_out_vals.append(cur_out)
        growth_in.append(growth_pct(cur_in, prev_in))
        growth_out.append(growth_pct(cur_out, prev_out))

    fig = go.Figure()
    fig.add_bar(name="Sell In", x=labels, y=sell_in_vals, marker_color="#7C3AED",
                text=[format_short(v) for v in sell_in_vals], textposition="outside")
    fig.add_bar(name="Sell Out", x=labels, y=sell_out_vals, marker_color="#EC4899",
                text=[format_short(v) for v in sell_out_vals], textposition="outside")
    fig.update_layout(barmode="group")

    ymax = max(sell_in_vals + sell_out_vals + [1])
    for i, lbl in enumerate(labels):
        gtxt = f"SI {growth_label(growth_in[i])} | SO {growth_label(growth_out[i])}"
        fig.add_annotation(x=lbl, y=ymax * 1.18, text=gtxt, showarrow=False,
                            font=dict(size=11, color="#FDE68A"))
    fig.update_yaxes(range=[0, ymax * 1.32])
    return style_fig(fig, 420)


with tabs[1]:
    st.markdown('<span class="section-badge">Poin 2, 3, 4</span>', unsafe_allow_html=True)
    st.subheader(f"Sell In vs Sell Out per Sales — {QUARTER_LABEL[sel_quarter]} {sel_year}")
    st.caption("Angka total & growth % (dibanding bulan sebelumnya) ditampilkan di atas diagram.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🌸 Liza")
        st.plotly_chart(quarterly_chart("Liza"), use_container_width=True)
        st.metric("Total Sell In (Kuartal)", format_short(df_in_bs[(df_in_bs.Year == sel_year) & (df_in_bs.Sales == "Liza") & (df_in_bs.Quarter == sel_quarter)]["Amount"].sum()))
    with c2:
        st.markdown("#### 🌊 Yoga")
        st.plotly_chart(quarterly_chart("Yoga"), use_container_width=True)
        st.metric("Total Sell In (Kuartal)", format_short(df_in_bs[(df_in_bs.Year == sel_year) & (df_in_bs.Sales == "Yoga") & (df_in_bs.Quarter == sel_quarter)]["Amount"].sum()))
    with c3:
        st.markdown("#### 🔮 Fanny")
        st.plotly_chart(quarterly_chart("Fanny"), use_container_width=True)
        st.metric("Total Sell In (Kuartal)", format_short(df_in_bs[(df_in_bs.Year == sel_year) & (df_in_bs.Sales == "Fanny") & (df_in_bs.Quarter == sel_quarter)]["Amount"].sum()))


# ======================================================================================
# TAB 3 — KATEGORI (Poin 8) & YoY (Poin 9, 10)
# ======================================================================================
def yoy_chart(metric_df_bs, amount_label):
    years_ctx = sorted(set(metric_df_bs["Year"].unique()))
    g = metric_df_bs[metric_df_bs["Month"] == sel_month].groupby(["Year", "Brand"], as_index=False)["Amount"].sum()
    if g.empty:
        return None, None
    fig = px.bar(g, x="Year", y="Amount", color="Brand", barmode="group",
                 color_discrete_map=BRAND_COLORS, labels={"Amount": amount_label, "Year": "Tahun"})
    fig.update_xaxes(type="category")
    fig.update_traces(hovertemplate="%{x} — %{fullData.name}: Rp%{y:,.0f}<extra></extra>")

    totals = metric_df_bs[metric_df_bs["Month"] == sel_month].groupby("Year")["Amount"].sum()
    ymax = g.groupby("Year")["Amount"].sum().max() if not g.empty else 1
    for y in years_ctx:
        cur = totals.get(y, 0)
        prev = totals.get(y - 1, None)
        g_ = growth_pct(cur, prev) if prev else None
        txt = f"{format_short(cur)}  ({growth_label(g_)})"
        fig.add_annotation(x=str(y), y=ymax * 1.18, text=txt, showarrow=False, font=dict(size=11, color="#FDE68A"))
    fig.update_yaxes(range=[0, ymax * 1.35])
    return style_fig(fig, 440), totals


with tabs[2]:
    st.markdown('<span class="section-badge">Poin 8</span>', unsafe_allow_html=True)
    st.subheader(f"Komposisi Kategori Sell Out — {BULAN_FULL[sel_month]} {sel_year}")
    gcat = df_out_month.groupby("Kategori", as_index=False)["Amount"].sum()
    if gcat.empty:
        st.info("Belum ada data untuk kombinasi filter ini.")
    else:
        figcat = px.pie(gcat, names="Kategori", values="Amount", hole=0.45,
                         color="Kategori", color_discrete_map=CAT_COLORS)
        figcat.update_traces(textinfo="label+percent", textfont_size=13)
        st.plotly_chart(style_fig(figcat, 440), use_container_width=True)

    st.divider()
    st.markdown('<span class="section-badge">Poin 9</span>', unsafe_allow_html=True)
    st.subheader(f"Sell In per Brand — YoY Bulan {BULAN_FULL[sel_month]}")
    fig9, _ = yoy_chart(df_in_bs, "Sell In (Rp)")
    if fig9 is None:
        st.info("Belum ada data untuk kombinasi filter ini.")
    else:
        st.plotly_chart(fig9, use_container_width=True)

    st.markdown('<span class="section-badge">Poin 10</span>', unsafe_allow_html=True)
    st.subheader(f"Sell Out per Brand — YoY Bulan {BULAN_FULL[sel_month]}")
    fig10, _ = yoy_chart(df_out_bs, "Sell Out (Rp)")
    if fig10 is None:
        st.info("Belum ada data untuk kombinasi filter ini.")
    else:
        st.plotly_chart(fig10, use_container_width=True)


# ======================================================================================
# TAB 4 — TOP 10 TOKO BULAN BERJALAN (Poin 11 & 12)
# ======================================================================================
def top10_table(df_month, label):
    if df_month.empty:
        st.info("Belum ada data untuk kombinasi filter ini.")
        return
    pivot = df_month.pivot_table(index="Customer Group", columns="Brand", values="Amount",
                                  aggfunc="sum", fill_value=0)
    pivot["Total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("Total", ascending=False).head(10)
    pivot_jt = (pivot / 1_000_000).round(2)
    pivot_jt = pivot_jt.reset_index().rename(columns={"Customer Group": "Toko / Grup"})
    st.caption(f"Nilai dalam **Juta Rupiah (Jt Rp)** — klik header kolom untuk mengurutkan (sortable) · {label}")
    st.dataframe(pivot_jt, use_container_width=True, hide_index=True)


with tabs[3]:
    st.markdown('<span class="section-badge">Poin 11</span>', unsafe_allow_html=True)
    st.subheader(f"Top 10 Toko — Sell In {BULAN_FULL[sel_month]} {sel_year}")
    top10_table(df_in_month, "Sell In")

    st.divider()
    st.markdown('<span class="section-badge">Poin 12</span>', unsafe_allow_html=True)
    st.subheader(f"Top 10 Toko — Sell Out {BULAN_FULL[sel_month]} {sel_year}")
    top10_table(df_out_month, "Sell Out")


# ======================================================================================
# TAB 5 — REKAP TOKO TAHUNAN (Poin 13 & 14)
# ======================================================================================
def annual_store_table(df_year, label):
    if df_year.empty:
        st.info("Belum ada data untuk kombinasi filter ini.")
        return
    target_groups = list(STORE_GROUPS.keys())
    df_target = df_year[df_year["Customer Group"].isin(target_groups)]
    if df_target.empty:
        st.info("Belum ada data toko target pada tahun/filter ini.")
        return

    pivot = df_target.pivot_table(index="Customer Group", columns="Month", values="Amount",
                                   aggfunc="sum", fill_value=0)
    for m in range(1, 13):
        if m not in pivot.columns:
            pivot[m] = 0
    pivot = pivot[sorted(pivot.columns)]
    pivot["Total"] = pivot.sum(axis=1)
    pivot = pivot.reindex(target_groups).fillna(0)
    pivot_jt = (pivot / 1_000_000).round(2)
    pivot_jt.columns = [BULAN_SINGKAT.get(c, c) if isinstance(c, int) else c for c in pivot_jt.columns]
    pivot_jt = pivot_jt.reset_index().rename(columns={"Customer Group": "Toko / Grup"})
    st.caption(f"Nilai dalam **Juta Rupiah (Jt Rp)**, Januari–Desember {sel_year} · {label}")
    st.dataframe(pivot_jt, use_container_width=True, hide_index=True)

    for group, members in STORE_GROUPS.items():
        if len(members) <= 1:
            continue
        with st.expander(f"🔎 Rincian anggota — {group}"):
            df_g = df_target[df_target["Customer Group"] == group]
            detail = df_g.pivot_table(index="Customer", columns="Month", values="Amount",
                                       aggfunc="sum", fill_value=0)
            for m in range(1, 13):
                if m not in detail.columns:
                    detail[m] = 0
            detail = detail[sorted(detail.columns)]
            detail["Total"] = detail.sum(axis=1)
            detail_jt = (detail / 1_000_000).round(2)
            detail_jt.columns = [BULAN_SINGKAT.get(c, c) if isinstance(c, int) else c for c in detail_jt.columns]
            detail_jt = detail_jt.reset_index().rename(columns={"Customer": "Nama Toko"})
            st.dataframe(detail_jt, use_container_width=True, hide_index=True)


with tabs[4]:
    st.markdown('<span class="section-badge">Poin 13</span>', unsafe_allow_html=True)
    st.subheader(f"Rekap Sell In Tahunan Toko Prioritas — {sel_year}")
    annual_store_table(df_in_year, "Sell In")

    st.divider()
    st.markdown('<span class="section-badge">Poin 14</span>', unsafe_allow_html=True)
    st.subheader(f"Rekap Sell Out Tahunan Toko Prioritas — {sel_year}")
    annual_store_table(df_out_year, "Sell Out")


# ======================================================================================
# TAB 6 — HERO vs BASIC PRODUCT (Poin 15, 16, 17)
# ======================================================================================
def hero_pie(df_month, label):
    if df_month.empty:
        st.info("Belum ada data untuk kombinasi filter ini.")
        return
    brands_present = [b for b in sel_brands if b in df_month["Brand"].unique()]
    if not brands_present:
        st.info("Belum ada data untuk kombinasi filter ini.")
        return
    cols = st.columns(min(3, len(brands_present)) or 1)
    for i, brand in enumerate(brands_present):
        d = df_month[df_month["Brand"] == brand]
        g = d.groupby("Kategori Produk", as_index=False)["Amount"].sum()
        total = g["Amount"].sum()
        fig = px.pie(g, names="Kategori Produk", values="Amount", hole=0.45,
                     color="Kategori Produk", color_discrete_map=HERO_COLORS)
        # tampilkan nominal (Rp) + persentase langsung di dalam diagram pie
        fig.update_traces(
            textinfo="label+percent", textfont_size=12,
            customdata=g["Amount"].apply(format_rp),
            texttemplate="%{label}<br>%{customdata}<br>(%{percent})",
        )
        fig.update_layout(title=dict(text=f"{brand} — {BULAN_FULL[sel_month]} {sel_year}", font=dict(size=13)))
        with cols[i % len(cols)]:
            st.plotly_chart(style_fig(fig, 380), use_container_width=True)
    st.caption(f"{label} — total Hero vs Basic Product per brand, bulan {BULAN_FULL[sel_month]} {sel_year}.")


with tabs[5]:
    st.markdown('<span class="section-badge">Poin 15</span>', unsafe_allow_html=True)
    st.subheader(f"Perbandingan Total Hero vs Basic Product — {BULAN_FULL[sel_month]} {sel_year}")
    colA, colB = st.columns(2)
    with colA:
        st.markdown("**Sell In**")
        gh_in = df_in_month.groupby("Kategori Produk", as_index=False)["Amount"].sum()
        if gh_in.empty:
            st.info("Belum ada data.")
        else:
            fig_in = px.bar(gh_in, x="Kategori Produk", y="Amount", color="Kategori Produk",
                             color_discrete_map=HERO_COLORS, text=gh_in["Amount"].apply(format_short))
            fig_in.update_traces(textposition="outside")
            st.plotly_chart(style_fig(fig_in, 360), use_container_width=True)
    with colB:
        st.markdown("**Sell Out**")
        gh_out = df_out_month.groupby("Kategori Produk", as_index=False)["Amount"].sum()
        if gh_out.empty:
            st.info("Belum ada data.")
        else:
            fig_out = px.bar(gh_out, x="Kategori Produk", y="Amount", color="Kategori Produk",
                              color_discrete_map=HERO_COLORS, text=gh_out["Amount"].apply(format_short))
            fig_out.update_traces(textposition="outside")
            st.plotly_chart(style_fig(fig_out, 360), use_container_width=True)

    st.divider()
    st.markdown('<span class="section-badge">Poin 16</span>', unsafe_allow_html=True)
    st.subheader("Hero vs Basic Product — Sell In per Brand")
    hero_pie(df_in_month, "Sell In")

    st.divider()
    st.markdown('<span class="section-badge">Poin 17</span>', unsafe_allow_html=True)
    st.subheader("Hero vs Basic Product — Sell Out per Brand")
    hero_pie(df_out_month, "Sell Out")

st.write("")
st.markdown("---")
st.caption("Dashboard Regional Solo Raya · Dibuat dengan ❤️ Streamlit + Plotly · Data auto-update setiap file Excel di-replace.")
