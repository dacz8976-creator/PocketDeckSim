# Gemini side-by-side check, one Codex batch: for each Codex packet in the evidence folder, copy the recording into WSL, run the two
# Gemini passes (run.sh), cut 1-fps full-resolution frames for the scorer, build the scorer's folder, then remove the big copy.
# usage: powershell -File gcheck.ps1 -Evidence <DRIVE_LADDER_ folder> -Out <scoring root on C:>
param([Parameter(Mandatory = $true)][string]$Evidence, [Parameter(Mandatory = $true)][string]$Out)
$w = '\\wsl$\Ubuntu\home\dacz8976\gemini_ladder'
$wslOut = '/mnt/c' + ($Out.Substring(2) -replace '\\', '/')
New-Item -ItemType Directory -Force "$w\src", $Out | Out-Null
$map = @()
foreach ($d in Get-ChildItem -LiteralPath $Evidence -Directory) {
  $j = Get-Content -LiteralPath (Join-Path $d.FullName 'SOURCE.json') -Raw | ConvertFrom-Json
  # Codex's SOURCE.json shapes vary by reviewer: filename/recording/video_basename, local_cache_path/physical_cache_path
  $name = $j.filename; if (-not $name) { $name = $j.recording }; if (-not $name) { $name = $j.video_basename }
  $cache = $j.local_cache_path; if (-not $cache) { $cache = $j.physical_cache_path }
  if (-not $name) { Write-Output "$($d.Name): no recording name in SOURCE.json, skipped"; continue }
  $map += [pscustomobject]@{ packet = $d.FullName; name = $name; cache = $cache; seconds = $j.duration_seconds }
}
$map | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $Out 'map.json')
foreach ($m in $map) {
  $key = $m.name -replace '\.mp4$', ''
  $S = Join-Path $Out $key
  if (Test-Path -LiteralPath (Join-Path $S 'score\SCORE.md')) { Write-Output "${key}: already prepared"; continue }
  $src = $m.cache
  if (-not ($src -and (Test-Path -LiteralPath $src -PathType Leaf))) { $src = "G:\My Drive\Battle Logs\Reviewed\$($m.name)" }
  if (-not (Test-Path -LiteralPath $src -PathType Leaf)) { Write-Output "${key}: video not found"; continue }
  Copy-Item -LiteralPath $src "$w\src\$($m.name)" -Force
  wsl bash -lc "bash ~/gemini_ladder/run.sh '$($m.name)' && bash ~/gemini_ladder/frames.sh '$($m.name)' '$wslOut/$key/frames'"
  Remove-Item -LiteralPath "$w\src\$($m.name)" -Force
  # the scorer's folder: Gemini's full review, Gemini's cheap sheet, Codex's packet text files, placeholders
  $G = "$w\games\$key"
  New-Item -ItemType Directory -Force "$S\gemini", "$S\gemini_cheap", "$S\codex", "$S\score" | Out-Null
  foreach ($f in 'REVIEW.md', 'OPPONENT.json', 'UNCERTAINTIES.md') { Copy-Item -LiteralPath "$G\review_high\$f" "$S\gemini\$f" -Force }
  Copy-Item -LiteralPath "$G\review_default\OPPONENT.json" "$S\gemini_cheap\OPPONENT.json" -Force
  Get-ChildItem -LiteralPath $m.packet -Recurse -File | Where-Object { $_.Extension -in '.md', '.json' } | ForEach-Object {
    $rel = $_.FullName.Substring($m.packet.Length + 1); $dst = Join-Path "$S\codex" $rel
    New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null; Copy-Item -LiteralPath $_.FullName $dst -Force }
  foreach ($f in 'SCORE.md', 'score.json') { Set-Content -LiteralPath "$S\score\$f" -Value 'PLACEHOLDER' }
  Write-Output "${key}: prepared ($((Get-ChildItem -LiteralPath "$S\frames").Count) frames)"
}
