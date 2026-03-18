"""
CA Healthy Beverage Intelligence Dashboard — Phase 2
Run: streamlit run phases/phase2_dashboard/app.py
"""

import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from datetime import datetime

from phases.phase2_dashboard.runner import load_all_data, summarize_top10
from phases.phase2_dashboard.claude_callouts import get_all_callouts
from phases.phase2_dashboard.components import (
    brand_rankings,
    sentiment_heatmap,
    trends_chart,
    purchase_channels,
    youtube_engagement,
    wikimedia_momentum,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CA Beverage Intelligence",
    page_icon="🧃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ────────────────────────────────────────────────────────────────
css_path = Path(__file__).parent / "assets" / "style.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    return load_all_data()

try:
    data = load_data()
except (FileNotFoundError, ValueError) as e:
    st.error(f"Data load error: {e}")
    st.stop()

summary = summarize_top10(data["top10"])

# ── Generate Claude callouts ──────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_callouts():
    panel_data = {
        "brand_rankings":    data["top10"].head(5).to_csv(index=False),
        "sentiment_heatmap": data["sentiment"].head(5).to_csv(index=False),
        "trends_chart":      data["trends_raw"].groupby("brand")["interest"].mean().reset_index().head(5).to_csv(index=False),
        "purchase_channels": data["purchase"].head(5).to_csv(index=False),
        "youtube_engagement": data["youtube"].head(5).to_csv(index=False),
        "wikimedia_momentum": data["wikimedia"].head(5).to_csv(index=False),
    }
    return get_all_callouts(panel_data)

callouts = load_callouts()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='color:#06B6D4;'>🧃 CA Healthy Beverage Research</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Market:** California, USA")
    st.markdown("**Period:** Jan 2025 – Mar 2026")
    st.markdown("**Categories:**")
    st.markdown("<span style='color:#F9FAFB;'>- Kombucha & Fermented</span>", unsafe_allow_html=True)
    st.markdown("<span style='color:#F9FAFB;'>- Plant-Based Milks</span>", unsafe_allow_html=True)
    st.markdown("---")

    force_refresh = st.button("🔄 Refresh Callouts", help="Force re-generate Claude callouts")
    if force_refresh:
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown(
        f"<p style='color:#6B7280;font-size:11px;'>Last updated: {datetime.now().strftime('%b %d, %Y %H:%M')}</p>",
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# California Healthy Beverage Intelligence")
st.markdown(
    "<p style='color:#6B7280;font-size:14px;margin-top:-12px;'>Market Intelligence · Phase 2 Dashboard · Internal Use Only</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── KPI tiles ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Brands Tracked", summary["total_brands"])
c2.metric("Top Brand", summary["top_brand"])
c3.metric("Avg Composite Score", summary["avg_score"])
c4.metric("Avg Momentum Shift", summary["avg_momentum"])

st.markdown("---")

# ── Row 1: Rankings + Sentiment ───────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    brand_rankings.render(data["top10"], callouts.get("brand_rankings", ""))
with col2:
    sentiment_heatmap.render(data["sentiment"], callouts.get("sentiment_heatmap", ""))

st.markdown("---")

# ── Row 2: Google Trends (full width) ────────────────────────────────────────
trends_chart.render(data["trends_raw"], callouts.get("trends_chart", ""))

st.markdown("---")

# ── Row 3: YouTube + Wikimedia ────────────────────────────────────────────────
col3, col4 = st.columns(2)
with col3:
    youtube_engagement.render(data["youtube"], callouts.get("youtube_engagement", ""))
with col4:
    wikimedia_momentum.render(data["wikimedia"], callouts.get("wikimedia_momentum", ""))

st.markdown("---")

# ── Row 4: Purchase Channels (full width) ────────────────────────────────────
purchase_channels.render(data["purchase"], callouts.get("purchase_channels", ""))
