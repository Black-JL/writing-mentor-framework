@echo off
rem Writing Mentor Framework CLI for Windows (Command Prompt and PowerShell)
rem   wmf init [path]   Set up a folder for reviewing submissions
rem   wmf claude        Open Claude Code in the current folder
rem   wmf help          Show this help
setlocal
set "FRAMEWORK_DIR=%~dp0.."
set "CMD=%~1"
if "%CMD%"=="" set "CMD=help"

if /I "%CMD%"=="init" (
    if "%~2"=="" (
        python "%FRAMEWORK_DIR%\scripts\init_project.py" --target "%CD%" --framework "%FRAMEWORK_DIR%" --force
    ) else (
        python "%FRAMEWORK_DIR%\scripts\init_project.py" --target "%~2" --framework "%FRAMEWORK_DIR%" --force
    )
    exit /b %ERRORLEVEL%
)
if /I "%CMD%"=="claude" (
    claude
    exit /b %ERRORLEVEL%
)
echo Writing Mentor Framework
echo.
echo Usage:
echo   wmf init [path]   Set up a folder (default: the current folder)
echo   wmf claude        Open Claude Code in the current folder
echo   wmf help          Show this help
echo.
echo Then put assignment.md, rubric.md and the writers' files (in submissions\) in the folder,
echo open Claude Code there and type /feedback
exit /b 0
