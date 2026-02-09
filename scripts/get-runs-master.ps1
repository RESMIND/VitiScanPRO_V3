$uri = "https://api.github.com/repos/RESMIND/VitiScanPRO_V3/actions/runs?branch=master&per_page=10"
Write-Output "Fetching $uri"
Invoke-WebRequest -Uri $uri -OutFile "$PSScriptRoot\runs_master.json"
Write-Output "Saved $PSScriptRoot\runs_master.json"