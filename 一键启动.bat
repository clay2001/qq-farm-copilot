@echo off
chcp 65001 >nul
echo ========================================
echo   QQ Farm Copilot 启动中...
echo ========================================
echo.

cd /d "%~dp0"

echo 正在激活Python 3.10环境并启动程序...
call conda activate cp310
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 程序启动失败！
    pause
    exit /b 1
)

pause
