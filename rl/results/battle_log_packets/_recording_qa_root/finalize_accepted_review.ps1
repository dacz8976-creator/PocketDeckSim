param([Parameter(Mandatory=$true)][string]$Video,[Parameter(Mandatory=$true)][string]$Packet)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if ([IO.Path]::GetFileName($Video) -ne $Video) { throw 'Video must be a basename' }
$source = [IO.Path]::GetFullPath((Join-Path $root $Video))
$destination = [IO.Path]::GetFullPath((Join-Path $root ('Reviewed/' + $Video)))
$packetPath = [IO.Path]::GetFullPath((Join-Path $root $Packet))
if (!( $source.StartsWith($root + '\') -and $destination.StartsWith($root + '\Reviewed\') -and $packetPath.StartsWith($root + '\Recording_QA\'))) { throw 'Path outside expected workspace' }
if (Test-Path -LiteralPath $destination) { throw 'Destination collision' }
$acceptance = Get-Content -LiteralPath (Join-Path $packetPath 'LEAD_ACCEPTANCE.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($acceptance.accepted -ne $true -and $acceptance.decision -ne 'accepted_full_battle_review') { throw 'Lead acceptance required' }
$binding = Get-Content -LiteralPath (Join-Path $packetPath 'SOURCE.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$boundHash = if ($binding.sha256) { $binding.sha256 } else { $binding.source_sha256 }
$relatedPath = Join-Path $packetPath 'RELATED_GAME_PACKETS.json'
if (Test-Path -LiteralPath $relatedPath) {
    $related = Get-Content -LiteralPath $relatedPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($acceptance.all_source_games_accepted -ne $true -or $acceptance.source_game_count -ne $related.game_count) { throw 'Every recorded game must be accepted before source archival' }
    foreach ($gamePacket in $related.game_packets) {
        $gamePath = [IO.Path]::GetFullPath((Join-Path $packetPath $gamePacket.path))
        if ($gamePath -ne $packetPath -and !$gamePath.StartsWith($packetPath + '\')) { throw 'Game packet outside source folder' }
        $gameAcceptance = Get-Content -LiteralPath (Join-Path $gamePath 'LEAD_ACCEPTANCE.json') -Raw -Encoding UTF8 | ConvertFrom-Json
        $gameRegistration = Get-Content -LiteralPath (Join-Path $gamePath 'REGISTRATION_RESULT.json') -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($gameAcceptance.accepted -ne $true -or $gameAcceptance.source_sha256 -ne $boundHash -or $gameRegistration.exit_code -ne 0) { throw 'Multi-game source has an unfinished game' }
    }
}
$before = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
if ($before -ne $boundHash) { throw 'Source binding hash mismatch' }
$events = @(Get-ChildItem -LiteralPath (Join-Path $root 'Review_Log/events') -Filter '*.json' | ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json } | Where-Object video_basename -eq $Video | Sort-Object logged_at_utc)
if (!$events.Count) { throw 'No review event' }
$latest = $events[-1]
if ($latest.status -notin @('full_battle_review_complete','rule_test_review_complete') -or $latest.video_sha256 -ne $before) { throw 'Verified completion event required' }
$lockPath = Join-Path $root 'Review_Log/.write.lock'
$null = New-Item -ItemType Directory -Path $lockPath -ErrorAction Stop
try {
    @{pid=$PID;purpose='accepted review move and current index update'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $lockPath 'owner.json') -Encoding utf8
    $rows = @(Import-Csv -LiteralPath (Join-Path $root 'BATTLE_REVIEW_INDEX.csv'))
    $row = @($rows | Where-Object Video -eq $Video)
    if ($row.Count -ne 1 -or $row[0].Status -ne 'Reviewed') { throw 'One completed index row required' }
    $size = (Get-Item -LiteralPath $source).Length
    Move-Item -LiteralPath $source -Destination $destination
    $after = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($after -ne $before) { throw 'Post-move hash mismatch' }
    $utc = [DateTime]::UtcNow.ToString('o')
    $receiptPath = Join-Path $packetPath ('MOVE_RECEIPT.' + $Video + '.json')
    @{schema='battle-media-move-receipt/v1';filename=$Video;from=$source;to=$destination;bytes=$size;sha256_before=$before;sha256_after=$after;identity_match=$true;moved_utc=$utc;review_event_id=$latest.event_id;review_status=$latest.status;evidence_packet=$packetPath} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8
    $row[0].Location = 'Reviewed/' + $Video
    $rows | Export-Csv -LiteralPath (Join-Path $root 'BATTLE_REVIEW_INDEX.csv') -NoTypeInformation -Encoding utf8BOM
    $mapPath = Join-Path $root 'MEDIA_LOCATIONS.json'
    $map = Get-Content -LiteralPath $mapPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $evidence = @('REVIEW.md','COVERAGE.md','LEAD_ACCEPTANCE.json' | ForEach-Object { Join-Path $packetPath $_ })
    $entry = [pscustomobject]@{filename=$Video;old_path=$source;current_path=$destination;bytes=$size;sha256=$after;review_evidence=$evidence;location_history=@(@{from=$source;to=$destination;utc=$utc;reason=('Completed source review accepted by lead: ' + $latest.status);receipt=$receiptPath});review_status='Reviewed'}
    $map.moved = @($map.moved | Where-Object filename -ne $Video) + @($entry)
    $map.index_video_count = $rows.Count
    $map.awaiting_review_or_confirmation = @($rows | Where-Object Status -ne 'Reviewed').Count
    $map.updated_utc = $utc
    $map | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath $mapPath -Encoding utf8
    Write-Output "Verified move: $Video ($after)"
} finally {
    $ownLockRecord = Join-Path $lockPath 'owner.json'
    if (Test-Path -LiteralPath $ownLockRecord) {
        $ownLockItem = Get-Item -LiteralPath $ownLockRecord -Force
        $ownLockItem.Attributes = $ownLockItem.Attributes -band (-bnot [IO.FileAttributes]::ReadOnly)
        Remove-Item -LiteralPath $ownLockRecord -ErrorAction SilentlyContinue
    }
    # OneDrive can add ReadOnly to this transient directory. Remove only our empty lock.
    if ((Test-Path -LiteralPath $lockPath) -and @(Get-ChildItem -LiteralPath $lockPath -Force).Count -eq 0) {
        $ownLockDirectory = Get-Item -LiteralPath $lockPath -Force
        $ownLockDirectory.Attributes = $ownLockDirectory.Attributes -band (-bnot [IO.FileAttributes]::ReadOnly)
        Remove-Item -LiteralPath $lockPath -ErrorAction SilentlyContinue
    }
}
$storagePython = 'C:\Users\dacz8\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$storageHelper = Join-Path $PSScriptRoot 'free_reviewed_video_space.py'
if ((Test-Path -LiteralPath $storagePython) -and (Test-Path -LiteralPath $storageHelper)) {
    & $storagePython $storageHelper --video $Video --apply --wait-seconds 5
    if ($LASTEXITCODE -ne 0) { Write-Warning 'Review and archive completed, but OneDrive storage preference needs follow-up.' }
} else {
    Write-Warning 'Review and archive completed. Use OneDrive Free up space after sync; storage helper unavailable.'
}
