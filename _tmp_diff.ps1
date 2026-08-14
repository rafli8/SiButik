$root = 'd:\Riset MBKM\model results'
$src = Join-Path $root 'Batik_Re-Palette\showcase\images'
$dst = Join-Path $root 'hf_space\showcase\images'
Get-ChildItem $src -File | ForEach-Object {
    $h1 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    $h2 = (Get-FileHash (Join-Path $dst $_.Name) -Algorithm SHA256 -ErrorAction SilentlyContinue).Hash
    if ($h1 -ne $h2) {
        [PSCustomObject]@{ Name = $_.Name; Local = $h1.Substring(0,12); HF = $h2.Substring(0,12); Size = $_.Length }
    }
} | Format-Table -AutoSize