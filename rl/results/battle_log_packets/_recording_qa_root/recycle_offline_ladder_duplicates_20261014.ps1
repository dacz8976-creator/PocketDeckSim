$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$taskBatch = Join-Path $taskRoot 'Recording_QA/BATCH_2026-10-14_OFFLINE_LADDER_FOUR'
$taskPlan = Get-Content -LiteralPath (Join-Path $taskBatch 'DUPLICATE_CLEANUP_PLAN.json') -Raw | ConvertFrom-Json
$taskKeepStates = Get-Content -LiteralPath (Join-Path $taskBatch 'SYNC_RECOVERY_KEEP_SYNC.json') -Raw | ConvertFrom-Json
$taskContentChecks = Get-Content -LiteralPath (Join-Path $taskBatch 'SYNC_RECOVERY_CONTENT_CHECKS.json') -Raw | ConvertFrom-Json
$taskAllowedNames = @('20261014_160506000_iOS.MP4','20261014_161324000_iOS.MP4','20261014_163325000_iOS.MP4','20261014_164328000_iOS.MP4')
$taskAllowedParents = @([IO.Path]::GetFullPath((Join-Path $taskRoot 'Offline_Reviewed')), 'C:\Users\dacz8\Downloads')
$taskReceiptPath = Join-Path $taskBatch 'DUPLICATE_CLEANUP_RECEIPT.json'
$taskCompleted = @()
if (Test-Path -LiteralPath $taskReceiptPath) {
    $taskPrior = Get-Content -LiteralPath $taskReceiptPath -Raw | ConvertFrom-Json
    $taskCompleted = @($taskPrior.files)
}
Add-Type -AssemblyName Microsoft.VisualBasic
foreach ($taskItem in $taskPlan.files) {
    $taskPath = [IO.Path]::GetFullPath($taskItem.path)
    $taskParent = [IO.Path]::GetDirectoryName($taskPath)
    $taskKeep = [IO.Path]::GetFullPath($taskItem.keep)
    if ($taskParent -notin $taskAllowedParents -or [IO.Path]::GetFileName($taskPath) -notin $taskAllowedNames) { throw 'Duplicate target outside exact authorized paths' }
    if ([IO.Path]::GetDirectoryName($taskKeep) -ne (Join-Path $taskRoot 'Reviewed') -or $taskPath -eq $taskKeep) { throw 'Invalid retained archive path' }
    $taskKeepState = @($taskKeepStates.sources | Where-Object filename -eq $taskItem.filename)
    if ($taskKeepState.Count -ne 1 -or !$taskKeepState[0].metadata.cloud_placeholder) { throw 'Retained cloud source identity is missing' }
    $taskKeepInfo = Get-Item -LiteralPath $taskKeep
    if ($taskKeepInfo.Length -ne $taskItem.bytes) { throw 'Retained archive size mismatch' }
    $taskPacket = Join-Path $taskBatch ([IO.Path]::GetFileNameWithoutExtension($taskItem.filename))
    $taskMove = Get-Content -LiteralPath (Join-Path $taskPacket 'SYNC_RECOVERY_MOVE_RECEIPT.json') -Raw | ConvertFrom-Json
    if (!$taskMove.identity_match -or !$taskMove.canonical_cloud_copy_verified -or $taskMove.sha256_after -ne $taskItem.sha256 -or $taskMove.to -ne $taskKeep) { throw 'Verified retained canonical source is required' }
    $taskSourceCheck = @($taskContentChecks.checks | Where-Object filename -eq $taskItem.filename)[0]
    $taskKeptOriginalCheck = @($taskSourceCheck.copies | Where-Object path -eq $taskMove.from)[0]
    $taskKeptMtimeNs = ($taskKeepInfo.LastWriteTimeUtc.Ticks - 621355968000000000L) * 100L
    if ($taskKeptMtimeNs -ne $taskKeptOriginalCheck.mtime_ns) { throw 'Retained archive changed since hash verification' }
    if (@($taskCompleted | Where-Object path -eq $taskPath).Count -eq 1) {
        if (Test-Path -LiteralPath $taskPath) { throw 'Previously recycled duplicate reappeared' }
        continue
    }
    $taskInfo = Get-Item -LiteralPath $taskPath
    $taskMtimeNs = ($taskInfo.LastWriteTimeUtc.Ticks - 621355968000000000L) * 100L
    if ($taskInfo.Length -ne $taskItem.bytes -or $taskMtimeNs -ne $taskItem.mtime_ns) { throw 'Duplicate changed since byte identity verification' }
    [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($taskPath,
        [Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,
        [Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin,
        [Microsoft.VisualBasic.FileIO.UICancelOption]::ThrowException)
    if (Test-Path -LiteralPath $taskPath) { throw 'Duplicate remains after recycle operation' }
    $taskCompleted += [pscustomobject]@{path=$taskPath;kept=$taskKeep;sha256=$taskItem.sha256;bytes=$taskItem.bytes;recycled_utc=[DateTime]::UtcNow.ToString('o');recoverable=$true;retained_archive_sync_pending=(!$taskKeepState[0].metadata.in_sync);retained_canonical_identity_verified=$true}
    [pscustomobject]@{method='Windows Recycle Bin';permanent_deletions=0;files=$taskCompleted;recycled_count=$taskCompleted.Count} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $taskReceiptPath -Encoding utf8
    Write-Output ('Recycled verified duplicate: ' + $taskPath)
}
if ($taskCompleted.Count -ne 8) { throw 'Expected exactly eight verified extra copies' }
