param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$')]
    [string]$ImageTag
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$MinikubeBin = Join-Path $env:LOCALAPPDATA 'Programs\minikube'
if (Test-Path (Join-Path $MinikubeBin 'minikube.exe')) { $env:Path = "$MinikubeBin;$env:Path" }
$Image = "devops-lab2:$ImageTag"

function Invoke-DeployStep([string]$Label, [scriptblock]$Action, [switch]$TailOnly) {
    Write-Host "`n[deploy] $Label" -ForegroundColor Cyan
    $Output = @(& $Action 2>&1)
    $ExitCode = $LASTEXITCODE
    if ($null -eq $ExitCode) { $ExitCode = 0 }
    if ($TailOnly) { $Output = @($Output | Select-Object -Last 1) }
    foreach ($Line in $Output) { Write-Host ([string]$Line) }
    if ($ExitCode -ne 0) { throw "Step failed with exit code ${ExitCode}: $Label" }
}

Write-Host "DevOps Lab 2 local CD | image=$Image | student=Kartik Kumar | roll=2301730205"
Invoke-DeployStep "docker build --quiet -t $Image ." { docker build --quiet -t $Image . }
Invoke-DeployStep "minikube image load $Image" { minikube image load $Image }
Invoke-DeployStep 'kubectl apply -f .\k8s\namespace.yaml' { kubectl apply -f .\k8s\namespace.yaml }
Invoke-DeployStep 'kubectl apply -f .\k8s\deployment.yaml' { kubectl apply -f .\k8s\deployment.yaml }
Invoke-DeployStep "kubectl -n devops-lab2 set image deployment/devops-lab2 web=$Image" { kubectl -n devops-lab2 set image deployment/devops-lab2 "web=$Image" }
Invoke-DeployStep "kubectl -n devops-lab2 set env deployment/devops-lab2 APP_VERSION=$ImageTag" { kubectl -n devops-lab2 set env deployment/devops-lab2 "APP_VERSION=$ImageTag" }
Invoke-DeployStep 'kubectl -n devops-lab2 rollout status deployment/devops-lab2 --timeout=120s' { kubectl -n devops-lab2 rollout status deployment/devops-lab2 --timeout=120s } -TailOnly
Write-Host "Deployment completed: $ImageTag" -ForegroundColor Green
