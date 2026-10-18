$ErrorActionPreference = 'Stop'
$taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$taskSavedPath = $env:PATH
$taskDistribution = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'dist\TaskList'))
$taskExpectedRoot = [System.IO.Path]::GetFullPath($PSScriptRoot) + [System.IO.Path]::DirectorySeparatorChar

if (-not $taskDistribution.StartsWith($taskExpectedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Папка сборки должна находиться внутри проекта.'
}
if (-not (Test-Path -LiteralPath $taskPython)) {
    throw 'Сначала создайте .venv и установите requirements-build.txt.'
}

Push-Location $PSScriptRoot
try {
    # Исключаем сторонние DLL из PATH на время сборки.
    $env:PATH = "$env:SystemRoot\System32;$env:SystemRoot;$PSScriptRoot\.venv\Scripts"
    & $taskPython -m PyInstaller --noconfirm --clean --onedir --windowed --contents-directory . --name TaskList main.py
    if ($LASTEXITCODE -ne 0) {
        throw 'Не удалось собрать приложение.'
    }
}
finally {
    $env:PATH = $taskSavedPath
    Pop-Location
}
