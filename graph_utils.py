"""Pure computation utilities for PyGraph — no Streamlit dependency."""

import numpy as np
import pandas as pd

# Number of sample points along the x-axis.
NUM_POINTS = 800

# Default x range.
X_MIN = -10.0
X_MAX = 10.0

SUPPORTED_EQUATIONS = ("sin", "cos", "tan")


def compute_graph(equation: str, freq: int) -> pd.DataFrame:
    """Return a DataFrame of (x, y) values for the given trig function.

    Parameters
    ----------
    equation:
        One of ``"sin"``, ``"cos"``, or ``"tan"``.
    freq:
        Integer frequency multiplier applied to *x* before evaluation.

    Returns
    -------
    pd.DataFrame
        Single-column DataFrame whose index is the x values and whose
        column name matches *equation*.  Infinite values (e.g. tan
        asymptotes) are replaced by ``NaN``.

    Raises
    ------
    ValueError
        If *equation* is not one of the supported functions.
    """
    if equation not in SUPPORTED_EQUATIONS:
        raise ValueError(
            f"Unsupported equation '{equation}'. "
            f"Choose one of {SUPPORTED_EQUATIONS}."
        )

    x = np.linspace(X_MIN, X_MAX, NUM_POINTS)

    if equation == "sin":
        y = np.sin(freq * x)
    elif equation == "cos":
        y = np.cos(freq * x)
    else:  # tan
        y = np.tan(freq * x)

    # Replace ±inf / NaN with NaN for clean charting.
    y = np.where(np.isfinite(y), y, np.nan)

    return pd.DataFrame({equation: y}, index=x)
