from PyDrocsid.settings import Settings
from PyDrocsid.translations import translations
from discord import Embed


def make_error(message) -> Embed:
    return Embed(title=translations.error, colour=0xCF0606, description=translations.f_error_string(message))


async def get_prefix() -> str:
    return await Settings.get(str, "prefix", ".")


async def set_prefix(new_prefix: str):
    await Settings.set(str, "prefix", new_prefix)
