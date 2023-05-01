from .resolver import Resolver as Resolver


resolver = Resolver()
__all__ = ["Resolver","resolver"]


if __name__ == "__main__":
    from .cli import main
    main()