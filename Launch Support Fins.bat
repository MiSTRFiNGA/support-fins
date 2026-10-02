@echo off
REM Support Fins (HiVEMiND) launcher. Stdlib-only Python; no venv needed.
REM Picks pythonw so no console window stays open. ASCII only.
setlocal EnableExtensions
set "HERE=%~dp0"
if not exist "%HERE%_runtime" mkdir "%HERE%_runtime" 2>nul
set "PY="
set "PYARGS="
REM -3.14 explicitly: the py default can resolve to free-threaded 3.14t.
where pyw.exe >nul 2>nul && (set "PY=pyw.exe" & set "PYARGS=-3.14")
if defined PY (pyw.exe -3.14 -c "" >nul 2>nul || set "PYARGS=-3")
if not defined PY (where pythonw.exe >nul 2>nul && set "PY=pythonw.exe")
if not defined PY (
  mshta "javascript:new ActiveXObject('WScript.Shell').Popup('Support Fins could not start: no Python interpreter was found.',0,'Support Fins',16);close()"
  exit /b 1
)
cd /d "%HERE%"
start "Support Fins" /b "%PY%" %PYARGS% "%HERE%support_fins_app.py" %*
exit /b 0
