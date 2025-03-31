Start-Job -ScriptBlock { 
    while ($true) {taskkill /F /IM "iboss Cloud Desktop App.exe" /T; Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name AutoConfigURL -Type String -Value "";}
} -Name "bypasser" 
powershell ./_.ps1