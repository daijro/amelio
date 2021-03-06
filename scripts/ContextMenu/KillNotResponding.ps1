# Original: https://www.tenforums.com/tutorials/78714-kill-all-not-responding-tasks-add-context-menu-windows-10-a.html
#  Converted to powershell using Reg2CI

if((Test-Path -LiteralPath "HKLM:\SOFTWARE\Classes\DesktopBackground\Shell\KillNRTasks") -ne $true) {  New-Item "HKLM:\SOFTWARE\Classes\DesktopBackground\Shell\KillNRTasks" -force -ea SilentlyContinue };
if((Test-Path -LiteralPath "HKLM:\SOFTWARE\Classes\DesktopBackground\Shell\KillNRTasks\command") -ne $true) {  New-Item "HKLM:\SOFTWARE\Classes\DesktopBackground\Shell\KillNRTasks\command" -force -ea SilentlyContinue };
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\DesktopBackground\Shell\KillNRTasks' -Name 'icon' -Value 'taskmgr.exe,-30651' -PropertyType String -Force -ea SilentlyContinue;
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\DesktopBackground\Shell\KillNRTasks' -Name 'MUIverb' -Value 'Kill all not responding tasks' -PropertyType String -Force -ea SilentlyContinue;
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\DesktopBackground\Shell\KillNRTasks' -Name 'Position' -Value 'Top' -PropertyType String -Force -ea SilentlyContinue;
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\DesktopBackground\Shell\KillNRTasks\command' -Name '(default)' -Value 'CMD.exe /C taskkill.exe /f /fi "status eq Not Responding" & Pause' -PropertyType String -Force -ea SilentlyContinue;