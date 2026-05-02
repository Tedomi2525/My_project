$ErrorActionPreference = "Stop"

$services = @(
    @{ Name = "gateway"; App = "gateway.main:app"; Port = 8100 },
    @{ Name = "auth-service"; App = "services.auth_service.main:app"; Port = 8101 },
    @{ Name = "user-service"; App = "services.user_service.main:app"; Port = 8102 },
    @{ Name = "class-service"; App = "services.class_service.main:app"; Port = 8103 },
    @{ Name = "question-service"; App = "services.question_service.main:app"; Port = 8104 },
    @{ Name = "exam-service"; App = "services.exam_service.main:app"; Port = 8105 },
    @{ Name = "result-service"; App = "services.result_service.main:app"; Port = 8106 }
)

$python = "python"
$localPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (Test-Path $localPython) {
    $python = $localPython
}

$logsDir = Join-Path $PSScriptRoot "logs"
New-Item -ItemType Directory -Force $logsDir | Out-Null

foreach ($service in $services) {
    $stdout = Join-Path $logsDir "$($service.Name).out.log"
    $stderr = Join-Path $logsDir "$($service.Name).err.log"

    Write-Host "Starting $($service.Name) on port $($service.Port)..."
    Start-Process -FilePath $python `
        -ArgumentList "-m", "uvicorn", $service.App, "--host", "127.0.0.1", "--port", $service.Port `
        -WorkingDirectory $PSScriptRoot `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -WindowStyle Hidden
}

Write-Host ""
Write-Host "API Gateway: http://127.0.0.1:8100"
Write-Host "Gateway docs: http://127.0.0.1:8100/docs"
Write-Host "Service health URLs:"
Write-Host "  http://127.0.0.1:8101/health"
Write-Host "  http://127.0.0.1:8102/health"
Write-Host "  http://127.0.0.1:8103/health"
Write-Host "  http://127.0.0.1:8104/health"
Write-Host "  http://127.0.0.1:8105/health"
Write-Host "  http://127.0.0.1:8106/health"
Write-Host ""
Write-Host "Logs: $logsDir"
