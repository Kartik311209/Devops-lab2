$ErrorActionPreference = 'Stop'
$base = if ($env:APP_URL) { $env:APP_URL.TrimEnd('/') } else { 'http://127.0.0.1:8080' }
$checks = @('/healthz', '/readyz', '/api/info')
foreach ($path in $checks) {
    $response = Invoke-RestMethod -Uri "$base$path" -TimeoutSec 5
    "PASS $path"
    $response | ConvertTo-Json -Depth 5
}
