@echo off
setlocal EnableDelayedExpansion
title Pystart
cd /d "%~dp0"

rem =============================================================
rem  Lanceur portable de Pystart (sans installeur, sans droits
rem  administrateur, aucun executable compile a lancer).
rem
rem  Ce script :
rem    1. cherche un Python 3.10+ deja installe sur la machine ;
rem    2. cree un environnement virtuel local (dossier
rem       .pystart-venv, a cote de ce fichier) s'il n'existe pas ;
rem    3. installe les dependances de Pystart dans cet
rem       environnement (une seule fois) ;
rem    4. lance Pystart.
rem
rem  Rien n'est ecrit en dehors de ce dossier et de
rem  %%APPDATA%%\Pystart (donnees utilisateur). Aucune elevation
rem  de droits n'est demandee.
rem =============================================================

echo.
echo   Pystart - lancement
echo   --------------------
echo.

rem --- 1. Chercher un interpreteur Python 3.10 ou plus recent ---
set "PYEXE="

where py >nul 2>&1
if not errorlevel 1 (
    for /f "usebackq delims=" %%v in (`py -3 -c "import sys;print(sys.version_info>=(3,10))" 2^>nul`) do set "OK=%%v"
    if "!OK!"=="True" set "PYEXE=py -3"
)

if not defined PYEXE (
    where python >nul 2>&1
    if not errorlevel 1 (
        set "OK="
        for /f "usebackq delims=" %%v in (`python -c "import sys;print(sys.version_info>=(3,10))" 2^>nul`) do set "OK=%%v"
        if "!OK!"=="True" set "PYEXE=python"
    )
)

if not defined PYEXE (
    echo   Python 3.10 ou plus recent est necessaire mais n'a pas ete trouve.
    echo.
    echo   1. Va sur https://www.python.org/downloads/
    echo   2. Installe Python ^(coche bien "Add python.exe to PATH"^)
    echo   3. Relance ce fichier Pystart.bat
    echo.
    start "" https://www.python.org/downloads/
    pause
    exit /b 1
)

echo   Python trouve : !PYEXE!

rem --- 2. Environnement virtuel local (isole, sans droits admin) ---
set "VENV_DIR=%~dp0.pystart-venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo   Premier lancement : preparation de l'environnement...
    !PYEXE! -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo   Impossible de creer l'environnement virtuel dans :
        echo     %VENV_DIR%
        pause
        exit /b 1
    )
)

rem --- 3. Dependances (installees une seule fois) ---
"%VENV_PY%" -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo   Installation des dependances ^(premier lancement seulement,
    echo   environ 1 a 2 minutes, connexion Internet necessaire^)...
    "%VENV_PY%" -m pip install --quiet --upgrade pip
    if errorlevel 1 goto :pip_error
    "%VENV_PY%" -m pip install --quiet -r "%~dp0requirements.txt"
    if errorlevel 1 goto :pip_error
    echo   Dependances installees.
)

rem --- 4. Lancement de Pystart ---
echo.
echo   Demarrage de Pystart...
echo.
"%VENV_PY%" -m app
if errorlevel 1 (
    echo.
    echo   Pystart s'est arrete avec une erreur ^(voir ci-dessus^).
    pause
)
endlocal
exit /b 0

:pip_error
echo.
echo   Echec de l'installation des dependances. Verifie ta connexion
echo   Internet puis relance ce fichier.
pause
endlocal
exit /b 1
