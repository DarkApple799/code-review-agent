@echo off
rem 双击即用：启动 Code Review Agent 的 Web 界面（自动切到本脚本所在目录）
chcp 65001 >nul
cd /d "%~dp0"
echo ================================================
echo   Code Review Agent - Web UI
echo   目录: %CD%
echo   浏览器地址: http://127.0.0.1:8765  （端口号不能省）
echo ================================================
echo.
python webui.py %*
if errorlevel 1 (
  echo.
  echo [提示] 启动失败。常见原因：
  echo   1) 没装 Python，或 python 不在 PATH 中（可试 py webui.py）
  echo   2) 端口被占用，换一个：python webui.py --port 9000
  echo   3) 缺少 .env（复制 .env.example 为 .env 并填入 DEEPSEEK_API_KEY）
)
echo.
pause
