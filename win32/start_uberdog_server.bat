@echo off

set STATE_SERVER=402000
set ASTRON_IP=127.0.0.1:7190
set BASE_CHANNEL=1000000

rem Read the contents of PPYTHON_PATH into %PPYTHON_PATH%:
set /P PPYTHON_PATH=<PPYTHON_PATH

cd..

echo Starting UberDOG server...

%PPYTHON_PATH% -m RalphUDRepository --base-channel %BASE_CHANNEL% --stateserver %STATE_SERVER% --astron-ip %ASTRON_IP%

pause
