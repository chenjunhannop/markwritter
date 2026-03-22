"""Hello skill - Simple greeting."""

import argparse


def main() -> None:
    """Run hello skill."""
    parser = argparse.ArgumentParser(description="Greet someone")
    parser.add_argument(
        "--name",
        default="World",
        help="Name to greet",
    )

    args = parser.parse_args()
    print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()
