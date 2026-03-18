"""Wikimedia momentum panel — Wikipedia pageview trend slopes per brand."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

COLORS = {
    "bg": "#111827",
    "blue": "#06B6D4",
    "green": "#2C996A",
    "red": "#F58484",
    "text": "#F9FAFB",
    "muted": "#6B7280",
    "surface": "#1F2937",
}


def render(df: pd.DataFrame, callout: str) -> None:
    """
    df must have: brand, avg_monthly_views, momentum_pct
    Bar color driven by momentum_pct: positive = green, negative = red.
    """
    st.markdown("### 📖 Wikimedia Momentum — Wikipedia Pageview Trends")

    df = df.sort_values("momentum_pct", ascending=False).head(10)
    df["bar_color"] = df["momentum_pct"].apply(
        lambda s: COLORS["green"] if s >= 0 else COLORS["red"]
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["brand"],
        y=df["avg_monthly_views"],
        marker_color=df["bar_color"],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Avg Monthly Views: %{y:,.0f}<br>"
            "Momentum Score: %{customdata:.2f}<extra></extra>"
        ),
        customdata=df["momentum_pct"],
    ))

    # Zero baseline
    fig.add_hline(y=0, line_color=COLORS["muted"], line_width=1)

    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"], family="monospace"),
        xaxis=dict(
            showgrid=False,
            tickangle=-30,
            tickfont=dict(color=COLORS["text"], size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["surface"],
            tickfont=dict(color=COLORS["muted"]),
            title=dict(text="Avg Daily Views", font=dict(color=COLORS["muted"], size=10)),
        ),
        margin=dict(l=10, r=10, t=20, b=80),
        height=380,
    )

    # Legend note
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f"<span style='color:{COLORS['green']};font-size:12px;'>▲ Growing</span>"
        f"&nbsp;&nbsp;"
        f"<span style='color:{COLORS['red']};font-size:12px;'>▼ Declining</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:{COLORS['muted']};font-size:13px;font-style:italic;'>{callout}</p>",
        unsafe_allow_html=True,
    )
