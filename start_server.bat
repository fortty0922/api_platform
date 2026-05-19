@echo off
chcp 65001 > nul
setlocal

:: 取得目前批次檔所在的目錄
set "DIR=%~dp0"

echo =================================================
echo 🚀 啟動 API Platform 伺服器...
echo =================================================

:: 檢查是否有 Python 環境
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ 找不到 Python 指令。請確保您已啟用虛擬環境 (venv 或 conda)。
    exit /b 1
)

:: 切換到專案目錄
cd /d "%DIR%api_platform"

:: 1. 執行資料庫遷移
echo 📦 檢查並更新資料庫狀態...
python manage.py migrate --noinput

echo.
echo 🌐 伺服器即將啟動 (Daphne ASGI Server)
echo 👉 監控面板: http://127.0.0.1:8000/dashboard/
echo 👉 API 列表:  http://127.0.0.1:8000/api/help/
echo 💡 提示: 按下 Ctrl+C 可停止伺服器
echo -------------------------------------------------

:: 2. 啟動伺服器
daphne -b 127.0.0.1 -p 8000 api_platform.asgi:application
