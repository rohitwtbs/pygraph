import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Simple Calculator")
st.title("📈 PyGraph")

# 1. Inputs using Streamlit widgets
equation = st.selectbox("Select Function", ["sin", "cos", "tan"])
freq = st.slider("Frequency", 1, 10, 1)

# 2. Generate Data
x = np.linspace(0, 2 * np.pi, 500)
if equation == "sin":
    y = np.sin(freq * x)
elif equation == "cos":
    y = np.cos(freq * x)
else:
    y = np.tan(freq * x)

# 3. Streamlit charts need data in a DataFrame
chart_data = pd.DataFrame({
    'x': x,
    'y': y
}).set_index('x')

# 4. Plot using the native line chart
# This is automatically responsive to screen size
st.line_chart(chart_data)