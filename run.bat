@echo off
chcp 65001 > nul
mkdir _tmp_npm > nul 2>&1
copy tests\mock_npm.json _tmp_npm\express > nul
start /b python -m http.server 8000 -d _tmp_npm > nul 2>&1
timeout /t 1 /nobreak > nul

echo === Получение прямых зависимостей пакета express ===
python src/main.py --package express --repo http://127.0.0.1:8000

echo.
echo === Проверка ошибки для несуществующего пакета ===
python src/main.py --package non-existent-pkg --repo http://127.0.0.1:8000

taskkill /f /im python.exe > nul 2>&1
rmdir /s /q _tmp_npm > nul 2>&1
pause
