@echo off
echo ========================================
echo    Instalador Quinta-Feira
echo ========================================
echo.

echo Verificando Python...
python --version
if errorlevel 1 (
    echo Python nao encontrado! Baixe em: https://www.python.org/downloads/
    pause
    exit /b
)

echo.
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo ========================================
echo    Instalacao concluida!
echo ========================================
echo.
echo Para executar: python Main.py
echo.
pause
