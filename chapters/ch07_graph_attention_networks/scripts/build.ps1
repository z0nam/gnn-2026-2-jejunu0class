$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ChapterDir = Resolve-Path (Join-Path $ScriptDir "..")
$SlidesDir = Join-Path $ChapterDir "slides"
$NotesDir = Join-Path $ChapterDir "notes"
$BuildDir = Join-Path $ChapterDir "build"
$OutputDir = Join-Path $ChapterDir "output"

New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function Compile-Latex {
    param(
        [string]$WorkDir,
        [string]$InputTex
    )

    Push-Location $WorkDir
    try {
        & xelatex -interaction=nonstopmode -halt-on-error -output-directory $BuildDir $InputTex | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "LaTeX build failed: $InputTex"
        }
    }
    finally {
        Pop-Location
    }
}

Compile-Latex -WorkDir $SlidesDir -InputTex "ch07_beamer.tex"
Compile-Latex -WorkDir $SlidesDir -InputTex "ch07_handout.tex"
Compile-Latex -WorkDir $SlidesDir -InputTex "ch07_handout_text.tex"
Compile-Latex -WorkDir $NotesDir -InputTex "ch07_summary.tex"

Copy-Item -Force (Join-Path $BuildDir "ch07_beamer.pdf") (Join-Path $OutputDir "ch07_beamer.pdf")
Copy-Item -Force (Join-Path $BuildDir "ch07_handout.pdf") (Join-Path $OutputDir "ch07_handout.pdf")
Copy-Item -Force (Join-Path $BuildDir "ch07_handout_text.pdf") (Join-Path $OutputDir "ch07_handout_text.pdf")
Copy-Item -Force (Join-Path $BuildDir "ch07_summary.pdf") (Join-Path $OutputDir "ch07_summary.pdf")

Write-Host "Build complete. PDFs are in: $OutputDir"
