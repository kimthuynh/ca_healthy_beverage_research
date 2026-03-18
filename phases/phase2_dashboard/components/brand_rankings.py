"""Brand rankings leaderboard panel."""

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
    df must have: brand, composite_score, trends_avg, trends_momentum_shifted
    """
    st.markdown("### 🏆 Brand Rankings")

    df = df.sort_values("composite_score", ascending=False).head(10).reset_index(drop=True)
    df["rank"] = df.index + 1

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["composite_score"],
        y=df["brand"],
        orientation="h",
        marker=dict(
            color=df["composite_score"],
            colorscale=[[0, COLORS["surface"]], [1, COLORS["blue"]]],
            line=dict(width=0),
        ),
        text=df["composite_score"].round(1).astype(str),
        textposition="inside",
        textfont=dict(color=COLORS["text"], size=12),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Composite Score: %{x:.1f}<br>"
            "Trends Avg: %{customdata[0]:.1f}<br>"
            "Momentum Shift: %{customdata[1]:+.2f}<extra></extra>"
        ),
        customdata=df[["trends_avg", "trends_momentum_shifted"]].values,
    ))

    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"], family="monospace"),
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(color=COLORS["muted"]),
            range=[0, 100],
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color=COLORS["text"], size=13),
            autorange="reversed",
        ),
        margin=dict(l=10, r=20, t=20, b=20),
        height=380,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Callout
    st.markdown(
        f"<p style='color:{COLORS['muted']};font-size:13px;font-style:italic;'>{callout}</p>",
        unsafe_allow_html=True,
    )
