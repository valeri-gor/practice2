import argparse
import json
import os
import sys
import urllib.error
import urllib.request

MIN_DEPTH = 1
ALLOWED_EXTENSIONS = (".svg", ".png", ".d2")


def parse_arguments():
    parser = argparse.ArgumentParser(description="NPM Dependency Visualizer")
    parser.add_argument("--package", type=str, required=True)
    parser.add_argument("--repo", type=str, required=True)
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--output", type=str, default="graph.svg")
    parser.add_argument("--ascii", action="store_true")
    parser.add_argument("--max-depth", type=int, default=3)
    return parser.parse_args()


def validate_arguments(args):
    if not args.package.strip():
        raise ValueError("Ошибка: имя пакета не может быть пустым.")
    if not args.repo.strip():
        raise ValueError("Ошибка: путь или URL репозитория не задан.")
    if args.test_mode and not os.path.isfile(args.repo):
        raise ValueError(f"Ошибка: тестовый файл '{args.repo}' не найден.")
    is_http = args.repo.startswith(("http://", "https://"))
    if not args.test_mode and not is_http:
        raise ValueError("Ошибка: URL должен начинаться с http или https.")
    if not args.output.strip().endswith(ALLOWED_EXTENSIONS):
        raise ValueError("Ошибка: файл должен иметь расширение .svg или .png.")
    if args.max_depth < MIN_DEPTH:
        raise ValueError("Ошибка: глубина анализа должна быть не меньше 1.")


def load_test_repo(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as error:
        raise ValueError(f"Ошибка чтения тестового файла: {error}")
    if not isinstance(data, dict):
        raise ValueError("Ошибка: тестовый файл должен содержать JSON-словарь.")
    return data


def fetch_npm_dependencies(package_name, repo_url):
    base_url = repo_url.rstrip("/")
    url = f"{base_url}/{package_name}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            msg = f"Ошибка HTTP 404: пакет '{package_name}' не найден."
            raise ValueError(msg)
        raise ValueError(f"Ошибка HTTP {error.code}: ошибка сервера.")
    except Exception as error:
        raise ValueError(f"Ошибка сети: {error}")

    latest = data.get("dist-tags", {}).get("latest", "")
    versions = data.get("versions", {})
    deps = versions.get(latest, {}).get("dependencies", {})
    return list(deps.keys())


def build_dependency_graph(start_pkg, max_depth, get_deps_func):
    graph = {}
    cycles = []
    stack = [(start_pkg, 0, [start_pkg])]

    while stack:
        current_pkg, depth, path = stack.pop()
        if current_pkg not in graph:
            graph[current_pkg] = []

        if depth >= max_depth:
            continue

        deps = get_deps_func(current_pkg)
        for dep in reversed(deps):
            if dep not in graph[current_pkg]:
                graph[current_pkg].append(dep)
            if dep in path:
                cycles.append((current_pkg, dep))
            elif dep not in graph:
                stack.append((dep, depth + 1, path + [dep]))

    return graph, cycles


def get_load_order(start_pkg, graph):
    visited = set()
    order = []
    stack = [(start_pkg, False)]

    while stack:
        pkg, processed = stack.pop()
        if processed:
            if pkg not in order:
                order.append(pkg)
            continue
        if pkg in visited:
            continue
        visited.add(pkg)
        stack.append((pkg, True))
        for dep in reversed(graph.get(pkg, [])):
            if dep not in visited:
                stack.append((dep, False))

    return order


def print_stage4_output(start_pkg, graph, cycles, load_order):
    print(f"Граф зависимостей для '{start_pkg}':")
    for pkg, deps in graph.items():
        deps_str = ", ".join(deps) if deps else "нет"
        print(f"  {pkg} -> {deps_str}")

    if cycles:
        print("Обнаружены циклические зависимости:")
        for src, dst in cycles:
            print(f"  {src} -> {dst} (цикл)")

    print("Порядок загрузки зависимостей:")
    print("  " + " -> ".join(load_order))


def main():
    try:
        args = parse_arguments()
        validate_arguments(args)
        if args.test_mode:
            test_data = load_test_repo(args.repo)
            if args.package not in test_data:
                raise ValueError(f"Ошибка: пакет '{args.package}' не найден.")
            get_deps = lambda pkg: test_data.get(pkg, [])
        else:
            get_deps = lambda pkg: fetch_npm_dependencies(pkg, args.repo)

        graph, cycles = build_dependency_graph(
            args.package, args.max_depth, get_deps
        )
        load_order = get_load_order(args.package, graph)
    except ValueError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    print_stage4_output(args.package, graph, cycles, load_order)


if __name__ == "__main__":
    main()
