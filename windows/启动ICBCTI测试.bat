@echo off
rem ICBCTI 人格测试 一键启动（双击运行）
chcp 65001 >nul
cd /d D:\code\0901ICBCTI\windows
if exist "D:\Anaconda\envs\mike\python.exe" (
    "D:\Anaconda\envs\mike\python.exe" icbcti_game.py
) else (
    call conda activate mike
    python icbcti_game.py
)
if errorlevel 1 pause
