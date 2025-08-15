' Create Desktop Shortcut for Food POS System
Set WshShell = CreateObject("WScript.Shell")
Set oShellLink = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") & "\Food POS System.lnk")

' Get current directory
strCurrentDir = CreateObject("Scripting.FileSystemObject").GetAbsolutePathName(".")

' Set shortcut properties
oShellLink.TargetPath = strCurrentDir & "\Food_POS.bat"
oShellLink.WorkingDirectory = strCurrentDir
oShellLink.Description = "Food POS System - Restaurant Management"
oShellLink.IconLocation = strCurrentDir & "\icon.ico,0"

' Save the shortcut
oShellLink.Save

' Show success message
WScript.Echo "Desktop shortcut created successfully!" & vbCrLf & vbCrLf & "You can now start Food POS System from your desktop."