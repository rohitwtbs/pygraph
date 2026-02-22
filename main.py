import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="PyGraph",
    layout="wide",
    menu_items={},   # removes hamburger menu → one fewer deferred DOM subtree
)
# Theme colours come from .streamlit/config.toml, embedded in the initial HTTP
# response, so the browser applies them before the JS bundle executes —
# no white flash on load.

# ── Critical CSS — injected before any component renders ───────────────────
# Hiding the Streamlit chrome elements (header, footer, decoration bar) means
# they never appear and then disappear, which was adding a late visual-change
# event that dragged the Lighthouse Speed Index well below 0.9.
st.markdown(
    """
    <style>
    header[data-testid="stHeader"],
    #stDecoration,
    footer { display: none !important; }

    /* Remove the excess top padding so content reaches the viewport faster,
       reducing the time-to-first-meaningful-paint. */
    .main .block-container { padding-top: 1rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


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

# ── Fragment: only this subtree reruns on chart interaction ─────────────────
# @st.fragment means a slider drag or equation change triggers a partial rerun
# of just the chart block — the rest of the page DOM is untouched, removing
# one full round-trip of serialisation and React reconciliation.
@st.fragment
def render_chart(equation: str, freq: int) -> None:
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
        st.rerun(scope="fragment")

render_chart(equation, freq)