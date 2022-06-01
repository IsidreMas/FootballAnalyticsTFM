import sys
sys.path.append("../source")

import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from Match_Analytics import Match
from Tracking_Visualization import plot_sliding_window


@st.cache
def read_match():
    return [Match(data_source="metrica-sports", match_id=i) for i in [1, 2]]


if __name__ == '__main__':

    m = read_match()
    st.write("# Hello world!\n"
             "This is my master thesis haha")
    st.latex(r"A = \frac{34}{23}")
    a = st.slider("This is amazing hahaha")
    st.write(f"This is {a}")