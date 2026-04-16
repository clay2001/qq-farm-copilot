@echo off
chcp 65001 >nul
echo ========================================
echo   QQ Farm Copilot 一键更新脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] 正在拉取最新代码...
git fetch origin master
git checkout master
git pull origin master

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 代码更新失败！
    pause
    exit /b 1
)

echo.
echo [2/5] 正在合并到dev分支...
git checkout dev
git merge master

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 合并dev分支失败！
    pause
    exit /b 1
)

echo.
echo [3/5] 正在推送到你的fork...
git push clay dev

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 推送失败！
    pause
    exit /b 1
)

echo.
echo [4/5] 正在更新依赖...
call conda activate cp310
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 依赖安装失败！
    pause
    exit /b 1
)

echo.
echo [5/5] 清理完成
echo.
echo ========================================
echo   更新完成！
echo ========================================
echo.
pause
