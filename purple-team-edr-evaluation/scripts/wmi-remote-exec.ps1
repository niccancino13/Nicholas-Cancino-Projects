# wmi-remote-exec.ps1
Invoke-CimMethod -ClassName Win32_Process -MethodName Create `
  -Arguments @{ CommandLine = 'rundll32.exe shell32.dll,Control_RunDLL desk.cpl' }
