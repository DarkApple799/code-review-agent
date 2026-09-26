@echo off
rem 在任意目录下审查代码（子命令写在路径前后都行）：
rem   review.cmd                  审查当前目录
rem   review.cmd "D:\proj"        审查指定目录
rem   review.cmd "D:\proj" scan   只跑静态规则（不联网、免费）
rem   review.cmd "D:\proj" --focus security --offline
chcp 65001 >nul
python "%~dp0review.py" %*
echo.
pause
