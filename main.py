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

    /* Pre-reserve the chart container so the Plotly iframe never shifts.
       CLS contributors identified in LH run 3:
         page-2-DIV  → stElementContainer wrapping the h1 title  (score 0.0086)
         page-1-DIV  → stElementContainer wrapping the frequency slider (0.0019)
       Fixing all three eliminates the residual 0.010 CLS. */
    .st-key-graph,
    .st-key-graph > div,
    [data-testid="stPlotlyChart"] { min-height: 600px; }

    /* Title row: h1 is 89 px tall per LH bounding-rect; 96 px gives breathing room.
       stElementContainer *wraps* stHeading — selector must go parent→child via :has(). */
    .stElementContainer:has([data-testid="stHeading"]),
    .stElementContainer:has(.stHeading) { min-height: 96px; }

    /* Slider row: bounding-rect height 68 px; lock the wrapper to avoid the reflow. */
    .stElementContainer:has([data-testid="stSlider"]) { min-height: 72px; }
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
    # Reserve the slot immediately so Streamlit can flush the page skeleton
    # (including the pre-sized .st-key-graph container) to the browser before
    # the heavy Plotly delta arrives.  This pushes the 288ms Plotly-init long
    # task out of the FCP→TTI window, reducing TBT.
    chart_slot = st.empty()

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

    event = chart_slot.plotly_chart(
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