@echo off
setlocal

REM ============================================================
REM Step 3 — Generate public transport from GTFS (gtfs2pt.py)
REM ============================================================

echo ===============================================
echo   Generate public transport from GTFS (gtfs2pt)
echo ===============================================
echo Start time: %DATE% %TIME%
echo.

set "NET=cda_la_rochelle.net.xml"
set "GTFS=input\ca_la_rochelle-aggregated-gtfs.zip"
set "STOPS=busstop.add.xml"
set "GTFS_DATE=20260317"

if not exist "%NET%" (
  echo [ERROR] Network file not found: %NET%
  pause
  exit /b 1
)

if not exist "%GTFS%" (
  echo [ERROR] GTFS zip not found: %GTFS%
  pause
  exit /b 1
)

if not exist "%STOPS%" (
  echo [ERROR] Stops file not found: %STOPS%
  pause
  exit /b 1
)

REM ============================================================
REM IMPORTANT:
REM This step may take up to three hours depending on the network
REM and the size of the GTFS dataset.
REM
REM During execution, gtfs2pt.py may display no new command-line
REM output for a long time. This is normal and does not necessarily
REM mean that the program has crashed.
REM
REM Do not close this window unless an explicit error is displayed.
REM ============================================================

echo.
echo [INFO] The GTFS import is starting.
echo [INFO] This operation may take up to three hours.
echo [INFO] No additional command-line output may appear during processing.
echo [INFO] This is normal. Please do not close this window.
echo.

python gtfs2pt.py ^
  --network "%NET%" ^
  --gtfs "%GTFS%" ^
  --date %GTFS_DATE% ^
  --stops "%STOPS%"

if errorlevel 1 (
  echo.
  echo [ERROR] GTFS import failed.
  pause
  exit /b 1
)

echo.
echo End time: %DATE% %TIME%
echo [OK] GTFS import finished successfully.
pause