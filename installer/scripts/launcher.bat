@echo off
cd /d "%~dp0"
python simple_launcher.py %*
if errorlevel 1 (
    echo.
    echo Error ejecutando la aplicacion. Presiona cualquier tecla para continuar...
    pause >nul
)
