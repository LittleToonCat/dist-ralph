@echo off

rem Read the contents of PPYTHON_PATH into %PPYTHON_PATH%:
set /P PPYTHON_PATH=<PPYTHON_PATH

cd..

echo Starting game...

%PPYTHON_PATH% -m RalphClientRepository
pause
