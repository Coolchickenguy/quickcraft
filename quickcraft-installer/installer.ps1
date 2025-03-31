Remove-Item temp -Force -Recurse -ErrorAction SilentlyContinue
#Remove-Item java -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item python -Force -Recurse -ErrorAction SilentlyContinue
mkdir temp
$ProgressPreference = 'SilentlyContinue'
# Find python dl url
$arch = $env:PROCESSOR_ARCHITECTURE
$url = ""
if ($arch -eq "x86") {
    $url = "https://www.python.org/ftp/python/3.13.2/python-3.13.2-embed-win32.zip"
} else if ($arch -eq "AMD64"){
    $url = "https://www.python.org/ftp/python/3.13.2/python-3.13.2-embed-amd64.zip"
} else if ($arch -eq "ARM"){
    throw "Arch not supported (Fun fact: IT IS SO SLOW, JUST GET A NEW COMPUTER!)"
} else if ($arch -eq "ARM64"){
    $url = "https://www.python.org/ftp/python/3.13.2/python-3.13.2-embed-arm64.zip"
}

Invoke-WebRequest -OutFile ./temp/python.zip $url
Expand-Archive temp/python.zip -DestinationPath python

#Invoke-WebRequest -OutFile ./temp/java21.zip https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.6%2B7/OpenJDK21U-jre_x64_windows_hotspot_21.0.6_7.zip
#Expand-Archive temp/java21.zip -DestinationPath java
#mv ./java/*/* ./java
./python/python ./get-pip.py
Add-Content -Path ./python/python*._pth -Value 'import site'
./python/python -m pip install minecraft_launcher_lib
Remove-Item temp -Force -Recurse -ErrorAction SilentlyContinue