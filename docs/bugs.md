# Bug Tracker

## bug记录表
1. ~~2024年7月6日 开发者模式gg了(发现是因为每次都把developer_mode变成了False)~~
   ```python
      # 侧边栏开发者模式切换按钮
   st.session_state["developer_mode"] = st.sidebar.checkbox(
      "开发者模式", value=st.session_state["developer_mode"]
   )
   ```
2. 
