from .cz import CommitizenCLI


def main() -> int:
    return CommitizenCLI().run()


if __name__ == "__main__":
    raise SystemExit(main())
