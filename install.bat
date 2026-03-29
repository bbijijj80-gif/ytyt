@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: Check Admin Rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ================================================================
    echo ERROR: Administrator rights required!
    echo Right-click this file and select "Run as administrator"
    echo ================================================================
    pause
    exit /b 1
)

echo ================================================================
echo   Windows 11 Security Hardener - Installation
echo ================================================================
echo.
echo [1/6] Checking system requirements...

:: Check Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.x from python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo [+] Python found.

:: Change to script directory
cd /d "%~dp0"

:: Check source code
if not exist "src\main.py" (
    echo ERROR: src\main.py not found!
    echo Ensure the src folder and main.py are next to install.bat
    pause
    exit /b 1
)
echo [+] Source code found.

echo.
echo [2/6] Installing dependencies (PyInstaller)...
pip install pyinstaller --quiet
if %errorLevel% neq 0 (
    echo ERROR: Failed to install PyInstaller. Check internet connection.
    pause
    exit /b 1
)
echo [+] PyInstaller installed.

echo.
echo [3/6] Compiling program to EXE...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

pyinstaller --onefile --windowed --name "WinSecHardener" --icon=NONE src/main.py
if %errorLevel% neq 0 (
    echo ERROR: Compilation failed. Check main.py for syntax errors.
    pause
    exit /b 1
)

if not exist "dist\WinSecHardener.exe" (
    echo ERROR: WinSecHardener.exe was not created.
    pause
    exit /b 1
)
echo [+] Program compiled successfully.

echo.
echo [4/6] Installing to system...
set "INSTALL_DIR=C:\Program Files\WinSecHardener"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

copy /Y "dist\WinSecHardener.exe" "%INSTALL_DIR%\WinSecHardener.exe" >nul
echo [+] File copied to %INSTALL_DIR%

echo.
echo [5/6] Configuring access rights (ACL)...
icacls "%INSTALL_DIR%" /grant Administrators:(OI)(CI)F /grant SYSTEM:(OI)(CI)F /inheritance:r >nul
icacls "%INSTALL_DIR%\WinSecHardener.exe" /grant Administrators:F /grant SYSTEM:F /remove:g Users >nul
echo [+] Access rights configured.

echo.
echo [6/6] Creating desktop shortcut...
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_DIR%\WinSecHardener.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\WinSecHardener.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'WinSecHardener (Admin Only)'; $Shortcut.Save()"

if exist "%DESKTOP_DIR%\WinSecHardener.lnk" (
    echo [+] Desktop shortcut created.
) else (
    echo [-] Failed to create shortcut automatically.
    echo     You can create it manually from: %INSTALL_DIR%
)

:: Cleanup
rmdir /s /q "build"
rmdir /s /q "dist"

echo.
echo ================================================================
echo   INSTALLATION COMPLETED SUCCESSFULLY!
echo ================================================================
echo.
echo Installed to: %INSTALL_DIR%
echo Shortcut created on Desktop.
echo.
echo IMPORTANT:
echo - Run the program ONLY as Administrator.
echo - Standard users cannot delete or modify this program.
echo - To uninstall, delete the folder %INSTALL_DIR% (requires Admin).
echo.
pause
