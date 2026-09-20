Write-Host "Iniciando compilacion con PyInstaller..."
pyinstaller --noconfirm SolidAdventureLegacy.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error en PyInstaller."
    exit $LASTEXITCODE
}
Write-Host "Copiando carpeta assets a dist/SolidAdventureLegacy..."
Copy-Item -Path assets -Destination dist\SolidAdventureLegacy\assets -Recurse -Force
Write-Host "Compilacion completada con exito."
