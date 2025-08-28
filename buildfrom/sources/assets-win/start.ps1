try {
    New-Item -Path "./" -Name "preserve" -ItemType Directory
} catch {

}
try {
    New-Item -Path "./preserve" -Name "updates" -ItemType Directory
} catch {

}
Get-ChildItem -Path "./preserve/updates" -Force | Remove-Item -Recurse -Force

New-Item -Path "./preserve/updates" -Name "acode" -ItemType Directory

Copy-Item "./gui/updates.py" -Destination "./preserve/updates/acode"
Copy-Item "./gui/common.py" -Destination "./preserve/updates/acode"
Copy-Item "./gui/loaders.py" -Destination "./preserve/updates/acode"
Copy-Item "./gui/release_manifest.py" -Destination "preserve/updates/acode"
Copy-Item "./gui/collapsibleSection.py" -Destination "preserve/updates/acode"
Copy-Item "./gui/_types.py" -Destination "./preserve/updates/acode"

"import acode.updates`nacode.updates.startApp()" | Out-File -Encoding UTF8 -FilePath "./preserve/updates/main.py"
$path=$PWD.Path
$path -replace "\\", "\\\\"
"assets_root=`"$path`"" | Out-File -Encoding UTF8 -FilePath "./preserve/updates/assets_root.py"
./python/python ./preserve/updates/main.py
Get-ChildItem -Path "./preserve/updates" -Force | Remove-Item -Recurse -Force

./python/python main.py