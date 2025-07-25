Remove-Item temp -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item python -Force -Recurse -ErrorAction SilentlyContinue
mkdir temp
$ProgressPreference = 'SilentlyContinue'
# Find python dl url
$arch = $env:PROCESSOR_ARCHITECTURE
$url = ""
if ($arch -eq "x86") {
    $url = "https://www.python.org/ftp/python/3.13.2/python-3.13.2-embed-win32.zip"
} elseif ($arch -eq "AMD64"){
    $url = "https://www.python.org/ftp/python/3.13.2/python-3.13.2-embed-amd64.zip"
} elseif ($arch -eq "ARM"){
    throw "Arch not supported (Fun fact: IT IS SO SLOW, JUST GET A NEW COMPUTER!)"
} elseif ($arch -eq "ARM64"){
    $url = "https://www.python.org/ftp/python/3.13.2/python-3.13.2-embed-arm64.zip"
}

Invoke-WebRequest -OutFile ./temp/python.zip $url
Expand-Archive temp/python.zip -DestinationPath python

./python/python ./get-pip.py
Add-Content -Path ./python/python*._pth -Value "import site`n../`n../preserve/updates"
./python/python -m pip install -r requirements.txt
./python/python ./add_shortcut.py
Remove-Item temp -Force -Recurse -ErrorAction SilentlyContinue