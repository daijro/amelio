#  Original: http://www.eightforums.com/tutorials/9487-clear-clipboard-add-context-menu-windows.html
#  Converted to powershell using Reg2CI

if((Test-Path -LiteralPath "HKLM:\SOFTWARE\Classes\*\shell\Clear Clipboard") -ne $true) {  New-Item "HKLM:\SOFTWARE\Classes\*\shell\Clear Clipboard" -force -ea SilentlyContinue };
if((Test-Path -LiteralPath "HKLM:\SOFTWARE\Classes\*\shell\Clear Clipboard\command") -ne $true) {  New-Item "HKLM:\SOFTWARE\Classes\*\shell\Clear Clipboard\command" -force -ea SilentlyContinue };
if((Test-Path -LiteralPath "HKLM:\SOFTWARE\Classes\Directory\background\shell\Clear Clipboard") -ne $true) {  New-Item "HKLM:\SOFTWARE\Classes\Directory\background\shell\Clear Clipboard" -force -ea SilentlyContinue };
if((Test-Path -LiteralPath "HKLM:\SOFTWARE\Classes\Directory\background\shell\Clear Clipboard\command") -ne $true) {  New-Item "HKLM:\SOFTWARE\Classes\Directory\background\shell\Clear Clipboard\command" -force -ea SilentlyContinue };
if((Test-Path -LiteralPath "HKLM:\SOFTWARE\Classes\Folder\shell\Clear Clipboard") -ne $true) {  New-Item "HKLM:\SOFTWARE\Classes\Folder\shell\Clear Clipboard" -force -ea SilentlyContinue };
if((Test-Path -LiteralPath "HKLM:\SOFTWARE\Classes\Folder\shell\Clear Clipboard\command") -ne $true) {  New-Item "HKLM:\SOFTWARE\Classes\Folder\shell\Clear Clipboard\command" -force -ea SilentlyContinue };
if((Test-Path -LiteralPath "HKLM:\SOFTWARE\Classes\LibraryFolder\background\shell\Clear Clipboard") -ne $true) {  New-Item "HKLM:\SOFTWARE\Classes\LibraryFolder\background\shell\Clear Clipboard" -force -ea SilentlyContinue };
if((Test-Path -LiteralPath "HKLM:\SOFTWARE\Classes\LibraryFolder\background\shell\Clear Clipboard\command") -ne $true) {  New-Item "HKLM:\SOFTWARE\Classes\LibraryFolder\background\shell\Clear Clipboard\command" -force -ea SilentlyContinue };
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\*\shell\Clear Clipboard' -Name 'Icon' -Value 'shell32.dll,-16763' -PropertyType String -Force -ea SilentlyContinue;
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\*\shell\Clear Clipboard' -Name 'Position' -Value 'Bottom' -PropertyType String -Force -ea SilentlyContinue;
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\*\shell\Clear Clipboard\command' -Name '(default)' -Value 'cmd.exe /c "echo off | clip' -PropertyType String -Force -ea SilentlyContinue;
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\Directory\background\shell\Clear Clipboard' -Name 'Icon' -Value 'shell32.dll,-16763' -PropertyType String -Force -ea SilentlyContinue;
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\Directory\background\shell\Clear Clipboard\command' -Name '(default)' -Value 'cmd.exe /c "echo off | clip' -PropertyType String -Force -ea SilentlyContinue;
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\Folder\shell\Clear Clipboard' -Name 'Icon' -Value 'shell32.dll,-16763' -PropertyType String -Force -ea SilentlyContinue;
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\Folder\shell\Clear Clipboard\command' -Name '(default)' -Value 'cmd.exe /c "echo off | clip' -PropertyType String -Force -ea SilentlyContinue;
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\LibraryFolder\background\shell\Clear Clipboard' -Name 'Icon' -Value 'shell32.dll,-16763' -PropertyType String -Force -ea SilentlyContinue;
New-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Classes\LibraryFolder\background\shell\Clear Clipboard\command' -Name '(default)' -Value 'cmd.exe /c "echo off | clip' -PropertyType String -Force -ea SilentlyContinue;