from .resolver import _ENCODED_PATTERN, Resolver


def main():
    app = typer.Typer()

    @app.command("decode", help="Decode the text")
    def decode(encoded_text: str, pattern: str = _ENCODED_PATTERN):
        resolver = Resolver(pattern)
        print(resolver.decode_to_json(encoded_text))

    app()


if __name__ == "__main__":
    try:
        # test if the optional dependency is installed
        import typer  # noqa: F401

        main()
    except ImportError:
        print("To use Wynntils Resolver from command-line, please install wynntillsresolver[cli]")
        exit(0)
