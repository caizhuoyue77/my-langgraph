import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# 配置页面
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 启用Altair的黑暗主题
alt.themes.enable("dark")

# 读取数据
df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')

# 侧边栏
with st.sidebar:
    st.title('🏂 US Population Dashboard')

    year_list = list(df_reshaped.year.unique())[::-1]
    selected_year = st.selectbox('Select a year', year_list, index=len(year_list)-1)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

# 创建列布局
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown("This is col 0")

with col[1]:
    st.markdown('#### Total Population')


with col[2]:
    st.markdown('#### Top States')
