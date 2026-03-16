REM ============================================================
REM  launch.vbs  —  VBScript Launcher (Double-click to run)
REM ============================================================
REM This script minimizes the console window and launches Amulya AI
REM Save this file and double-click it to start the app

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strScriptPath = objShell.CurrentDirectory & "\run.bat"

If objFSO.FileExists(strScriptPath) Then
    objShell.Run strScriptPath, 1, False
Else
    MsgBox "Error: run.bat not found in " & objShell.CurrentDirectory, vbCritical, "Amulya AI Launcher"
End If
