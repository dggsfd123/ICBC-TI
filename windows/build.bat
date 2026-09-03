@echo off
rem ICBC-TI 人格测试 —— 打包为 Windows 单文件可执行程序
rem 生成结果：D:\code\0901ICBCTI\windows\dist\ICBC-TI人格测试.exe
chcp 65001 >nul
cd /d D:\code\0901ICBCTI\windows

set PY=D:\Anaconda\envs\mike\python.exe
if not exist "%PY%" set PY=python
set BIN=D:\Anaconda\envs\mike\Library\bin

"%PY%" -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "ICBC-TI人格测试" ^
  --icon app.ico ^
  --add-data "icbcti;icbcti" ^
  --add-binary "%BIN%\tcl86t.dll;." ^
  --add-binary "%BIN%\tk86t.dll;." ^
  --add-binary "%BIN%\liblzma.dll;." ^
  --add-binary "%BIN%\libbz2.dll;." ^
  --add-binary "%BIN%\libcrypto-1_1-x64.dll;." ^
  --add-binary "%BIN%\libssl-1_1-x64.dll;." ^
  --hidden-import "tkinter" ^
  --hidden-import "tkinter.filedialog" ^
  icbcti_game.py

if errorlevel 1 goto :fail
echo.
echo ============================================
echo  打包完成：dist\ICBC-TI人格测试.exe
echo ============================================
pause
exit /b 0

:fail
echo.
echo 打包失败，请检查上方错误信息。
pause
exit /b 1
