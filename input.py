import streamlit as st
import numpy as np
import pandas as pd
import sympy as sp


class InputBox():
    def __init__(self, default="sinx(x)"):
        self.default = default
        self.allowed = {
            "x": sp.symbols("x)"),
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "exp": sp.exp,
        }
        pass

    def render(self):
        return st.text_input("Enter f(x)", value=self.default)
    