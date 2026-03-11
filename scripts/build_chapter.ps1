$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory = $true)]
    [string]$ChapterDir
)

$chapterPath = Resolve-Path -LiteralPath $ChapterDir -ErrorAction Stop
$chapterScript = Join-Path $chapterPath "scripts/build.ps1"

if (-not (Test-Path -LiteralPath $chapterScript)) {
    throw "Chapter build script not found: $chapterScript"
}

& powershell -ExecutionPolicy Bypass -File $chapterScript
if ($LASTEXITCODE -ne 0) {
    throw "Build failed for chapter: $chapterPath"
}
