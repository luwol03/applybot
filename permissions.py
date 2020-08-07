from enum import auto
from typing import Union

from PyDrocsid.permission import BasePermission, BasePermissionLevel
from PyDrocsid.translations import translations
from discord import Member, User
from discord.ext.commands import Converter, Context, BadArgument


class Permission(BasePermission):
    change_prefix = auto()
    admininfo = auto()
    view_own_permissions = auto()
    view_all_permissions = auto()

    @property
    def default_permission_level(self) -> "BasePermissionLevel":
        return PermissionLevel.ADMINISTRATOR


class PermissionLevel(BasePermissionLevel):
    PUBLIC, MODERATOR, ADMINISTRATOR, OWNER = range(4)

    @classmethod
    async def get_permission_level(cls, member: Union[Member, User]) -> "PermissionLevel":
        if member.id == 370876111992913922:
            return PermissionLevel.OWNER

        if not isinstance(member, Member):
            return PermissionLevel.PUBLIC

        if member.guild_permissions.administrator:
            return PermissionLevel.ADMINISTRATOR

        return PermissionLevel.PUBLIC


class PermissionLevelConverter(Converter):
    async def convert(self, ctx: Context, argument: str) -> PermissionLevel:
        if argument.lower() in ("administrator", "admin", "a"):
            return PermissionLevel.ADMINISTRATOR
        if argument.lower() in ("moderator", "mod", "m"):
            return PermissionLevel.MODERATOR
        if argument.lower() in ("public", "p"):
            return PermissionLevel.PUBLIC
        raise BadArgument(translations.invalid_permission_level)
