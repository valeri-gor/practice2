import argparse
import os
import sys

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

    if not args.test_mode and not args.repo.startswith(("http://", "https://")):
        raise ValueError("Ошибка: URL должен начинаться с http или https.")

    if not args.output.strip().endswith(ALLOWED_EXTENSIONS):
        raise ValueError("Ошибка: файл должен иметь расширение .svg или .png.")

    if args.max_depth < MIN_DEPTH:
        raise ValueError("Ошибка: глубина анализа должна быть не меньше 1.")


def print_config(args):
    params = {
        "package": args.package,
        "repo": args.repo,
        "test_mode": args.test_mode,
        "output": args.output,
        "ascii": args.ascii,
        "max_depth": args.max_depth,
    }
    for key, value in params.items():
        print(f"{key}: {value}")


def main():
    try:
        args = parse_arguments()
        validate_arguments(args)
    except ValueError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    print_config(args)


if __name__ == "__main__":
    main()
