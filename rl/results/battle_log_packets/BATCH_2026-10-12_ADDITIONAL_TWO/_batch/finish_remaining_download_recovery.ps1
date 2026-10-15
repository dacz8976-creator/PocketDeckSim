$ErrorActionPreference = 'Stop'
$path = Join-Path $PSScriptRoot 'ONEDRIVE_RECOVERY_SECOND.json'
$r = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
if ($r.restart_requested) { throw 'Restart already requested' }
$old = @($r.original_client_pids | ForEach-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue })
if ($old.Count) { throw 'Original clients are still closing; leave them alone' }
$other = @(Get-Process -Name OneDrive -ErrorAction SilentlyContinue | Where-Object Id -ne $r.shutdown_request_pid)
if ($other.Count) { throw 'Other OneDrive clients appeared; inspect before launching another' }
$helper = Get-CimInstance Win32_Process -Filter ('ProcessId=' + $r.shutdown_request_pid)
if ($helper -and ($helper.CommandLine -notlike '*/shutdown*' -or $helper.ExecutablePath -ne $r.executable)) { throw 'Shutdown helper identity mismatch' }
Copy-Item -LiteralPath $path -Destination (Join-Path $PSScriptRoot 'ONEDRIVE_RECOVERY_SECOND.initial.json') -ErrorAction Stop
if ($helper) { Stop-Process -Id $r.shutdown_request_pid -ErrorAction Stop }
$fresh = Start-Process -FilePath $r.executable -WindowStyle Hidden -PassThru
$r.shutdown_completed = $true
$r.restart_requested = $true
$r.original_clients_still_running = @()
$r | Add-Member -NotePropertyName followup_utc -NotePropertyValue ([DateTime]::UtcNow.ToString('o'))
$r | Add-Member -NotePropertyName restarted_pid -NotePropertyValue $fresh.Id
$r | Add-Member -NotePropertyName task_owned_shutdown_helper_stopped -NotePropertyValue ([bool]$helper)
$r | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $path -Encoding utf8
$r | ConvertTo-Json -Depth 8
