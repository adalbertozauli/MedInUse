param(
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

$Python = ".\.venv\Scripts\python.exe"
$RuntimeName = "MedInUseRuntime"
$PayloadDir = ".\build\installer_payload"

if (-not (Test-Path $Python)) {
    Write-Host "Criando ambiente Python local..."
    python -m venv .venv
}

Write-Host "Instalando dependencias..."
& $Python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Falha ao atualizar pip." }
& $Python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar dependencias." }

Write-Host "Gerando aplicativo principal..."
& $Python -m PyInstaller --noconfirm --clean --onefile --windowed --name $RuntimeName .\main.py
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar aplicativo principal." }

New-Item -ItemType Directory -Force $PayloadDir | Out-Null
Copy-Item ".\dist\$RuntimeName.exe" "$PayloadDir\MedInUse.exe" -Force

try {
    Copy-Item "$PayloadDir\MedInUse.exe" ".\dist\MedInUse.exe" -Force
} catch {
    Write-Host "Nao foi possivel atualizar dist\MedInUse.exe porque o arquivo esta em uso. O instalador usara a versao recem-gerada."
}

Write-Host "Gerando instalador..."
& $Python -m PyInstaller --noconfirm --clean --onefile --windowed --name MedInUseSetup --add-data "$PayloadDir\MedInUse.exe;." .\installer\medinuse_installer.py
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar instalador." }

New-Item -ItemType Directory -Force release | Out-Null
$ReleasePath = ".\release\MedInUseSetup-v$Version.exe"
Copy-Item .\dist\MedInUseSetup.exe $ReleasePath -Force

Write-Host "Instalador pronto em $ReleasePath"
