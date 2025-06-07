@echo off
title Sistema de Constancias - Escuela
cd /d "%~dp0"

:: Buscar Python instalado
set PYTHON_PATHS="%ProgramFiles%\Python312\python.exe" "%ProgramFiles(x86)%\Python312\python.exe" "%LocalAppData%\Programs\Python\Python312\python.exe" "python"
set PYTHON_EXE=

for %%p in (%PYTHON_PATHS%) do (
    if exist %%p (
        set PYTHON_EXE=%%p
        goto :found_python
    )
)

:: Si no se encuentra Python, intentar desde PATH
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_EXE=python
    goto :found_python
)

echo ERROR: No se pudo encontrar Python instalado
echo.
echo Por favor, ejecute install_dependencies.bat primero
echo o reinstale el sistema.
echo.
pause
exit /b 1

:found_python
:: Verificar dependencias críticas
%PYTHON_EXE% -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PyQt5 no esta instalado
    echo.
    echo Ejecutando instalador de dependencias...
    call install_dependencies.bat
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

:: Ejecutar aplicación
%PYTHON_EXE% simple_launcher.py %*
if errorlevel 1 (
    echo.
    echo Error ejecutando la aplicacion.
    echo.
    echo Verifique el archivo install_dependencies.log para mas detalles.
    echo Presiona cualquier tecla para continuar...
    pause >nul
)
