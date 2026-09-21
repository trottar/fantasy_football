@echo off
setlocal EnableExtensions
set "RUNNER=%~dp0run_package.py"
if not exist "%RUNNER%" (
  echo FFPKG WRAPPER FAIL
  echo Missing runner: "%RUNNER%"
  exit /b 2
)
python "%RUNNER%" %*
set "RC=%ERRORLEVEL%"
exit /b %RC%
