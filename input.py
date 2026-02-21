import streamlit as st
import numpy as np
import pandas as pd
import sympy as sp


class InputBox():
    def __init__(self, default="sinx(x)"):
        self.expr_text = ""
        self.default = default
        self.allowed = {
            "x": sp.symbols("x)"),
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "exp": sp.exp,
        }
        pass

    def parse(self):
        expr = sp.sympify(self.expr_text, locals=self._allowed)
        return sp.lambdify(sp.symbols("x"), expr, modules=["numpy"])

    def __eq__(self, other):
        return self.expr_text == other
    