@echo off
title ChainKYC - Make Portable ZIP
color 0E

echo.
echo  ===============================================
echo   ChainKYC - Creating Portable ZIP
echo  ===============================================
echo.
echo  This will create ChainKYC_Portable.zip
echo  excluding: node_modules, .env, cache, artifacts
echo.

REM Get timestamp for unique filename
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "ZIPNAME=ChainKYC_Portable_%DD%%MM%%YY%.zip"

echo  Output: ..\%ZIPNAME%
echo.

REM Use PowerShell to create zip excluding large/sensitive files
powershell -NoProfile -Command ^
    "$source = '%~dp0'; " ^
    "$dest = Join-Path (Split-Path $source) '%ZIPNAME%'; " ^
    "$tempDir = Join-Path $env:TEMP 'chainkyc_zip_temp'; " ^
    "if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }; " ^
    "New-Item $tempDir -ItemType Directory -Force | Out-Null; " ^
    "$exclude = @('node_modules', '.env', 'cache', 'artifacts', '*.zip', 'chainkyc_zip_temp'); " ^
    "Get-ChildItem $source -Recurse | Where-Object { " ^
    "  $path = $_.FullName; " ^
    "  $skip = $false; " ^
    "  foreach ($e in $exclude) { if ($path -like \"*\$e*\") { $skip = $true; break } }; " ^
    "  -not $skip " ^
    "} | ForEach-Object { " ^
    "  $rel = $_.FullName.Substring($source.Length); " ^
    "  $target = Join-Path $tempDir $rel; " ^
    "  if ($_.PSIsContainer) { New-Item $target -ItemType Directory -Force | Out-Null } " ^
    "  else { $parent = Split-Path $target; if (!(Test-Path $parent)) { New-Item $parent -ItemType Directory -Force | Out-Null }; Copy-Item $_.FullName $target } " ^
    "}; " ^
    "if (Test-Path $dest) { Remove-Item $dest -Force }; " ^
    "Compress-Archive -Path (Join-Path $tempDir '*') -DestinationPath $dest -Force; " ^
    "Remove-Item $tempDir -Recurse -Force; " ^
    "Write-Host ''; " ^
    "Write-Host \"  Created: $dest\" -ForegroundColor Green; " ^
    "Write-Host \"  Size: $([math]::Round((Get-Item $dest).Length / 1KB, 1)) KB\" -ForegroundColor Green"

echo.
echo  ===============================================
echo   ZIP created! Copy it to USB / share it.
echo   On the target PC, extract and run START.bat
echo  ===============================================
echo.
pause
