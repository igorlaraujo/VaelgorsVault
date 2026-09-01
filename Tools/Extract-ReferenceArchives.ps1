$sourcePath = "C:\Users\igorm\Downloads\Mods Container Analisar\00_Originals"
$destinationRoot = "C:\Users\igorm\Downloads\Mods Container Analisar\01_Extracted_ZIP"

New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null

$archives = Get-ChildItem -Path $sourcePath -File |
    Where-Object { $_.Extension.ToLower() -in ".zip", ".7z", ".rar" }

foreach ($archive in $archives) {

    $folderName = $archive.BaseName
    $destinationPath = Join-Path $destinationRoot $folderName
    $markerPath = Join-Path $destinationPath ".extracted.ok"

    # Já foi extraído com sucesso anteriormente
    if (Test-Path $markerPath) {
        Write-Host "[SKIP] Já extraído: $folderName"
        continue
    }

    # Cria a pasta se ainda não existir
    if (-not (Test-Path $destinationPath)) {
        New-Item -ItemType Directory -Path $destinationPath | Out-Null
    }

    # Segurança: não mexer em pasta que já tenha conteúdo inesperado
    $existingFiles = Get-ChildItem -Path $destinationPath -Force

    if ($existingFiles.Count -gt 0) {
        Write-Host "[WARN] Pasta contém arquivos mas não possui marcador: $folderName"
        continue
    }

    try {
        Write-Host "[EXTRACT] $($archive.Name)"

        if ($archive.Extension.ToLower() -eq ".zip") {

            Expand-Archive `
                -LiteralPath $archive.FullName `
                -DestinationPath $destinationPath `
                -ErrorAction Stop
        }

        elseif ($archive.Extension.ToLower() -in ".7z", ".rar") {

            & tar.exe -xf $archive.FullName -C $destinationPath

            if ($LASTEXITCODE -ne 0) {
                throw "tar.exe terminou com código $LASTEXITCODE"
            }
        }

        # Só cria o marcador se a extração terminou com sucesso
        Set-Content `
            -Path $markerPath `
            -Value "Archive: $($archive.Name)`nExtracted: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

        Write-Host "[OK] Extraído: $folderName"
    }
    catch {
        Write-Host "[ERRO] Falha ao extrair: $folderName"
        Write-Host "       $($_.Exception.Message)"
    }
}