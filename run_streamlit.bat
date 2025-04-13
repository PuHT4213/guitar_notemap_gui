@echo off
REM filepath: d:\src\notemap\run_streamlit.bat

REM 激活虚拟环境
call .\venv\Scripts\activate

REM 运行 Streamlit 应用
streamlit run .\notemap.py

REM 保持终端窗口打开
pause