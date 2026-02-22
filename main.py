import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(
    page_title="PyGraph",
    layout="wide",
    menu_items={},
)

st.markdown(
    '<meta name="description" content="PyGraph — plot sin, cos and tan functions interactively. Adjust frequency and explore the graph in your browser.">',
    unsafe_allow_html=True,
)

# ── Critical CSS ────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    header[data-testid="stHeader"],
    #stDecoration,
    footer { display: none !important; }

    /* Pre-reserve chart height to prevent CLS.
       Vega-Lite renders inline — no iframe shift, so only title/slider need locking. */

    /* Title row */
    .stElementContainer:has([data-testid="stHeading"]),
    .stElementContainer:has(.stHeading) { min-height: 96px; }

    /* Slider row */
    .stElementContainer:has([data-testid="stSlider"]) { min-height: 72px; }

    /* st.info() alert box — bounding-rect height 56px; lock it to prevent CLS. */
    .stElementContainer:has([data-testid="stAlert"]) { min-height: 60px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Cached computation ──────────────────────────────────────────────────────
@st.cache_data(max_entries=64)
def compute_graph(equation: str, freq: int) -> pd.DataFrame:
    # 800 pts gives smooth curves with a small payload.
    x = np.linspace(-10, 10, 800)
    if equation == "sin":
        y = np.sin(freq * x)
    elif equation == "cos":
        y = np.cos(freq * x)
    else:
        y = np.tan(freq * x)
    y = np.where(np.isfinite(y), y, np.nan)
    return pd.DataFrame({equation: y}, index=x)


# ── UI ──────────────────────────────────────────────────────────────────────
st.title("📈 PyGraph")

equation = st.selectbox(
    "Select Function",
    ["sin", "cos", "tan"],
    index=None,
    placeholder="Choose a function to plot…",
)

if equation is None:
    st.info("Select a function above to plot the graph.", icon="📈")
else:
    freq = st.slider("Frequency", 1, 10, 1)

    # @st.fragment scopes reruns to this block only — slider drags don't
    # re-execute the selectbox or any widget above.
    @st.fragment
    def render_chart(equation: str, freq: int) -> None:
        df = compute_graph(equation, freq)
        st.line_chart(
            df,
            height=600,
            color=["#1f77b4"],
            use_container_width=True,
        )

    render_chart(equation, freq)