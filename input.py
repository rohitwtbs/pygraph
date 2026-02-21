import streamlit as st
import sympy as sp


class InputBox:
    def __init__(self, default="sin(x)"):
        self._allowed = {
            "x": sp.symbols("x"),
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "exp": sp.exp,
            "log": sp.log,
            "sqrt": sp.sqrt,
            "pi": sp.pi,
            "abs": sp.Abs,
        }
        self.expr_text = st.text_input("Enter f(x)", value=default)

    def parse(self):
        expr = sp.sympify(self.expr_text, locals=self._allowed)
        return sp.lambdify(sp.symbols("x"), expr, modules=["numpy"])