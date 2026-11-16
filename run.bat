@echo off
chcp 65001 > nul
echo === Тестовый репозиторий (глубина 4, обнаружение цикла B - C) ===
python src/main.py --package A --repo tests/test_repo.json --test-mode --max-depth 4

echo.
echo === Тестовый репозиторий (ограничение глубины 2) ===
python src/main.py --package A --repo tests/test_repo.json --test-mode --max-depth 2
pause
