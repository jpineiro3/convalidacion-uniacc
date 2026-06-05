@echo off
REM ============================================================
REM  Sistema de Convalidación UNIACC — Lanzador Windows
REM ============================================================

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo Python no encontrado. Instalalo desde https://www.python.org
    pause
    exit /b
)

echo Instalando dependencias...
pip install flask anthropic --quiet

echo.
echo Iniciando sistema...
echo Abre tu navegador en: http://localhost:5050
echo Configura tu API Key en la seccion Configuracion dentro de la app.
echo.
echo Presiona Ctrl+C para detener el servidor.
echo.

start "" "http://localhost:5050"
python app.py
