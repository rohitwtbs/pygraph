import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="PyGraph", layout="wide")
st.title("📈 PyGraph")

equation = st.selectbox("Select Function", ["sin", "cos", "tan"])
freq = st.slider("Frequency", 1, 10, 1)

if "x_range" not in st.session_state:
    st.session_state.x_range = [-10, 10]
if "y_range" not in st.session_state:
    st.session_state.y_range = [-5, 5]

x_min, x_max = st.session_state.x_range
x = np.linspace(x_min, x_max, 3000)

if equation == "sin":
    y = np.sin(freq * x)
elif equation == "cos":
    y = np.cos(freq * x)
else:
    y = np.tan(freq * x)

y = np.array(y, dtype=float)
y[~np.isfinite(y)] = np.nan

BG_COLOR = "#0e1117"
GRID_COLOR = "#2d2d2d"
LINE_COLOR = "#ffffff"

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=x, y=y,
    mode="lines",
    line=dict(color="#1f77b4", width=2),
    name=equation
))

fig.update_layout(
    dragmode="pan",
    paper_bgcolor=BG_COLOR,      # outer background
    plot_bgcolor=BG_COLOR,       # inner plot background
    xaxis=dict(
        range=st.session_state.x_range,
        showgrid=True,
        zeroline=True,
        zerolinecolor=LINE_COLOR,
        zerolinewidth=2,
        gridcolor=GRID_COLOR,
        color=LINE_COLOR,         # axis text/tick color
    ),
    yaxis=dict(
        range=st.session_state.y_range,
        showgrid=True,
        zeroline=True,
        zerolinecolor=LINE_COLOR,
        zerolinewidth=2,
        gridcolor=GRID_COLOR,
        color=LINE_COLOR,         # axis text/tick color
    ),
    font=dict(color=LINE_COLOR),  # all text color
    margin=dict(l=0, r=0, t=30, b=0),
    height=600,
)

event = st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "scrollZoom": True,
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["select2d", "lasso2d"],
    },
    on_select="rerun",
    key="graph"
)

if event and "layout" in event:
    layout = event["layout"]
    if "xaxis.range[0]" in layout:
        st.session_state.x_range = [layout["xaxis.range[0]"], layout["xaxis.range[1]"]]
    if "yaxis.range[0]" in layout:
        st.session_state.y_range = [layout["yaxis.range[0]"], layout["yaxis.range[1]"]]
    st.rerun()