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
set "DATE=20251124"

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

python gtfs2pt.py ^
  --network "%NET%" ^
  --gtfs "%GTFS%" ^
  --date %DATE% ^
  --stops "%STOPS%"

if errorlevel 1 (
  echo [ERROR] GTFS import failed.
  pause
  exit /b 1
)

echo.
echo End time: %DATE% %TIME%
echo [OK] Finished.
pause