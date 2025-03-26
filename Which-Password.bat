@echo off
setlocal enabledelayedexpansion

rem Get the current directory where the script is located
set "CURRENT_DIR=%~dp0"

rem Prompt for the file name
set /p "FILE_NAME=Enter the name of the archive file (with extension): "

rem Set the path for the password file
set "PASSWORD_FILE=%CURRENT_DIR%PWD.txt"

rem Check if the password file exists
if not exist "%PASSWORD_FILE%" (
    echo Password file not found: %PASSWORD_FILE%
    pause
    exit /b 1
)

rem Check if the specified file exists
if not exist "%CURRENT_DIR%!FILE_NAME!" (
    echo Archive file not found: "%CURRENT_DIR%!FILE_NAME!"
    pause
    exit /b 1
)

rem Determine the file extension
for %%A in ("!FILE_NAME!") do set "EXT=%%~xA"
echo File extension detected: !EXT!

rem Read passwords from the password file and try to extract the archive
for /f "delims=" %%p in (%PASSWORD_FILE%) do (
    echo Trying password: %%p

    rem Check the file extension and use the appropriate command
    if /i "!EXT!"==".rar" (
        "C:\Program Files\7-Zip\7z.exe" x "%CURRENT_DIR%!FILE_NAME!" -p"%%p" -y
    ) else if /i "!EXT!"==".zip" (
        "C:\Program Files\7-Zip\7z.exe" x "%CURRENT_DIR%!FILE_NAME!" -p"%%p" -y
    ) else if /i "!EXT!"==".7z" (
        "C:\Program Files\7-Zip\7z.exe" x "%CURRENT_DIR%!FILE_NAME!" -p"%%p" -y
    ) else (
        echo Unsupported file type: !EXT!
        pause
        exit /b 1
    )

    rem Check if the extraction was successful
    if !errorlevel! == 0 (
        echo Password found: %%p
        pause
        exit /b 0
    )
)

echo No valid password found.
pause
exit /b 1
