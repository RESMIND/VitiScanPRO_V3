$repo = 'RESMIND/VitiScanPRO_V3'
$pr = 2
while ($true) {
  try {
    $prData = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/pulls/$pr" -Headers @{ 'User-Agent' = 'vitiscan-monitor' }
    $sha = $prData.head.sha
    $status = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/commits/$sha/status" -Headers @{ 'User-Agent' = 'vitiscan-monitor' }
    $state = $status.state
    Write-Output "$(Get-Date -Format o) COMBINED STATE: $state"

    $checkRuns = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/commits/$sha/check-runs" -Headers @{ 'User-Agent' = 'vitiscan-monitor'; 'Accept' = 'application/vnd.github.v3+json' }
    foreach ($cr in $checkRuns.check_runs) {
      $name = $cr.name
      $st = $cr.status
      $concl = $cr.conclusion
      Write-Output "$name - $st - $concl"
    }

    if ($state -eq 'success') {
      $allOk = $true
      foreach ($cr in $checkRuns.check_runs) {
        if ($cr.status -ne 'completed' -or $cr.conclusion -ne 'success') {
          $allOk = $false
          break
        }
      }
      if ($allOk) {
        Write-Output "ALL CHECKS GREEN - STOPPING MONITOR"
        break
      } else {
        Write-Output "Combined success but some check runs not success yet."
      }
    }
  } catch {
    Write-Output "Error calling GitHub API: $($_.Exception.Message)"
  }

  Start-Sleep -Seconds 120
}
Write-Output "READY_TO_MERGE"
