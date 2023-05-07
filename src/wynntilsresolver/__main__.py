"""
Author       : FYWinds i@windis.cn
Date         : 1969-12-31 19:00:00
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2023-05-07 17:42:26
FilePath     : /src/wynntilsresolver/__main__.py

Copyright (c) 2023 by FYWinds
All Rights Reserved.
Any modifications or distributions of the file
should mark the original author's name.
"""

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
