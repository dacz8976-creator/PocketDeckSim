$ErrorActionPreference = 'Stop'
$receiptPath = Join-Path $PSScriptRoot 'ONEDRIVE_RECOVERY.json'
if (Test-Path -LiteralPath $receiptPath) { throw 'Inspect the existing recovery before another restart.' }
$clients = @(Get-Process -Name OneDrive -ErrorAction SilentlyContinue)
if (!$clients.Count) { throw 'No running OneDrive client.' }
$paths = @($clients | ForEach-Object Path | Sort-Object -Unique)
$installedExe = 'C:\Program Files\Microsoft OneDrive\OneDrive.exe'
if ($paths.Count -ne 1 -or $paths[0] -ne $installedExe -or !(Test-Path -LiteralPath $installedExe)) { throw 'Installed client identity does not match.' }
$receipt = [ordered]@{
    started_utc = [DateTime]::UtcNow.ToString('o')
    operation = 'One graceful OneDrive restart after both requested downloads stalled at 500 MiB and a bounded missing-range request timed out.'
    executable = $installedExe
    original_client_pids = @($clients.Id)
    source_contents_rewritten = $false
    settings_changed = $false
    original_clients_forcibly_terminated = $false
    shutdown_completed = $false
    restart_requested = $false
}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath ($receiptPath + '.initial') -Encoding utf8
$shutdownRequest = Start-Process -FilePath $installedExe -ArgumentList '/shutdown' -WindowStyle Hidden -PassThru
$receipt.shutdown_request_pid = $shutdownRequest.Id
$deadline = [DateTime]::UtcNow.AddSeconds(180)
do {
    $stillRunning = @($clients.Id | ForEach-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue })
    if (!$stillRunning.Count) { break }
    Start-Sleep -Seconds 1
} while ([DateTime]::UtcNow -lt $deadline)
$receipt.original_clients_still_running = @($stillRunning.Id)
if (!$stillRunning.Count) {
    $receipt.shutdown_completed = $true
    $shutdownRequest.Refresh()
    if (!$shutdownRequest.HasExited) {
        $ownHelper = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + $shutdownRequest.Id)
        if ($ownHelper.ExecutablePath -ne $installedExe -or $ownHelper.CommandLine -notmatch '/shutdown') { throw 'Task-owned shutdown helper identity changed.' }
        Stop-Process -Id $shutdownRequest.Id -ErrorAction Stop
        $receipt.task_owned_shutdown_helper_stopped = $true
    }
    $newClient = Start-Process -FilePath $installedExe -WindowStyle Hidden -PassThru
    $receipt.restart_requested = $true
    $receipt.restarted_pid = $newClient.Id
}
$receipt.checked_utc = [DateTime]::UtcNow.ToString('o')
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8
$receipt | ConvertTo-Json -Depth 8
