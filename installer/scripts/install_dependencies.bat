@echo off
echo ========================================
echo INSTALADOR DE DEPENDENCIAS PYTHON
echo Sistema de Constancias v2.0.0
echo ========================================

:: Configurar variables
set PYTHON_PATHS="%ProgramFiles%\Python312\python.exe" "%ProgramFiles(x86)%\Python312\python.exe" "%LocalAppData%\Programs\Python\Python312\python.exe" "python"
set REQUIREMENTS_FILE="%~dp0requirements.txt"
set LOG_FILE="%~dp0install_dependencies.log"

echo [%date% %time%] Iniciando instalacion de dependencias >> %LOG_FILE%

:: Buscar Python instalado
echo Buscando instalacion de Python...
set PYTHON_EXE=

for %%p in (%PYTHON_PATHS%) do (
    if exist %%p (
        echo Encontrado Python en: %%p
        set PYTHON_EXE=%%p
        goto :found_python
    )
)

:: Si no se encuentra Python, intentar desde PATH
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python encontrado en PATH
    set PYTHON_EXE=python
    goto :found_python
)

echo ERROR: No se pudo encontrar Python instalado
echo [%date% %time%] ERROR: Python no encontrado >> %LOG_FILE%
pause
exit /b 1

:found_python
echo Usando Python: %PYTHON_EXE%
echo [%date% %time%] Python encontrado: %PYTHON_EXE% >> %LOG_FILE%

:: Verificar pip
echo Verificando pip...
%PYTHON_EXE% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip no esta disponible
    echo [%date% %time%] ERROR: pip no disponible >> %LOG_FILE%
    pause
    exit /b 1
)

:: Actualizar pip
echo Actualizando pip...
%PYTHON_EXE% -m pip install --upgrade pip >> %LOG_FILE% 2>&1

:: Instalar dependencias
echo Instalando dependencias desde requirements.txt...
echo [%date% %time%] Instalando dependencias >> %LOG_FILE%

%PYTHON_EXE% -m pip install -r %REQUIREMENTS_FILE% >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Fallo la instalacion de dependencias
    echo [%date% %time%] ERROR: Fallo instalacion dependencias >> %LOG_FILE%
    echo.
    echo Intentando instalacion individual...
    
    :: Instalar dependencias críticas una por una
    echo Instalando PyQt5 (interfaz grafica)...
    %PYTHON_EXE% -m pip install PyQt5==5.15.10 >> %LOG_FILE% 2>&1

    echo Instalando Google Generative AI (IA)...
    %PYTHON_EXE% -m pip install google-generativeai >> %LOG_FILE% 2>&1

    echo Instalando python-dotenv (configuracion)...
    %PYTHON_EXE% -m pip install python-dotenv >> %LOG_FILE% 2>&1

    echo Instalando procesadores de PDF...
    %PYTHON_EXE% -m pip install pdfplumber==0.10.2 >> %LOG_FILE% 2>&1
    %PYTHON_EXE% -m pip install PyPDF2==3.0.1 >> %LOG_FILE% 2>&1
    %PYTHON_EXE% -m pip install reportlab >> %LOG_FILE% 2>&1

    echo Instalando procesamiento de imagenes...
    %PYTHON_EXE% -m pip install Pillow==10.0.0 >> %LOG_FILE% 2>&1

    echo Instalando plantillas y comunicacion...
    %PYTHON_EXE% -m pip install Jinja2==3.1.2 >> %LOG_FILE% 2>&1
    %PYTHON_EXE% -m pip install requests >> %LOG_FILE% 2>&1

    echo Instalando utilidades adicionales...
    %PYTHON_EXE% -m pip install PyMuPDF >> %LOG_FILE% 2>&1
    %PYTHON_EXE% -m pip install urllib3 >> %LOG_FILE% 2>&1
)

:: Verificar instalacion
echo Verificando instalacion...
echo [%date% %time%] Verificando instalacion >> %LOG_FILE%

%PYTHON_EXE% -c "import PyQt5; print('PyQt5: OK')" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo WARNING: PyQt5 no se instalo correctamente
    echo [%date% %time%] WARNING: PyQt5 fallo >> %LOG_FILE%
) else (
    echo PyQt5: Instalado correctamente
)

%PYTHON_EXE% -c "import google.generativeai; print('Gemini: OK')" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo WARNING: google-generativeai no se instalo correctamente
    echo [%date% %time%] WARNING: google-generativeai fallo >> %LOG_FILE%
) else (
    echo Google Generative AI: Instalado correctamente
)

echo Verificando procesadores de PDF...
%PYTHON_EXE% -c "import pdfplumber, PyPDF2; print('PDF: OK')" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Procesadores PDF no se instalaron correctamente
) else (
    echo Procesadores PDF: Instalados correctamente
)

echo Verificando python-dotenv...
%PYTHON_EXE% -c "import dotenv; print('dotenv: OK')" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo WARNING: python-dotenv no se instalo correctamente
) else (
    echo python-dotenv: Instalado correctamente
)

echo.
echo ========================================
echo INSTALACION COMPLETADA
echo ========================================
echo [%date% %time%] Instalacion completada >> %LOG_FILE%

:: Mostrar resumen
echo Resumen de instalacion:
echo - Python: %PYTHON_EXE%
echo - Log: %LOG_FILE%
echo.
echo El sistema esta listo para usar.
echo.

timeout /t 3 >nul
exit /b 0
