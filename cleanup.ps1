# Kill all Node.js processes (frontend)
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force

# Kill all Python processes (backend)
Get-Process | Where-Object {$_.Path -like "*AutoWeb_Outreach_AI*python*"} | Stop-Process -Force

Write-Host "All processes cleaned up!"
