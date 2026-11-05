param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('smoke', 'docker', 'docker-run', 'kubernetes', 'kubernetes-scale', 'rollout', 'rollout-rollback', 'cd-deploy', 'continuous-deployment')]
    [string]$Experiment
)

$PowerShellExe = (Get-Command pwsh.exe).Source
$CaptureScript = Join-Path $PSScriptRoot 'capture-powershell.ps1'
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class NewConsoleProcess {
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
  public struct STARTUPINFO {
    public int cb; public string lpReserved; public string lpDesktop; public string lpTitle;
    public int dwX; public int dwY; public int dwXSize; public int dwYSize;
    public int dwXCountChars; public int dwYCountChars; public int dwFillAttribute; public int dwFlags;
    public short wShowWindow; public short cbReserved2; public IntPtr lpReserved2;
    public IntPtr hStdInput; public IntPtr hStdOutput; public IntPtr hStdError;
  }
  [StructLayout(LayoutKind.Sequential)] public struct PROCESS_INFORMATION { public IntPtr hProcess; public IntPtr hThread; public int dwProcessId; public int dwThreadId; }
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  public static extern bool CreateProcess(string app, StringBuilder commandLine, IntPtr processAttributes, IntPtr threadAttributes, bool inheritHandles, uint flags, IntPtr environment, string currentDirectory, ref STARTUPINFO startupInfo, out PROCESS_INFORMATION processInformation);
  [DllImport("kernel32.dll")] public static extern uint WaitForSingleObject(IntPtr handle, uint milliseconds);
  [DllImport("kernel32.dll", SetLastError=true)] public static extern bool GetExitCodeProcess(IntPtr process, out uint exitCode);
  [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr handle);
}
'@

$startup = [NewConsoleProcess+STARTUPINFO]::new()
$startup.cb = [System.Runtime.InteropServices.Marshal]::SizeOf([type][NewConsoleProcess+STARTUPINFO])
$startup.dwFlags = 1
$startup.wShowWindow = 1
$pi = [NewConsoleProcess+PROCESS_INFORMATION]::new()
$command = '"{0}" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "{1}" -Experiment "{2}"' -f $PowerShellExe, $CaptureScript, $Experiment
$created = [NewConsoleProcess]::CreateProcess($PowerShellExe, [System.Text.StringBuilder]::new($command), [IntPtr]::Zero, [IntPtr]::Zero, $false, 0x10, [IntPtr]::Zero, $ProjectRoot, [ref]$startup, [ref]$pi)
if (-not $created) { throw "CreateProcess failed with Win32 error $([Runtime.InteropServices.Marshal]::GetLastWin32Error())" }
[void][NewConsoleProcess]::WaitForSingleObject($pi.hProcess, [uint32]::MaxValue)
$exit = [uint32]0
[void][NewConsoleProcess]::GetExitCodeProcess($pi.hProcess, [ref]$exit)
[void][NewConsoleProcess]::CloseHandle($pi.hThread)
[void][NewConsoleProcess]::CloseHandle($pi.hProcess)
Write-Host "PowerShell capture session completed with exit code $exit"
if ($exit -ne 0) { exit $exit }
