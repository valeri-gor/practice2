@echo off
chcp 65001 > nul
echo === 1. Визуализация пакета A (с циклом и ASCII-деревом) ===
python src/main.py --package A --repo tests/test_repo.json --test-mode --output graph_A.svg --ascii --max-depth 4

echo.
echo === 2. Визуализация пакета B (подграф с циклом) ===
python src/main.py --package B --repo tests/test_repo.json --test-mode --output graph_B.svg --ascii --max-depth 3

echo.
echo === 3. Визуализация пакета F (линейная цепочка без циклов) ===
python src/main.py --package F --repo tests/test_repo.json --test-mode --output graph_F.svg --ascii --max-depth 3
pause
