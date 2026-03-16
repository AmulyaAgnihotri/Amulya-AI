# 🚀 Launch Scripts for Amulya AI

Three convenient ways to start the voice assistant:

## **Option 1: Double-Click (Easiest)**
👉 **Double-click `launch.vbs`**

This opens a console window and launches the app. Perfect for quick access.

---

## **Option 2: Command Prompt**
```cmd
run.bat
```

Works in Windows Command Prompt or PowerShell. Simple and straightforward.

---

## **Option 3: PowerShell (Most Features)**
```powershell
.\run.ps1                  # Basic launch
.\run.ps1 -Logs           # Show recent log files
```

**Note:** If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\run.ps1
```

---

## **Create Desktop Shortcut** (Optional)

### For Double-Click Launch:
1. Right-click `launch.vbs` → **Send to** → **Desktop (create shortcut)**
2. Double-click shortcut to launch anytime!

### For Command Prompt:
1. Right-click desktop → **New** → **Shortcut**
2. Enter target: 
   ```
   cmd /k "cd /d E:\VS Code\Amulya AI && run.bat"
   ```
3. Name it "Amulya AI" and click Finish

---

## **How to Use Once Running**

Say **"Hey Amulya"** to wake up the assistant, then say your command:

- "What's the weather in New York?"
- "Play Shape of You on YouTube"
- "Tell me a joke"
- "Take a screenshot"
- "Open Google"
- "What time is it?"

Type **"exit"** or **"quit"** to stop the assistant.

---

## **Logs**

Activity logs are saved in the `logs/` folder. View them with:
```powershell
Get-Content logs\amulya_ai_*.log
```

Or use the PowerShell launch script with `-Logs` flag to see recent logs.
