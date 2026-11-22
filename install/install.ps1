# Writing Mentor installer for Windows 10 and 11.
# Installs what is missing (Git, Python, poppler, Tesseract, Claude Code), downloads the
# framework to %USERPROFILE%\writing-mentor-framework, and adds the /mentor command.
# Safe to run again: it updates the framework and skips what is already installed.
#
# Optional settings (for testing):
#   WMF_SOURCE  copy the framework from this folder instead of downloading it
#   WMF_BRANCH  download this branch instead of main
# Keep this file ASCII-only: Windows PowerShell 5.1 misreads other characters.

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Repo = 'Black-JL/writing-mentor-framework'
$Branch = if ($env:WMF_BRANCH) { $env:WMF_BRANCH } else { 'main' }
$Target = Join-Path $HOME 'writing-mentor-framework'

function Say($msg) { Write-Host $msg }
function Step($msg) { Write-Host ''; Write-Host "== $msg" -ForegroundColor Cyan }
function Fail($msg) {
    Write-Host ''
    Write-Host "Setup stopped: $msg" -ForegroundColor Red
    exit 1
}
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                [Environment]::GetEnvironmentVariable('Path', 'User')
}
function First-Existing($patterns) {
    foreach ($p in $patterns) {
        $hit = Get-ChildItem -Path $p -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
        if ($hit) { return $hit.FullName }
    }
    return $null
}
function Find-Command($name, $patterns) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue | Where-Object { $_.Source -notmatch 'WindowsApps' } | Select-Object -First 1
    if ($cmd) { return $cmd.Source }
    return First-Existing $patterns
}

function Find-Python {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        $exe = & $py.Source -3 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
    }
    return Find-Command 'python' @(
        "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe",
        "$env:ProgramFiles\Python3*\python.exe")
}
function Find-Git { Find-Command 'git' @("$env:ProgramFiles\Git\cmd\git.exe") }
# pdftoppm, not pdftotext: some programs (e.g. Git, TeX) ship pdftotext alone.
function Find-Poppler { Find-Command 'pdftoppm' @(
        "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\oschwartz10612.Poppler*\poppler-*\Library\bin\pdftoppm.exe",
        "$env:ProgramFiles\poppler*\Library\bin\pdftoppm.exe") }
function Find-Tesseract { Find-Command 'tesseract' @(
        "$env:ProgramFiles\Tesseract-OCR\tesseract.exe",
        "${env:ProgramFiles(x86)}\Tesseract-OCR\tesseract.exe",
        "$env:LOCALAPPDATA\Programs\Tesseract-OCR\tesseract.exe") }
function Find-Claude { Find-Command 'claude' @("$HOME\.local\bin\claude.exe") }

function Install-Package($id, $label, $finder) {
    $found = & $finder
    if ($found) { Say "  $label is already installed."; return }
    Say "  Installing $label (Windows may ask for permission)..."
    winget install -e --id $id --silent --accept-source-agreements --accept-package-agreements --disable-interactivity | Out-Host
    Refresh-Path
    if (-not (& $finder)) { Fail "$label could not be installed. Try again, or install it by hand: winget install -e --id $id" }
    Say "  $label installed."
}

Say ''
Say 'Writing Mentor setup'
Say '--------------------'
Say 'This installs the programs the Writing Mentor needs (Git, Python, poppler for'
Say 'PDFs, Tesseract for scanned pages, and Claude Code), puts the framework in'
Say "$Target, and adds the /mentor command to Claude Code."
Say 'Programs that are already installed are left alone.'

Step 'Checking for winget (the Windows package installer)'
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Fail ('winget is missing. Install "App Installer" from the Microsoft Store, ' +
          'then run this setup again. If your computer is managed by your organization, ' +
          'ask IT to install App Installer.')
}
Say '  Found.'

Step 'Installing programs'
Install-Package 'Git.Git' 'Git' ${function:Find-Git}
Install-Package 'Python.Python.3.12' 'Python' ${function:Find-Python}
Install-Package 'oschwartz10612.Poppler' 'poppler (reads PDFs)' ${function:Find-Poppler}
Install-Package 'UB-Mannheim.TesseractOCR' 'Tesseract (reads scanned pages)' ${function:Find-Tesseract}

if (Find-Claude) {
    Say '  Claude Code is already installed.'
} else {
    Say '  Installing Claude Code...'
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://claude.ai/install.ps1 | iex" | Out-Host
    Refresh-Path
    $env:Path = "$HOME\.local\bin;" + $env:Path
    if (-not (Find-Claude)) { Fail 'Claude Code could not be installed. See https://code.claude.com/docs/en/setup' }
    Say '  Claude Code installed.'
}

Step "Getting the Writing Mentor framework"
$staging = Join-Path ([IO.Path]::GetTempPath()) ("wmf-" + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $staging | Out-Null
try {
    if ($env:WMF_SOURCE) {
        Say "  Copying from $env:WMF_SOURCE"
        $src = $env:WMF_SOURCE
    } else {
        $zip = Join-Path $staging 'framework.zip'
        Say "  Downloading from github.com/$Repo ($Branch)"
        Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/$Repo/archive/refs/heads/$Branch.zip" -OutFile $zip
        Expand-Archive -Path $zip -DestinationPath $staging
        $src = (Get-ChildItem -Path $staging -Directory | Select-Object -First 1).FullName
    }

    if (Test-Path (Join-Path $Target '.git')) {
        Say "  $Target is a Git copy; leaving its files alone (update it with: git pull)."
    } else {
        New-Item -ItemType Directory -Force -Path $Target | Out-Null
        # Replace everything except the private Python environment
        Get-ChildItem -Path $Target -Force | Where-Object { $_.Name -ne '.venv' } | Remove-Item -Recurse -Force
        Get-ChildItem -Path $src -Force | Where-Object { $_.Name -notin @('.git', '.venv', '.github') } |
            Copy-Item -Destination $Target -Recurse -Force
        Say "  Framework is in $Target"
    }
} finally {
    Remove-Item -Recurse -Force $staging -ErrorAction SilentlyContinue
}

Step 'Setting up Python packages'
$python = Find-Python
if (-not $python) { Fail 'Python was installed but cannot be found. Close this window and run setup again.' }
$venv = Join-Path $Target '.venv'
$vpy = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $vpy)) { & $python -m venv $venv; if ($LASTEXITCODE -ne 0) { Fail 'could not create the Python environment.' } }
& $vpy -m pip install --quiet --disable-pip-version-check --upgrade olefile python-docx
if ($LASTEXITCODE -ne 0) { Fail 'could not install the Python packages (olefile, python-docx).' }
Say '  Done.'

Step 'Adding the /mentor command to Claude Code'
$skillDir = Join-Path $HOME '.claude\skills\mentor'
New-Item -ItemType Directory -Force -Path $skillDir | Out-Null
$template = [IO.File]::ReadAllText((Join-Path $Target 'skills\mentor\SKILL.md'))
$skill = $template.Replace('{{FRAMEWORK}}', ($Target -replace '\\', '/')).Replace('{{PYTHON}}', ($vpy -replace '\\', '/'))
[IO.File]::WriteAllText((Join-Path $skillDir 'SKILL.md'), $skill, (New-Object Text.UTF8Encoding $false))
Say "  Added: $skillDir\SKILL.md"

Step 'Checking everything'
& $vpy (Join-Path $Target 'skills\feedback\scripts\check_dependencies.py')
$checkCode = $LASTEXITCODE

Say ''
Say '--------------------'
if ($checkCode -eq 0) { Say 'Setup finished.' } else { Say 'Setup finished, but some items above are missing. Run setup again to retry.' }
Say ''
Say 'Next:'
Say '  1. In Cursor, install the "Claude Code" extension (Extensions panel, search "Claude Code"),'
Say '     or use the Code tab in the Claude desktop app.'
Say '  2. Open the folder that holds the writers'' files.'
Say '  3. Open Claude Code, sign in with your Claude account if asked, and type:  /mentor'
Say ''
Say 'To update later, run this setup again.'
exit $checkCode
