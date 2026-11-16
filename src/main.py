import argparse
import json
import os
import subprocess
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
        raise ValueError("Ошибка: файл должен иметь расширение .svg/.png/.d2.")
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


def generate_d2_text(graph):
    lines = ["direction: down"]
    for pkg, deps in graph.items():
        if not deps:
            lines.append(f'"{pkg}"')
        for dep in deps:
            lines.append(f'"{pkg}" -> "{dep}"')
    return "\n".join(lines) + "\n"


def save_graph_image(d2_text, output_path):
    if output_path.endswith(".d2"):
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(d2_text)
        print(f"Описание графа D2 сохранено в '{output_path}'.")
        return

    d2_temp = f"{output_path}.d2"
    with open(d2_temp, "w", encoding="utf-8") as file:
        file.write(d2_text)

    try:
        subprocess.run(
            ["d2", d2_temp, output_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.remove(d2_temp)
        print(f"Изображение графа сохранено в '{output_path}'.")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(f"Утилита d2 не найдена. Исходник D2 сохранён в '{d2_temp}'.")


def print_ascii_tree(start_pkg, graph):
    print("ASCII-дерево зависимостей:")
    print(start_pkg)
    stack = []
    root_deps = graph.get(start_pkg, [])
    for idx in range(len(root_deps) - 1, -1, -1):
        is_last = idx == len(root_deps) - 1
        stack.append((root_deps[idx], "", is_last, {start_pkg}))

    while stack:
        pkg, prefix, is_last, path = stack.pop()
        connector = "└── " if is_last else "├── "
        if pkg in path:
            print(f"{prefix}{connector}{pkg} (цикл)")
            continue
        print(f"{prefix}{connector}{pkg}")
        new_prefix = prefix + ("    " if is_last else "│   ")
        new_path = path | {pkg}
        deps = graph.get(pkg, [])
        for idx in range(len(deps) - 1, -1, -1):
            child_last = idx == len(deps) - 1
            stack.append((deps[idx], new_prefix, child_last, new_path))


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

        graph, _ = build_dependency_graph(
            args.package, args.max_depth, get_deps
        )
        d2_text = generate_d2_text(graph)
        print("Представление графа на языке D2:")
        print(d2_text.strip())
        save_graph_image(d2_text, args.output)
        if args.ascii:
            print_ascii_tree(args.package, graph)
    except ValueError as error:
        print(error, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
