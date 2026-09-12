@echo off
echo Compiling screen shake program with GDI...
g++ -o shake.exe shake.cpp -luser32 -lgdi32

if %errorlevel% neq 0 (
    echo Compilation failed. Make sure MinGW is installed.
    echo Install MinGW from: https://github.com/niXman/mingw-builds-binaries/releases
    pause
    exit /b 1
)

echo Compilation successful!
echo Running screen shake for 10 seconds...
shake.exe

pause
