$DiscordAppPath = (Join-Path "$($env:localappdata)\Discord\" $(cmd /c dir "%localappdata%\Discord" /B /A:D | findstr app))
$DiscordPath = "$($DiscordAppPath)\resources"
$asarUrl = "https://github.com/rauenzi/BetterDiscordApp/releases/latest/download/betterdiscord.asar"
$asarFile = "$($env:APPDATA)\BetterDiscord\data\betterdiscord.asar"
Invoke-WebRequest -Uri $asarUrl -OutFile (New-Item -Path $asarFile -Force)
New-Item -ItemType Directory -Path "$($DiscordPath)\app" -Force >$null
Set-Content -Path "$($DiscordPath)\app\package.json" `
            -Value '{"name": "betterdiscord", "main": "index.js"}'
Set-Content -Path "$($DiscordPath)\app\index.js" `
            -Value "require('$($asarFile.Replace("\", "/").Replace("'", "\'"))')"