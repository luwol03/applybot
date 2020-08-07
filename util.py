from PyDrocsid.settings import Settings


def make_error(message) -> str:
    return f":x: Error: {message}"


async def get_prefix() -> str:
    return await Settings.get(str, "prefix", ".")


async def set_prefix(new_prefix: str):
    await Settings.set(str, "prefix", new_prefix)
