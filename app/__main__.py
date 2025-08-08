# Run the app as a module: python -m app
from .main import run

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
