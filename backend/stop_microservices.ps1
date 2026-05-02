$ports = @(8100, 8101, 8102, 8103, 8104, 8105, 8106)

foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        try {
            Stop-Process -Id $connection.OwningProcess -Force -ErrorAction Stop
            Write-Host "Stopped process $($connection.OwningProcess) on port $port"
        } catch {
            Write-Host "Could not stop process $($connection.OwningProcess) on port $port"
        }
    }
}
