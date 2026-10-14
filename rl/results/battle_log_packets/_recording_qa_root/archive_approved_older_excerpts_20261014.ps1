$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$taskBatch = Join-Path $taskRoot 'Recording_QA/BATCH_2026-10-14_OLDER_FOUR'
$taskApprovalPath = Join-Path $taskBatch 'OWNER_EXCERPT_ARCHIVE_APPROVAL.json'
$taskApproval = Get-Content -LiteralPath $taskApprovalPath -Raw -Encoding UTF8 | ConvertFrom-Json
$taskVideos = @('20260926_211809000_iOS.MP4','20260926_212155000_iOS.MP4')
if ($taskApproval.approved -ne $true -or $taskApproval.answer -ne 'Approve archival of these two excerpts' -or @($taskApproval.source_basenames).Count -ne 2) { throw 'Exact owner exception required' }
foreach ($taskVideo in $taskVideos) {
    if ($taskVideo -notin $taskApproval.source_basenames) { throw 'Source not approved' }
    $taskSource = [IO.Path]::GetFullPath((Join-Path $taskRoot $taskVideo))
    $taskDestination = [IO.Path]::GetFullPath((Join-Path $taskRoot ('Reviewed/' + $taskVideo)))
    $taskPacket = [IO.Path]::GetFullPath((Join-Path $taskBatch ([IO.Path]::GetFileNameWithoutExtension($taskVideo))))
    if ([IO.Path]::GetDirectoryName($taskSource) -ne $taskRoot -or [IO.Path]::GetDirectoryName($taskDestination) -ne (Join-Path $taskRoot 'Reviewed') -or !$taskPacket.StartsWith($taskBatch + '\')) { throw 'Resolved target outside intended workspace' }
    if (!(Test-Path -LiteralPath $taskSource) -or (Test-Path -LiteralPath $taskDestination)) { throw 'Source missing or destination collision' }
    $taskLead = Get-Content -LiteralPath (Join-Path $taskPacket 'LEAD_ACCEPTANCE.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $taskIndependent = Get-Content -LiteralPath (Join-Path $taskPacket 'independent_sol/CHECK_RESULT.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $taskRegistration = Get-Content -LiteralPath (Join-Path $taskPacket 'REGISTRATION_RESULT.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($taskLead.accepted -ne $true -or $taskLead.battle_complete -ne $false -or $taskIndependent.decision -ne 'accepted_available_footage_packet' -or $taskRegistration.exit_code -ne 0) { throw 'Accepted available-footage review required' }
    $taskApprovedHash = $taskApproval.source_sha256.$taskVideo
    if ($taskLead.source_sha256 -ne $taskApprovedHash) { throw 'Approval identity mismatch' }
    $taskBefore = (Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($taskBefore -ne $taskApprovedHash) { throw 'Current source hash mismatch' }
    $taskEvents = @(Get-ChildItem -LiteralPath (Join-Path $taskRoot 'Review_Log/events') -Filter '*.json' | ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json } | Where-Object video_basename -eq $taskVideo | Sort-Object logged_at_utc)
    $taskLatest = $taskEvents[-1]
    if ($taskLatest.status -ne 'partial' -or $taskLatest.video_sha256 -ne $taskBefore) { throw 'Latest matching partial event required' }
    $taskLockPath = [IO.Path]::GetFullPath((Join-Path $taskRoot 'Review_Log/.write.lock'))
    if (!$taskLockPath.StartsWith((Join-Path $taskRoot 'Review_Log') + '\')) { throw 'Lock outside expected workspace' }
    $null = New-Item -ItemType Directory -Path $taskLockPath -ErrorAction Stop
    try {
        @{pid=$PID;purpose='Explicit owner exception for two recording-limited excerpt archives'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskLockPath 'owner.json') -Encoding utf8
        $taskRows = @(Import-Csv -LiteralPath (Join-Path $taskRoot 'BATTLE_REVIEW_INDEX.csv'))
        $taskRow = @($taskRows | Where-Object Video -eq $taskVideo)
        if ($taskRow.Count -ne 1 -or $taskRow[0].Status -ne 'Needs full battle review') { throw 'Matching partial index row required' }
        $taskSize = (Get-Item -LiteralPath $taskSource).Length
        Move-Item -LiteralPath $taskSource -Destination $taskDestination
        $taskAfter = (Get-FileHash -LiteralPath $taskDestination -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($taskAfter -ne $taskBefore) { throw 'Post-move identity mismatch' }
        $taskUtc = [DateTime]::UtcNow.ToString('o')
        $taskReceipt = Join-Path $taskPacket ('MOVE_RECEIPT.' + $taskVideo + '.json')
        @{schema='battle-media-move-receipt/v1';filename=$taskVideo;from=$taskSource;to=$taskDestination;bytes=$taskSize;sha256_before=$taskBefore;sha256_after=$taskAfter;identity_match=$true;moved_utc=$taskUtc;review_event_id=$taskLatest.event_id;review_status='partial';battle_complete=$false;archive_authority='Explicit owner exception for completed available-footage excerpt';approval_receipt=$taskApprovalPath} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $taskReceipt -Encoding utf8
        @{approved=$true;source_video=$taskVideo;source_sha256=$taskBefore;available_footage_review_accepted=$true;battle_complete=$false;preserved_status='Needs full battle review';approval_receipt=$taskApprovalPath;move_receipt=$taskReceipt;approved_utc=$taskUtc} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskPacket 'LEAD_ARCHIVE_EXCEPTION.json') -Encoding utf8
        $taskRow[0].Location = 'Reviewed/' + $taskVideo
        $taskRow[0].Notes += ' Owner explicitly approved archive/offload of this completed excerpt on 2026-10-14; partial-battle status and missing-opening notes preserved.'
        $taskRows | Export-Csv -LiteralPath (Join-Path $taskRoot 'BATTLE_REVIEW_INDEX.csv') -NoTypeInformation -Encoding utf8BOM
        $taskMapPath = Join-Path $taskRoot 'MEDIA_LOCATIONS.json'
        $taskMap = Get-Content -LiteralPath $taskMapPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $taskEntry = [pscustomobject]@{filename=$taskVideo;old_path=$taskSource;current_path=$taskDestination;bytes=$taskSize;sha256=$taskAfter;review_evidence=@((Join-Path $taskPacket 'REVIEW.md'),(Join-Path $taskPacket 'LEAD_ACCEPTANCE.json'),(Join-Path $taskPacket 'LEAD_ARCHIVE_EXCEPTION.json'));location_history=@(@{from=$taskSource;to=$taskDestination;utc=$taskUtc;reason='Explicit owner archive exception; complete available footage, partial battle';receipt=$taskReceipt});review_status='Needs full battle review';battle_complete=$false;archive_exception_approval=$taskApprovalPath}
        $taskMap.moved = @($taskMap.moved | Where-Object filename -ne $taskVideo) + @($taskEntry)
        $taskMap.index_video_count = $taskRows.Count
        $taskMap.awaiting_review_or_confirmation = @($taskRows | Where-Object Status -ne 'Reviewed').Count
        $taskMap.updated_utc = $taskUtc
        $taskMap | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath $taskMapPath -Encoding utf8
        Write-Output "Verified owner-approved excerpt move: $taskVideo ($taskAfter); partial status preserved"
    } finally {
        $taskOwnLockRecord = Join-Path $taskLockPath 'owner.json'
        if (Test-Path -LiteralPath $taskOwnLockRecord) {
            $taskOwnLockItem = Get-Item -LiteralPath $taskOwnLockRecord -Force
            $taskOwnLockItem.Attributes = $taskOwnLockItem.Attributes -band (-bnot [IO.FileAttributes]::ReadOnly)
            Remove-Item -LiteralPath $taskOwnLockRecord
        }
        if ((Test-Path -LiteralPath $taskLockPath) -and @(Get-ChildItem -LiteralPath $taskLockPath -Force).Count -eq 0) {
            $taskOwnLockDirectory = Get-Item -LiteralPath $taskLockPath -Force
            $taskOwnLockDirectory.Attributes = $taskOwnLockDirectory.Attributes -band (-bnot [IO.FileAttributes]::ReadOnly)
            Remove-Item -LiteralPath $taskLockPath
        }
    }
}
