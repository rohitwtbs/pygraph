import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from input import InputBox

st.set_page_config(page_title="PyGraph", layout="wide")
st.title("📈 PyGraph")

equation = InputBox()

x = np.linspace(-10, 10, 2000)

try:
    f = equation.parse()
    y = np.array(f(x), dtype=float)
    y[~np.isfinite(y)] = np.nan

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode="lines",
        line=dict(color="#1f77b4", width=2),
        name=equation.expr_text
    ))

    fig.update_layout(
        dragmode="pan",                  # pan by default, scroll to zoom
        xaxis=dict(
            showgrid=True,
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=1.5,
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=1.5,
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=600,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": True,          # smooth scroll to zoom
            "displayModeBar": True,
            "modeBarButtonsToRemove": ["select2d", "lasso2d"],
        }
    )
except Exception as e:
    st.error(f"Invalid function: {e}")