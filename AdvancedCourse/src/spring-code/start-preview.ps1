param([int]$Port = 18780)

$ErrorActionPreference = 'Stop'
if ($Port -lt 1024 -or $Port -gt 65535) {
    throw 'Choose a preview port between 1024 and 65535.'
}

# This task keeps its portable JDK outside the source checkout.
$runtimeFolder = Join-Path $PSScriptRoot '..\..\..\..\tools'
$portableJdk = Get-ChildItem -LiteralPath $runtimeFolder -Directory -Filter 'jdk-17*' -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($portableJdk) {
    $env:JAVA_HOME = $portableJdk.FullName
}
if (-not $env:JAVA_HOME -or -not (Test-Path -LiteralPath (Join-Path $env:JAVA_HOME 'bin\javac.exe'))) {
    throw 'Set JAVA_HOME to a Java 17 or newer JDK, then run this script again.'
}

Write-Host "Preview: http://127.0.0.1:$Port/"
Write-Host 'Press Ctrl+C to stop the preview server.'
Push-Location -LiteralPath $PSScriptRoot
try {
    & .\mvnw.cmd -q -ntp spring-boot:run "-Dspring-boot.run.arguments=--server.address=127.0.0.1 --server.port=$Port --spring.thymeleaf.cache=false"
    if ($LASTEXITCODE -ne 0) { throw "Preview server exited with code $LASTEXITCODE." }
}
finally {
    Pop-Location
}
