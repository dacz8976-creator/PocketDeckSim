$ErrorActionPreference = 'Stop'
$receiptPath = Join-Path $PSScriptRoot 'ONEDRIVE_RECOVERY.json'
if (Test-Path -LiteralPath $receiptPath) { throw 'Inspect existing recovery before retrying' }
$clients = @(Get-Process -Name OneDrive -ErrorAction SilentlyContinue)
if (!$clients.Count) { throw 'No running OneDrive client to identify' }
$paths = @($clients | ForEach-Object Path | Sort-Object -Unique)
if ($paths.Count -ne 1 -or !(Test-Path -LiteralPath $paths[0])) { throw 'Cannot identify one installed OneDrive executable' }
$installedExe = $paths[0]
$receipt = [ordered]@{
    started_utc = [DateTime]::UtcNow.ToString('o')
    operation = 'One graceful shutdown and hidden restart to recover two stalled source downloads'
    executable = $installedExe
    original_client_pids = @($clients.Id)
    source_files_modified = $false
    settings_changed = $false
    forced_termination = $false
    shutdown_completed = $false
    restart_requested = $false
}
$shutdownRequest = Start-Process -FilePath $installedExe -ArgumentList '/shutdown' -WindowStyle Hidden -PassThru
$receipt.shutdown_request_pid = $shutdownRequest.Id
$deadline = [DateTime]::UtcNow.AddSeconds(40)
do {
    $stillRunning = @($clients.Id | ForEach-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue })
    if (!$stillRunning.Count) { break }
    Start-Sleep -Seconds 1
} while ([DateTime]::UtcNow -lt $deadline)
$receipt.original_clients_still_running = @($stillRunning.Id)
if (!$stillRunning.Count) {
    $receipt.shutdown_completed = $true
    $newClient = Start-Process -FilePath $installedExe -WindowStyle Hidden -PassThru
    $receipt.restart_requested = $true
    $receipt.restarted_pid = $newClient.Id
}
$receipt.checked_utc = [DateTime]::UtcNow.ToString('o')
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8
$receipt | ConvertTo-Json -Depth 8
