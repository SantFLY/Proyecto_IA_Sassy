@echo off
:: Script para iniciar Sassy en modo consola como administrador desde la raíz

set SCRIPT_PATH=%~dp0main_consola.py

echo === DEPURACIÓN SASSY CONSOLA ===
echo Ruta del script: %SCRIPT_PATH%
echo.

:: Ejecutar como administrador y mantener la consola abierta
powershell -Command "Start-Process cmd -ArgumentList '/k python \"%SCRIPT_PATH%\"' -Verb RunAs"

echo.
echo Si ves algún error arriba, revisa la ruta y permisos.
pause 