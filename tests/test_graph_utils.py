"""Unit tests for graph_utils.compute_graph."""

import math

import numpy as np
import pandas as pd
import pytest

from graph_utils import (
    NUM_POINTS,
    SUPPORTED_EQUATIONS,
    X_MAX,
    X_MIN,
    compute_graph,
)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _df(eq: str, freq: int = 1) -> pd.DataFrame:
    return compute_graph(eq, freq)


# ── Return-type and shape tests ──────────────────────────────────────────────

class TestReturnType:
    def test_returns_dataframe(self):
        assert isinstance(_df("sin"), pd.DataFrame)

    @pytest.mark.parametrize("eq", SUPPORTED_EQUATIONS)
    def test_shape(self, eq):
        df = _df(eq)
        assert df.shape == (NUM_POINTS, 1), f"Expected ({NUM_POINTS}, 1), got {df.shape}"

    @pytest.mark.parametrize("eq", SUPPORTED_EQUATIONS)
    def test_column_name_matches_equation(self, eq):
        assert list(_df(eq).columns) == [eq]

    @pytest.mark.parametrize("eq", SUPPORTED_EQUATIONS)
    def test_index_range(self, eq):
        df = _df(eq)
        assert math.isclose(df.index[0], X_MIN, rel_tol=1e-6)
        assert math.isclose(df.index[-1], X_MAX, rel_tol=1e-6)


# ── Value correctness tests ──────────────────────────────────────────────────

class TestSinValues:
    def test_sin_zero_at_origin(self):
        df = _df("sin")
        # x closest to 0
        idx = df.index.get_indexer([0.0], method="nearest")[0]
        assert abs(df["sin"].iloc[idx]) < 0.02

    def test_sin_bounded(self):
        df = _df("sin")
        valid = df["sin"].dropna()
        assert (valid >= -1.0 - 1e-9).all()
        assert (valid <= 1.0 + 1e-9).all()

    def test_sin_no_nan(self):
        """sin is defined everywhere — no NaN expected."""
        assert _df("sin")["sin"].notna().all()

    @pytest.mark.parametrize("freq", [1, 2, 5, 10])
    def test_sin_frequency_scaling(self, freq):
        """Higher frequency → more zero crossings inside [-10, 10]."""
        y1 = _df("sin", freq=1)["sin"].values
        yf = _df("sin", freq=freq)["sin"].values
        crossings1 = int(np.sum(np.diff(np.sign(y1)) != 0))
        crossingsf = int(np.sum(np.diff(np.sign(yf)) != 0))
        if freq > 1:
            assert crossingsf > crossings1, (
                f"freq={freq} should produce more crossings than freq=1"
            )


class TestCosValues:
    def test_cos_one_at_origin(self):
        df = _df("cos")
        idx = df.index.get_indexer([0.0], method="nearest")[0]
        assert abs(df["cos"].iloc[idx] - 1.0) < 0.02

    def test_cos_bounded(self):
        df = _df("cos")
        valid = df["cos"].dropna()
        assert (valid >= -1.0 - 1e-9).all()
        assert (valid <= 1.0 + 1e-9).all()

    def test_cos_no_nan(self):
        """cos is defined everywhere — no NaN expected."""
        assert _df("cos")["cos"].notna().all()

    @pytest.mark.parametrize("freq", [1, 2, 5, 10])
    def test_cos_frequency_scaling(self, freq):
        """cos(freq·x) at x=0 is always 1."""
        df = _df("cos", freq=freq)
        idx = df.index.get_indexer([0.0], method="nearest")[0]
        assert abs(df["cos"].iloc[idx] - 1.0) < 0.02


class TestTanValues:
    def test_tan_has_nan_at_asymptotes(self):
        """With enough frequency, some sample points land near an asymptote
        and produce very large finite values — or NaN if they land exactly on
        one.  We test both: either the series contains NaN, or it contains
        values whose absolute magnitude exceeds 1 (i.e. outside the sin/cos
        bound), which confirms the tan function is behaving correctly."""
        df = _df("tan", freq=5)  # higher freq → more asymptotes in [-10, 10]
        series = df["tan"]
        has_nan = series.isna().any()
        has_large = (series.abs() > 1.0).any()
        assert has_nan or has_large, (
            "tan(freq·x) should have NaN or values outside [-1, 1]"
        )

    def test_tan_no_inf(self):
        """All infinite values should have been replaced by NaN."""
        df = _df("tan")
        assert not np.isinf(df["tan"].values).any()

    def test_tan_zero_at_origin(self):
        df = _df("tan")
        idx = df.index.get_indexer([0.0], method="nearest")[0]
        assert abs(df["tan"].iloc[idx]) < 0.02


# ── Edge-case and error tests ────────────────────────────────────────────────

class TestEdgeCases:
    def test_invalid_equation_raises(self):
        with pytest.raises(ValueError, match="Unsupported equation"):
            compute_graph("invalid", 1)

    @pytest.mark.parametrize("eq", SUPPORTED_EQUATIONS)
    def test_freq_one_is_default_identity(self, eq):
        """Calling with freq=1 twice returns equal DataFrames."""
        df_a = compute_graph(eq, 1)
        df_b = compute_graph(eq, 1)
        pd.testing.assert_frame_equal(df_a, df_b)

    @pytest.mark.parametrize("eq", SUPPORTED_EQUATIONS)
    def test_different_frequencies_differ(self, eq):
        """freq=1 and freq=2 should not produce identical results."""
        df1 = compute_graph(eq, 1)
        df2 = compute_graph(eq, 2)
        assert not df1[eq].equals(df2[eq])

    @pytest.mark.parametrize("eq", SUPPORTED_EQUATIONS)
    def test_output_dtype_is_float(self, eq):
        df = _df(eq)
        assert df[eq].dtype == np.float64
