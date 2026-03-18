"""Sentiment heatmap panel — positive/neutral/negative % per brand."""

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
    "neutral": "#A78BFA",
}


def render(df: pd.DataFrame, callout: str) -> None:
    """
    df must have: brand, vader_pos, vader_neu, vader_neg
    """
    st.markdown("### 📊 Sentiment Rating")

    df = df.sort_values("vader_pos", ascending=False).head(10)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Positive",
        x=df["brand"],
        y=df["vader_pos"],
        marker_color=COLORS["green"],
        hovertemplate="<b>%{x}</b><br>Positive: %{y:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Neutral",
        x=df["brand"],
        y=df["vader_neu"],
        marker_color=COLORS["neutral"],
        hovertemplate="<b>%{x}</b><br>Neutral: %{y:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Negative",
        x=df["brand"],
        y=df["vader_neg"],
        marker_color=COLORS["red"],
        hovertemplate="<b>%{x}</b><br>Negative: %{y:.2f}<extra></extra>",
    ))

    fig.update_layout(
        barmode="stack",
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"], family="monospace"),
        legend=dict(
            orientation="h",
            x=0, y=1.08,
            font=dict(color=COLORS["text"], size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            showgrid=False,
            tickangle=-30,
            tickfont=dict(color=COLORS["text"], size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["surface"],
            tickfont=dict(color=COLORS["muted"]),
            range=[0, 1],
        ),
        margin=dict(l=10, r=10, t=40, b=80),
        height=380,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"<p style='color:{COLORS['muted']};font-size:13px;font-style:italic;'>{callout}</p>",
        unsafe_allow_html=True,
    )
