@echo off
chcp 65001 > nul
echo === Порядок загрузки зависимостей для пакета A (с циклом B - C) ===
python src/main.py --package A --repo tests/test_repo.json --test-mode --max-depth 4

echo.
echo === Порядок загрузки зависимостей для пакета F (без циклов) ===
python src/main.py --package F --repo tests/test_repo.json --test-mode --max-depth 4
pause
