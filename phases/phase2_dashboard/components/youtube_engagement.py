"""YouTube engagement panel — view + comment volume per brand."""

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
    df must have: brand, total_views, total_comments, engagement_score
    """
    st.markdown("### 📺 YouTube Engagement")

    df = df.sort_values("engagement_score", ascending=False).head(10)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Views",
        x=df["brand"],
        y=df["total_views"],
        marker_color=COLORS["blue"],
        yaxis="y",
        hovertemplate="<b>%{x}</b><br>Views: %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        name="Comments",
        x=df["brand"],
        y=df["total_comments"],
        mode="markers+lines",
        marker=dict(color=COLORS["green"], size=9),
        line=dict(color=COLORS["green"], width=1.5, dash="dot"),
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>Comments: %{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
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
            title=dict(text="Views", font=dict(color=COLORS["muted"], size=10)),
        ),
        yaxis2=dict(
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color=COLORS["green"], size=10),
            title=dict(text="Comments", font=dict(color=COLORS["green"], size=10)),
        ),
        margin=dict(l=10, r=60, t=40, b=80),
        height=380,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"<p style='color:{COLORS['muted']};font-size:13px;font-style:italic;'>{callout}</p>",
        unsafe_allow_html=True,
    )
