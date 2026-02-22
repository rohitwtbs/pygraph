import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="PyGraph", layout="wide")

# ── Instant dark background ────────────────────────────────────────────────
# Injected before any Streamlit widget renders, so the browser paints the
# correct background immediately instead of showing a white flash.
st.html("""
<style>
  html, body,
  [data-testid="stApp"],
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"] {
    background-color: #0e1117 !important;
  }
  /* Suppress the Streamlit rainbow top-bar decoration */
  [data-testid="stDecoration"] { display: none; }
</style>
""")

BG_COLOR   = "#0e1117"
GRID_COLOR = "#2d2d2d"
LINE_COLOR = "#ffffff"

# ── Cached computation ─────────────────────────────────────────────────────
# Results are reused across reruns when the inputs haven't changed,
# keeping the server-side work near-zero for repeated interactions.
@st.cache_data(max_entries=64)
def compute_graph(equation: str, freq: int, x_min: float, x_max: float):
    # 800 pts is indistinguishable from 3 000 on a ~1 000 px canvas but
    # produces a ~4× smaller JSON payload → faster serialisation & transfer.
    x = np.linspace(x_min, x_max, 800)
    if equation == "sin":
        y = np.sin(freq * x)
    elif equation == "cos":
        y = np.cos(freq * x)
    else:
        y = np.tan(freq * x)
    y = np.array(y, dtype=float)
    y[~np.isfinite(y)] = np.nan
    return x, y

# ── UI ─────────────────────────────────────────────────────────────────────
st.title("📈 PyGraph")

equation = st.selectbox("Select Function", ["sin", "cos", "tan"])
freq     = st.slider("Frequency", 1, 10, 1)

if "x_range" not in st.session_state:
    st.session_state.x_range = [-10, 10]
if "y_range" not in st.session_state:
    st.session_state.y_range = [-5, 5]

x_min, x_max = st.session_state.x_range
x, y = compute_graph(equation, freq, x_min, x_max)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=x, y=y,
    mode="lines",
    line=dict(color="#1f77b4", width=2),
    name=equation
))

fig.update_layout(
    dragmode="pan",
    # uirevision keeps Plotly from doing a full teardown/rebuild of the chart
    # on every Streamlit rerun — pan & zoom state are preserved and updates
    # are applied as smooth diffs instead of a cold render.
    uirevision="static",
    paper_bgcolor=BG_COLOR,
    plot_bgcolor=BG_COLOR,
    xaxis=dict(
        range=st.session_state.x_range,
        showgrid=True,
        zeroline=True,
        zerolinecolor=LINE_COLOR,
        zerolinewidth=2,
        gridcolor=GRID_COLOR,
        color=LINE_COLOR,
    ),
    yaxis=dict(
        range=st.session_state.y_range,
        showgrid=True,
        zeroline=True,
        zerolinecolor=LINE_COLOR,
        zerolinewidth=2,
        gridcolor=GRID_COLOR,
        color=LINE_COLOR,
    ),
    font=dict(color=LINE_COLOR),
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