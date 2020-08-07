from typing import Optional

from PyDrocsid.translations import translations
from PyDrocsid.util import send_long_embed
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, Bot, guild_only, Context, CommandError, UserInputError

from permissions import Permission, PermissionLevel, PermissionLevelConverter


async def list_permissions(ctx: Context, title: str, min_level: PermissionLevel):
    out = {}
    for permission in Permission:  # type: Permission
        level = await permission.resolve()
        if min_level.value >= level.value:
            out.setdefault(level.value, []).append(f"`{permission.name}` - {permission.description}")

    embed = Embed(title=title, colour=0xCF0606)
    if not out:
        embed.description = translations.no_permissions
        await ctx.send(embed=embed)
        return

    embed.colour = 0x256BE6
    for level, lines in sorted(out.items(), reverse=True):
        embed.add_field(name=translations.permission_levels[level], value="\n".join(sorted(lines)), inline=False)

    await send_long_embed(ctx, embed)


class PermissionsCog(Cog, name="Permissions"):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.group(aliases=["perm", "p"])
    @guild_only()
    async def permissions(self, ctx: Context):
        """
        manage bot permissions
        """

        if ctx.invoked_subcommand is None:
            raise UserInputError

    @permissions.command(name="list", aliases=["show", "l", "?"])
    @Permission.view_all_permissions.check
    async def permissions_list(self, ctx: Context, min_level: Optional[PermissionLevelConverter]):
        """
        list all permissions
        """

        if min_level is None:
            min_level = PermissionLevel.ADMINISTRATOR

        await list_permissions(ctx, translations.permissions_title, min_level)

    @permissions.command(name="my", aliases=["m", "own", "o"])
    @Permission.view_own_permissions.check
    async def permissions_my(self, ctx: Context):
        """
        list all permissions granted to the user
        """

        min_level: PermissionLevel = await PermissionLevel.get_permission_level(ctx.author)
        await list_permissions(ctx, translations.my_permissions_title, min_level)

    @permissions.command(name="set", aliases=["s", "="])
    @PermissionLevel.ADMINISTRATOR.check
    async def permissions_set(self, ctx: Context, permission: str, level: PermissionLevelConverter):
        """
        configure bot permissions
        """

        level: PermissionLevel
        try:
            permission: Permission = Permission[permission.lower()]
        except KeyError:
            raise CommandError(translations.invalid_permission)

        await permission.set(level)
        await ctx.send(translations.f_permission_set(permission.name, translations.permission_levels[level.value]))
