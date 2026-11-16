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


def fetch_npm_dependencies(package_name, repo_url):
    base_url = repo_url.rstrip("/")
    url = f"{base_url}/{package_name}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            raise ValueError("Ошибка HTTP 404: пакет не найден.")
        raise ValueError(f"Ошибка HTTP {error.code}: ошибка сервера.")
    except Exception as error:
        raise ValueError(f"Ошибка сети: {error}")

    latest = data.get("dist-tags", {}).get("latest", "")
    versions = data.get("versions", {})
    return versions.get(latest, {}).get("dependencies", {})




def print_dependencies(package_name, dependencies):
    print(f"Прямые зависимости пакета '{package_name}':")
    if not dependencies:
        print("Зависимости отсутствуют.")
        return
    for dep_name, dep_version in dependencies.items():
        print(f"- {dep_name}: {dep_version}")


def main():
    try:
        args = parse_arguments()
        validate_arguments(args)
        dependencies = fetch_npm_dependencies(args.package, args.repo)
    except ValueError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    print_dependencies(args.package, dependencies)


if __name__ == "__main__":
    main()
