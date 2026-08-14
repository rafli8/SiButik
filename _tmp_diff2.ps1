$root = 'd:\Riset MBKM\model results'
$src = Join-Path $root 'Batik_Re-Palette\showcase\images'
$dst = Join-Path $root 'hf_space\showcase\images'
$diffs = @()
Get-ChildItem $src -File | ForEach-Object {
    $name = $_.Name
    $size1 = $_.Length
    $other = Join-Path $dst $name
    if (Test-Path $other) {
        $size2 = (Get-Item $other).Length
        if ($size1 -ne $size2) {
            $diffs += [PSCustomObject]@{ Name = $name; LocalSize = $size1; HFSize = $size2 }
        }
    } else {
        $diffs += [PSCustomObject]@{ Name = $name; LocalSize = $size1; HFSize = 'MISSING' }
    }
}
if ($diffs.Count -eq 0) {
    Write-Host "All files have identical sizes between Batik_Re-Palette and hf_space showcase/images"
} else {
    $diffs | Format-Table -AutoSize
}
