@echo off
REM Creates (or repairs) the Support Fins desktop shortcut with the alien icon.
setlocal EnableExtensions
set "HERE=%~dp0"
set "APPDIR=%HERE:~0,-1%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop';" ^
 "$dest = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Support Fins.lnk';" ^
 "$sh = New-Object -ComObject WScript.Shell;" ^
 "$l = $sh.CreateShortcut($dest);" ^
 "$l.TargetPath = \"$env:ComSpec\";" ^
 "$l.Arguments = '/c \"\"%APPDIR%\Launch Support Fins.bat\"\"';" ^
 "$l.WorkingDirectory = '%APPDIR%';" ^
 "$l.IconLocation = '%APPDIR%\alien.ico,0';" ^
 "$l.Description = 'Support Fins - breakaway support fins baked into the STL';" ^
 "$l.WindowStyle = 7;" ^
 "$l.Save();" ^
 "if (-not (Test-Path $dest)) { Write-Host 'FAILED: shortcut was not written.'; exit 1 };" ^
 "Write-Host \"Created and verified: $dest\""
if errorlevel 1 exit /b 1
exit /b 0
