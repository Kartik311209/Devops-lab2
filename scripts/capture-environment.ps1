$ErrorActionPreference = 'Continue'
$MinikubeBin = Join-Path $env:LOCALAPPDATA 'Programs\minikube'
if (Test-Path (Join-Path $MinikubeBin 'minikube.exe')) { $env:Path = "$MinikubeBin;$env:Path" }
$root = Split-Path -Parent $PSScriptRoot
$target = Join-Path $root 'evidence\logs\environment-status.txt'
$lines = [System.Collections.Generic.List[string]]::new()
foreach ($cmd in @(
    @{ Name = 'docker version'; File = 'docker'; Args = @('version') },
    @{ Name = 'kubectl version --client=true'; File = 'kubectl'; Args = @('version','--client=true') },
    @{ Name = 'kubectl config get-contexts'; File = 'kubectl'; Args = @('config','get-contexts') },
    @{ Name = 'minikube version'; File = 'minikube'; Args = @('version') }
)) {
    $lines.Add("PS> $($cmd.Name)")
    $resolved = Get-Command $cmd.File -ErrorAction SilentlyContinue
    if (-not $resolved) {
        $lines.Add("NOT FOUND: $($cmd.File)")
    } else {
        $result = & $cmd.File @($cmd.Args) 2>&1 | Out-String
        $lines.Add($result.TrimEnd())
        $lines.Add("exit_code=$LASTEXITCODE")
    }
    $lines.Add('')
}
New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
$lines | Set-Content -Encoding utf8 $target
Get-Content $target
