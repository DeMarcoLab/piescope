:: Show each command and output
@echo on

:: Config for Basler Pylon software suite
:: https://www.baslerweb.com/en/sales-support/downloads/software-downloads/
set "PYLON_VERSION=5.2.0.13457"
set "PYLON_MD5=91f40fb37acfb474a19e6ca6f745650b"
set "PYLON_INSTALLER=Basler_pylon_%PYLON_VERSION%.exe"
set "PYLON_URL=https://www.baslerweb.com/fp-1551786641/media/downloads/software/pylon_software/Basler_pylon_%PYLON_VERSION%.exe"

:: Install the Basler Pylon software
:: Download
powershell -Command "(New-Object Net.WebClient).DownloadFile('%PYLON_URL%', '%PYLON_INSTALLER%')"
if errorlevel 1 exit 1
:: Check file hash
( certutil -hashfile "%PYLON_INSTALLER%" md5 | findstr /v ":" ) > "%PYLON_INSTALLER%.md5"
if errorlevel 1 exit 1
type "%PYLON_INSTALLER%.md5"
if errorlevel 1 exit 1
set /p PYLON_MD5_FOUND=<%PYLON_INSTALLER%.md5
if errorlevel 1 exit 1
set "PYLON_MD5_FOUND=%PYLON_MD5_FOUND: =%"
if errorlevel 1 exit 1
echo "%PYLON_MD5_FOUND%" | findstr /c:"%PYLON_MD5%"
if errorlevel 1 exit 1
:: Install
%PYLON_INSTALLER% /s
if errorlevel 1 exit 1
:: Clean up
del "%PYLON_INSTALLER%"
if errorlevel 1 exit 1
del "%PYLON_INSTALLER%.md5"
if errorlevel 1 exit 1


:: Python pypylon library (installed after the pylon software suite)
:: https://github.com/basler/pypylon/releases
set "PYPYLON_VERSION=1.4.0"
set "ARCH=win32"
set "PYPYLON_WHEEL=\pypylon-%PYPYLON_VERSION%-cp%PYVER%-cp%PYVER%m-%ARCH%.whl"
set "PYPYLON_URL=https://github.com/basler/pypylon/releases/download/%PYPYLON_VERSION%/pypylon-%PYPYLON_VERSION%-cp%PYVER%-cp%PYVER%m-%ARCH%.whl"

:: Install the python pypylon package
:: Download
powershell -Command "(New-Object Net.WebClient).DownloadFile('%PYPYLON_URL%', '%PYPYLON_WHEEL%')"
if errorlevel 1 exit 1
:: Check file hash
( certutil -hashfile "%PYPYLON_WHEEL%" md5 | findstr /v ":" ) > "%PYPYLON_WHEEL%.md5"
if errorlevel 1 exit 1
type "%PYPYLON_WHEEL%.md5"
if errorlevel 1 exit 1
set /p PYPYLON_WHEEL_MD5_FOUND=<%PYPYLON_WHEEL%.md5
if errorlevel 1 exit 1
set "PYPYLON_WHEEL_MD5_FOUND=%PYPYLON_WHEEL_MD5_FOUND: =%"
if errorlevel 1 exit 1
echo "%PYPYLON_WHEEL_MD5_FOUND%" | findstr /c:"%PYPYLON_WHEEL_MD5%"
if errorlevel 1 exit 1
:: Install
pip install %PYPYLON_WHEEL%
if errorlevel 1 exit 1
:: Clean up
del "%PYPYLON_WHEEL%"
if errorlevel 1 exit 1
del "pypylon_wheel.md5"
if errorlevel 1 exit 1
