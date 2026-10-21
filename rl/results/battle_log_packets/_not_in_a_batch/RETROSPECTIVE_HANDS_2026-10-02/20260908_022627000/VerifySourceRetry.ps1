$ErrorActionPreference = 'Stop'
$taskSource = 'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Reviewed\20260908_022627000_iOS.MP4'
$taskReceipt = Join-Path $PSScriptRoot 'SOURCE_VERIFICATION.json'
$taskFirstReceipt = Join-Path $PSScriptRoot 'SOURCE_VERIFICATION_ATTEMPT_1.json'
Copy-Item -LiteralPath $taskReceipt -Destination $taskFirstReceipt
$taskExpected = '5689a2c45eda9b0629d7a2616852beef6fedb8396bdfe34c080b4c136e4e364e'
$taskBefore = Get-Item -LiteralPath $taskSource
$taskStarted = [DateTime]::UtcNow
$taskData = [ordered]@{ source='20260908_022627000_iOS.MP4'; current_path=$taskSource; expected_sha256=$taskExpected; expected_bytes=1351891106; bytes_before=$taskBefore.Length; status='delivery_read_in_progress'; started_utc=$taskStarted.ToString('o'); attempt_number=2; previous_attempt_receipt='SOURCE_VERIFICATION_ATTEMPT_1.json'; source_identity_hash_attempts=2; concurrent_readers=1; authorization='Lead authorized one retry after prior read ended naturally with OS cloud timeout. Root observes metadata only.' }
$taskData | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskReceipt -Encoding utf8
try {
 $taskHash = (Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash.ToLowerInvariant()
 $taskAfter = Get-Item -LiteralPath $taskSource
 $taskData['actual_sha256']=$taskHash
 $taskData['bytes_after']=$taskAfter.Length
 $taskData['finished_utc']=[DateTime]::UtcNow.ToString('o')
 $taskData['wall_seconds']=([DateTime]::UtcNow-$taskStarted).TotalSeconds
 $taskData['source_stable']=($taskBefore.Length -eq $taskAfter.Length -and $taskBefore.LastWriteTimeUtc -eq $taskAfter.LastWriteTimeUtc)
 $taskData['status']=if($taskHash -eq $taskExpected -and $taskAfter.Length -eq 1351891106 -and $taskData['source_stable']) {'verified_sha256_match'} else {'verification_mismatch'}
 $taskData | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskReceipt -Encoding utf8
 Write-Output ($taskData | ConvertTo-Json -Depth 6 -Compress)
 if ($taskData['status'] -ne 'verified_sha256_match') { throw 'Source verification mismatch' }
} catch {
 $taskData['status']='verification_failed'
 $taskData['error']=$_.Exception.Message
 $taskData['finished_utc']=[DateTime]::UtcNow.ToString('o')
 $taskData | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskReceipt -Encoding utf8
 throw
}
