param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('smoke', 'docker', 'docker-run', 'kubernetes', 'kubernetes-scale', 'rollout', 'rollout-rollback', 'cd-deploy', 'continuous-deployment')]
    [string]$Experiment
)

$ErrorActionPreference = 'Continue'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$MinikubeBin = Join-Path $env:LOCALAPPDATA 'Programs\minikube'
if (Test-Path (Join-Path $MinikubeBin 'minikube.exe')) { $env:Path = "$MinikubeBin;$env:Path" }
$CaptureTitle = "DevOps Lab 2 - PowerShell - $Experiment - $PID"
$Host.UI.RawUI.WindowTitle = $CaptureTitle
try {
    $Host.UI.RawUI.BufferSize = [System.Management.Automation.Host.Size]::new(140, 300)
    $Host.UI.RawUI.WindowSize = [System.Management.Automation.Host.Size]::new(140, 45)
} catch { }
Clear-Host
Write-Host 'DEVOPS LAB 2 | Kartik Kumar | 2301730205 | kartikjangra5366@gmail.com' -ForegroundColor Cyan
Write-Host "PowerShell $($PSVersionTable.PSVersion) | Experiment: $Experiment" -ForegroundColor DarkCyan

function Invoke-ActualCommand([string]$Display, [string]$File, [string[]]$Arguments) {
    Write-Host "`nPS> $Display" -ForegroundColor Yellow
    $output = & $File @Arguments 2>&1
    $code = $LASTEXITCODE
    foreach ($line in $output) { Write-Host ([string]$line) }
    if ($null -eq $code) { $code = 0 }
    Write-Host "exit_code=$code" -ForegroundColor Gray
}
function Invoke-ActualPowerShell([string]$Display, [scriptblock]$Action) {
    Write-Host "`nPS> $Display" -ForegroundColor Yellow
    try {
        $result = & $Action 2>&1
        foreach ($line in $result) { Write-Host ([string]$line) }
        Write-Host 'exit_code=0' -ForegroundColor Gray
    } catch {
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host 'exit_code=1' -ForegroundColor Gray
    }
}

switch ($Experiment) {
    'smoke' {
        Invoke-ActualCommand 'python .\scripts\smoke_test.py' 'python' @('.\scripts\smoke_test.py')
    }
    'docker' {
        Invoke-ActualCommand "docker version --format 'client={{.Client.Version}} server={{.Server.Version}}'" 'docker' @('version','--format','client={{.Client.Version}} server={{.Server.Version}}')
        Invoke-ActualCommand 'docker build --quiet -t devops-lab2:1.0.0 .' 'docker' @('build','--quiet','-t','devops-lab2:1.0.0','.')
    }
    'docker-run' {
        $containerName = "devops-lab2-kartik-$PID"
        Invoke-ActualCommand "docker run --rm -d --name $containerName -p 18080:8080 devops-lab2:1.0.0" 'docker' @('run','--rm','-d','--name',$containerName,'-p','18080:8080','devops-lab2:1.0.0')
        Start-Sleep -Seconds 2
        Invoke-ActualPowerShell 'Invoke-RestMethod http://127.0.0.1:18080/healthz' { Invoke-RestMethod -ErrorAction Stop 'http://127.0.0.1:18080/healthz' | ConvertTo-Json -Compress }
        Invoke-ActualPowerShell 'Invoke-RestMethod http://127.0.0.1:18080/api/info | Select application, version, student' {
            $info = Invoke-RestMethod -ErrorAction Stop 'http://127.0.0.1:18080/api/info'
            "application=$($info.application)"
            "version=$($info.version)"
            "student=$($info.student.name) | $($info.student.roll_number) | $($info.student.email)"
        }
        Start-Sleep -Seconds 11
        Invoke-ActualCommand "docker ps --filter name=$containerName --format 'table {{.Names}} {{.Status}} {{.Ports}}'" 'docker' @('ps','--filter',"name=$containerName",'--format','table {{.Names}} {{.Status}} {{.Ports}}')
        Invoke-ActualCommand "docker stop $containerName" 'docker' @('stop',$containerName)
    }
    'kubernetes' {
        Invoke-ActualCommand 'kubectl apply -f .\k8s\namespace.yaml' 'kubectl' @('apply','-f','.\k8s\namespace.yaml')
        Invoke-ActualCommand 'kubectl apply -f .\k8s\deployment.yaml' 'kubectl' @('apply','-f','.\k8s\deployment.yaml')
        Invoke-ActualCommand 'kubectl -n devops-lab2 rollout status deployment/devops-lab2 --timeout=120s' 'kubectl' @('-n','devops-lab2','rollout','status','deployment/devops-lab2','--timeout=120s')
        Start-Sleep -Seconds 5
        Invoke-ActualCommand 'kubectl -n devops-lab2 get deployment,svc' 'kubectl' @('-n','devops-lab2','get','deployment,svc')
    }
    'kubernetes-scale' {
        Invoke-ActualCommand 'kubectl -n devops-lab2 scale deployment/devops-lab2 --replicas=4' 'kubectl' @('-n','devops-lab2','scale','deployment/devops-lab2','--replicas=4')
        Invoke-ActualCommand 'kubectl -n devops-lab2 rollout status deployment/devops-lab2 --timeout=120s' 'kubectl' @('-n','devops-lab2','rollout','status','deployment/devops-lab2','--timeout=120s')
        Invoke-ActualCommand 'kubectl -n devops-lab2 get deployment,pods' 'kubectl' @('-n','devops-lab2','get','deployment,pods')
    }
    'rollout' {
        Invoke-ActualCommand 'docker build -t devops-lab2:1.1.0 .' 'docker' @('build','--quiet','-t','devops-lab2:1.1.0','.')
        Invoke-ActualCommand 'minikube image load devops-lab2:1.1.0' 'minikube' @('image','load','devops-lab2:1.1.0')
        Invoke-ActualCommand 'kubectl -n devops-lab2 set image deployment/devops-lab2 web=devops-lab2:1.1.0' 'kubectl' @('-n','devops-lab2','set','image','deployment/devops-lab2','web=devops-lab2:1.1.0')
        Invoke-ActualCommand 'kubectl -n devops-lab2 set env deployment/devops-lab2 APP_VERSION=1.1.0' 'kubectl' @('-n','devops-lab2','set','env','deployment/devops-lab2','APP_VERSION=1.1.0')
        Invoke-ActualPowerShell 'kubectl -n devops-lab2 rollout status deployment/devops-lab2 --timeout=120s' {
            $output = kubectl -n devops-lab2 rollout status deployment/devops-lab2 --timeout=120s 2>&1
            if ($LASTEXITCODE -ne 0) { throw ($output | Out-String) }
            ($output | Select-Object -Last 1)
        }
        Invoke-ActualCommand 'kubectl -n devops-lab2 rollout history deployment/devops-lab2' 'kubectl' @('-n','devops-lab2','rollout','history','deployment/devops-lab2')
    }
    'rollout-rollback' {
        Invoke-ActualCommand 'kubectl -n devops-lab2 rollout undo deployment/devops-lab2' 'kubectl' @('-n','devops-lab2','rollout','undo','deployment/devops-lab2')
        Invoke-ActualCommand 'kubectl -n devops-lab2 rollout undo deployment/devops-lab2' 'kubectl' @('-n','devops-lab2','rollout','undo','deployment/devops-lab2')
        Invoke-ActualCommand 'kubectl -n devops-lab2 rollout status deployment/devops-lab2' 'kubectl' @('-n','devops-lab2','rollout','status','deployment/devops-lab2')
    }
    'cd-deploy' {
        $tag = "lab2-local-$(Get-Date -Format 'yyyyMMddHHmmss')"
        Invoke-ActualCommand "pwsh -NoLogo -NoProfile -File .\scripts\deploy.ps1 -ImageTag $tag" 'pwsh' @('-NoLogo','-NoProfile','-File','.\scripts\deploy.ps1','-ImageTag',$tag)
    }
    'continuous-deployment' {
        Invoke-ActualPowerShell 'git rev-parse --is-inside-work-tree' { git rev-parse --is-inside-work-tree 2>$null }
        $isRepo = git rev-parse --is-inside-work-tree 2>$null
        if ($isRepo -ne 'true') { Write-Host 'No Git repository or remote is configured in this workspace.' -ForegroundColor Gray }
        else { Invoke-ActualCommand 'git remote -v' 'git' @('remote','-v') }
        Invoke-ActualPowerShell 'Test-Path .\.github\workflows\deploy.yml' { Test-Path .\.github\workflows\deploy.yml }
        Write-Host "`nPS> Get-Content .\.github\workflows\deploy.yml | Select-Object -First 16" -ForegroundColor Yellow
        Get-Content .\.github\workflows\deploy.yml | Select-Object -First 16 | ForEach-Object { Write-Host $_ }
    }
}

Start-Sleep -Milliseconds 900
try {
Add-Type -AssemblyName System.Drawing -ErrorAction Stop
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public class DevopsLabWindowCapture {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int command);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int maxCount);
  public static IntPtr FindVisibleWindowContaining(string needle) {
    IntPtr found = IntPtr.Zero;
    EnumWindows(delegate(IntPtr hwnd, IntPtr param) {
      if (!IsWindowVisible(hwnd)) return true;
      StringBuilder text = new StringBuilder(512);
      GetWindowText(hwnd, text, text.Capacity);
      if (text.ToString().IndexOf(needle, StringComparison.OrdinalIgnoreCase) >= 0) { found = hwnd; return false; }
      return true;
    }, IntPtr.Zero);
    return found;
  }
}
'@
$window = [DevopsLabWindowCapture]::FindVisibleWindowContaining($CaptureTitle)
$outer = [DevopsLabWindowCapture+RECT]::new()
if ($window -eq [IntPtr]::Zero -or -not [DevopsLabWindowCapture]::GetWindowRect($window, [ref]$outer)) {
    throw 'Could not find the visible PowerShell terminal window.'
}
[void][DevopsLabWindowCapture]::SetForegroundWindow($window)
[void][DevopsLabWindowCapture]::ShowWindow($window, 3)
Start-Sleep -Milliseconds 500
[void][DevopsLabWindowCapture]::GetWindowRect($window, [ref]$outer)
$width = [int]($outer.Right - $outer.Left)
$height = [int]($outer.Bottom - $outer.Top)
$bitmap = [System.Drawing.Bitmap]::new($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$dc = $graphics.GetHdc()
$printed = [DevopsLabWindowCapture]::PrintWindow($window, $dc, 2)
$graphics.ReleaseHdc($dc)
if (-not $printed) { $graphics.CopyFromScreen($outer.Left, $outer.Top, 0, 0, $bitmap.Size) }
$name = switch ($Experiment) {
    'smoke' { 'powershell-local-app.png' }
    'docker' { 'powershell-docker-attempt.png' }
    'docker-run' { 'powershell-docker-run.png' }
    'kubernetes' { 'powershell-kubernetes-attempt.png' }
    'kubernetes-scale' { 'powershell-kubernetes-scale.png' }
    'rollout' { 'powershell-rollout-attempt.png' }
    'rollout-rollback' { 'powershell-rollout-rollback.png' }
    'cd-deploy' { 'powershell-cd-deploy.png' }
    'continuous-deployment' { 'powershell-cd-config.png' }
}
$path = Join-Path $ProjectRoot "evidence\screenshots\$name"
New-Item -ItemType Directory -Force (Split-Path $path) | Out-Null
$bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose(); $bitmap.Dispose()
Write-Host "`nPowerShell window screenshot saved: $path" -ForegroundColor Green
Start-Sleep -Seconds 2
} catch {
    $diagnostic = Join-Path $ProjectRoot 'evidence\logs\powershell-capture-error.txt'
    New-Item -ItemType Directory -Force (Split-Path $diagnostic) | Out-Null
    ($_ | Out-String) | Set-Content -Encoding utf8 $diagnostic
    throw
}
