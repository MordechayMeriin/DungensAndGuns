@echo off
chcp 65001 >nul
cd /d "%~dp0"
title מבוך ונשק

rem --- מחפשים את Python במחשב ---
set "PY=python"
%PY% --version >nul 2>&1
if not errorlevel 1 goto FOUND

set "PY=py -3"
%PY% --version >nul 2>&1
if not errorlevel 1 goto FOUND

echo.
echo לא נמצא Python במחשב הזה.
echo צריך להתקין אותו מהכתובת:  https://www.python.org/downloads/
echo חשוב! בזמן ההתקנה לסמן V ליד "Add python.exe to PATH".
echo.
pause
exit /b 1

:FOUND
rem --- בודקים שהספרייה של המשחק מותקנת, ואם לא - מתקינים ---
%PY% -c "import pygame, pydantic" >nul 2>&1
if not errorlevel 1 goto RUN

echo.
echo פעם ראשונה כאן - מתקין את מה שהמשחק צריך. זה לוקח דקה, רק בפעם הראשונה...
echo.
%PY% -m pip install -r requirements.txt
if not errorlevel 1 goto RUN

echo.
echo ההתקנה נכשלה. כדאי לבדוק שיש חיבור לאינטרנט ולנסות שוב.
echo.
pause
exit /b 1

:RUN
%PY% game.py
if errorlevel 1 pause
