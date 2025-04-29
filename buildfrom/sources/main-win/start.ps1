cd assets
# Prevent updating from upsetting file locks
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", '$content = Get-Content -Raw -Path ./start.ps1; Invoke-Expression $content'