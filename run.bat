@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%img_to_iso.py"

where py >nul 2>&1
if not errorlevel 1 (
  py -3 "%PY_SCRIPT%" %*
  exit /b !ERRORLEVEL!
)

where python >nul 2>&1
if not errorlevel 1 (
  python "%PY_SCRIPT%" %*
  exit /b !ERRORLEVEL!
)

echo Python 3 not found. Attempting install via winget...
where winget >nul 2>&1
if errorlevel 1 (
  echo Error: winget not available. Install Python 3 from https://www.python.org/downloads/ then re-run.
  exit /b 1
)

winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
  echo Error: failed to install Python via winget.
  exit /b 1
)

rem Refresh PATH for this session from Machine + User
for /f "usebackq tokens=2*" %%A in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul`) do set "MACHINE_PATH=%%B"
for /f "usebackq tokens=2*" %%A in (`reg query "HKCU\Environment" /v Path 2^>nul`) do set "USER_PATH=%%B"
set "PATH=!MACHINE_PATH!;!USER_PATH!;!PATH!"

where py >nul 2>&1
if not errorlevel 1 (
  py -3 "%PY_SCRIPT%" %*
  exit /b !ERRORLEVEL!
)

where python >nul 2>&1
if not errorlevel 1 (
  python "%PY_SCRIPT%" %*
  exit /b !ERRORLEVEL!
)

echo Error: Python was installed but is not on PATH yet. Open a new terminal and re-run.
exit /b 1
