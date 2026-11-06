@echo off
chcp 65001 >nul
title KALLPA - Descargar videos
set "DESTINO=D:\KALLPA\Videos"
set "BASE=https://kallpa.iamasterperu.workers.dev/redes"
echo.
echo  Descargando los videos de KALLPA en %DESTINO% ...
echo.
if not exist "%DESTINO%" mkdir "%DESTINO%"
for %%F in (Video1_KALLPA.mp4 Video1_portada.jpg Video1_para_TikTok.txt Video1_subtitulos.srt Video1_voz.mp3) do (
  echo  - %%F
  curl.exe -s -f -L -o "%DESTINO%\%%F" "%BASE%/%%F"
  if errorlevel 1 echo    No se pudo descargar %%F
)
echo.
echo  Listo. Se abrira la carpeta.
start "" "%DESTINO%"
pause
