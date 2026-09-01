$sourceRoot = "C:\Users\igorm\Downloads\Mods Container Analisar\01_Extracted_ZIP"
$destinationRoot = "C:\VVRefs\LSLib"
$divinePath = "C:\Tools\BG3\LSLib\Packed\Tools\Divine.exe"

if (-not (Test-Path $divinePath)) {
    throw "Divine.exe não encontrado em: $divinePath"
}

if (-not (Test-Path $sourceRoot)) {
    throw "Pasta de origem não encontrada: $sourceRoot"
}

New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null

$paks = Get-ChildItem `
    -Path $sourceRoot `
    -Filter "*.pak" `
    -File `
    -Recurse |
    Sort-Object FullName

Write-Host "[INFO] PAKs encontrados: $($paks.Count)"

$index = 1

foreach ($pak in $paks) {

    $shortId = "{0:D3}_{1}" -f $index, $pak.BaseName

    # Limita também o nome do PAK caso ele próprio seja enorme
    if ($shortId.Length -gt 70) {
        $shortId = $shortId.Substring(0, 70)
    }

    $destinationPath = Join-Path $destinationRoot $shortId
    $markerPath = Join-Path $destinationPath ".extracted.ok"

    if (Test-Path $markerPath) {
        Write-Host "[SKIP] Já extraído: $($pak.Name)"
        $index++
        continue
    }

    if (Test-Path $destinationPath) {

        $existingFiles = Get-ChildItem `
            -Path $destinationPath `
            -Force `
            -ErrorAction SilentlyContinue

        if ($existingFiles.Count -gt 0) {
            Write-Host "[WARN] Destino contém arquivos sem marcador: $destinationPath"
            $index++
            continue
        }
    }
    else {
        New-Item `
            -ItemType Directory `
            -Path $destinationPath `
            -Force |
            Out-Null
    }

    try {
        Write-Host "[EXTRACT] $($pak.Name)"
        Write-Host "          -> $shortId"

        & $divinePath `
            --game bg3 `
            --action extract-package `
            --source $pak.FullName `
            --destination $destinationPath

        if ($LASTEXITCODE -ne 0) {
            throw "Divine.exe terminou com código $LASTEXITCODE"
        }

        $realFiles = Get-ChildItem `
            -Path $destinationPath `
            -File `
            -Recurse `
            -ErrorAction SilentlyContinue

        if ($realFiles.Count -eq 0) {
            throw "Divine terminou sem erro, mas nenhum arquivo foi extraído."
        }

        Set-Content `
            -Path $markerPath `
            -Value @"
PAK: $($pak.Name)
Source: $($pak.FullName)
Extracted: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Files: $($realFiles.Count)
"@

        Write-Host "[OK] Extraído: $($pak.Name) [$($realFiles.Count) arquivos]"
    }
    catch {
        Write-Host "[ERRO] Falha ao extrair: $($pak.Name)"
        Write-Host "       $($_.Exception.Message)"
    }

    $index++
}