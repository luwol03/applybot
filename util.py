from typing import Optional

from PyDrocsid.settings import Settings
from PyDrocsid.translations import translations
from discord import Embed
from discord.abc import Messageable


def make_error(message) -> Embed:
    return Embed(title=translations.error, colour=0xCF0606, description=translations.f_error_string(message))


async def get_prefix() -> str:
    return await Settings.get(str, "prefix", ".")


async def set_prefix(new_prefix: str):
    await Settings.set(str, "prefix", new_prefix)


async def send_editable_log(channel: Messageable, title: str, name: str, value: str,
                            colour: Optional[int] = 0x008080, inline: Optional[bool] = False,
                            force_resend: Optional[bool] = False, force_new_embed: Optional[bool] = False):
    messages = await channel.history(limit=1).flatten()
    if messages and messages[0].embeds and force_new_embed is False:
        embed = messages[0].embeds[0]
        if embed.title == title:
            if embed.fields and embed.fields[-1].name == name:
                embed.set_field_at(index=-1, name=name, value=value, inline=inline)
            elif len(embed.fields) < 25:
                embed.add_field(name=name, value=value, inline=inline)
            else:
                return
            if force_resend:
                await messages[0].delete()
                await channel.send(embed=embed)
                return
            await messages[0].edit(embed=embed)
            return

    embed = Embed(title=title, colour=colour)
    embed.add_field(name=name, value=value, inline=inline)
    await channel.send(embed=embed)
