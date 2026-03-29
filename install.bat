@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Проверка прав администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo =====================================================
    echo   Windows 11 Security Hardener - Установка
    echo =====================================================
    echo.
    echo ОШИБКА: Эта программа должна быть запущена от имени администратора
    echo.
    echo Щелкните правой кнопкой мыши на install.bat и выберите
    echo "Запуск от имени администратора"
    echo.
    pause
    exit /b 1
)

echo =====================================================
echo   Windows 11 Security Hardener - Установка
echo =====================================================
echo.
echo [1/6] Проверка прав администратора... OK
echo.

:: Создание директорий
echo [2/6] Создание директорий...
set "INSTALL_DIR=C:\Program Files\WinSecHardener"
set "LOG_DIR=C:\ProgramData\WinSecHardener"

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo   - Создана папка установки: %INSTALL_DIR%
)

if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
    echo   - Создана папка логов: %LOG_DIR%
)
echo.

:: Установка Python зависимостей
echo [3/6] Установка зависимостей Python...
cd /d "%~dp0src"
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
    echo   - Зависимости установлены
) else (
    echo   - Файл requirements.txt не найден, пропускаем
)
echo.

:: Компиляция в EXE
echo [4/6] Компиляция программы в EXE...
pip install pyinstaller --quiet
pyinstaller --onefile --windowed --name "WinSecHardener" --icon=NONE main.py --quiet
if exist "dist\WinSecHardener.exe" (
    copy /Y "dist\WinSecHardener.exe" "%INSTALL_DIR%" >nul
    echo   - Программа скомпилирована и скопирована в %INSTALL_DIR%
) else (
    echo   - ОШИБКА: Не удалось создать EXE файл
    echo   - Пробуем копировать исходный скрипт...
    copy /Y "main.py" "%INSTALL_DIR%" >nul
)
echo.

:: Настройка прав доступа (ACL)
echo [5/6] Настройка прав доступа...
icacls "%INSTALL_DIR%" /grant Administrators:F /inheritance:r >nul
icacls "%INSTALL_DIR%" /grant Users:RX /inheritance:r >nul
echo   - Доступ разрешен только администраторам
echo.

:: Создание ярлыка
echo [6/6] Создание ярлыка на рабочем столе...
set "DESKTOP=%USERPROFILE%\Desktop"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\WinSecHardener.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\WinSecHardener.exe'; If (!(Test-Path '%INSTALL_DIR%\WinSecHardener.exe')) { $Shortcut.TargetPath = 'pythonw.exe'; $Shortcut.Arguments = '%INSTALL_DIR%\main.py' }; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Windows 11 Security Hardener'; $Shortcut.Save()"

if exist "%DESKTOP%\WinSecHardener.lnk" (
    echo   - Ярлык создан на рабочем столе
) else (
    echo   - Предупреждение: Не удалось создать ярлык
)
echo.

:: Завершение
echo =====================================================
echo   Установка завершена успешно!
echo =====================================================
echo.
echo Программа установлена в: %INSTALL_DIR%
echo Ярлык создан на рабочем столе
echo.
echo ВАЖНО: Для запуска программы щелкните правой кнопкой
echo мыши на ярлыке и выберите "Запуск от имени администратора"
echo.
echo Логирование включено: %LOG_DIR%\audit.log
echo.
pause
