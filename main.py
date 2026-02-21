import streamlit as st
import numpy as np
import pandas as pd
from input import InputBox

st.set_page_config(page_title="Simple Calculator")
st.title("📈 PyGraph")


equation = InputBox()
freq = st.slider("Frequency", 1, 10, 1)


x = np.linspace(0, 2 * np.pi, 500)
if equation == "sin":
    y = np.sin(freq * x)
elif equation == "cos":
    y = np.cos(freq * x)
else:
    y = np.tan(freq * x)


chart_data = pd.DataFrame({
    'x': x,
    'y': y
}).set_index('x')


st.line_chart(chart_data)