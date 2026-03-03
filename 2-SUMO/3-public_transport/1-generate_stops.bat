@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM Build SUMO network and generate PT stops (netconvert)
REM ============================================================

echo === Building SUMO network + PT stops ===

set "OSM_FILE=..\1-network\cda_la_rochelle.osm"
set "NET_OUT=cda_la_rochelle.net.xml"
set "PTSTOPS_OUT=busstop.add.xml"

if not exist "%OSM_FILE%" (
  echo [ERROR] OSM input file not found: %OSM_FILE%
  pause
  exit /b 1
)

netconvert ^
  --osm-files "%OSM_FILE%" ^
  -o "%NET_OUT%" ^
  --osm.stop-output.length 20 ^
  --ptstop-output "%PTSTOPS_OUT%"

if errorlevel 1 (
  echo [ERROR] netconvert failed.
  pause
  exit /b 1
)

echo [OK] Done.
echo [OK] Network: %NET_OUT%
echo [OK] PT stops: %PTSTOPS_OUT%
pause