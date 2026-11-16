@echo off
chcp 65001 > nul
echo === Корректный запуск ===
python src/main.py --package express --repo https://npmjs.org --output graph.svg --ascii --max-depth 3

echo.
echo === Демонстрация обработки ошибок ===
python src/main.py --package "" --repo invalid_url --max-depth 0
pause
