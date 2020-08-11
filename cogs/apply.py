from PyDrocsid.database import db_thread, db
from PyDrocsid.settings import Settings
from PyDrocsid.translations import translations
from PyDrocsid.util import read_normal_message, send_long_embed
from discord import Embed, Forbidden, HTTPException, TextChannel
from discord.ext import commands
from discord.ext.commands import Cog, Bot, guild_only, Context, UserInputError

from models.apply import Jobs, Questions
from permissions import Permission


class ApplyCog(Cog, name="apply"):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.group(aliases=["j"])
    @guild_only()
    async def job(self, ctx: Context):
        """
        create and apply for jobs
        """

        if ctx.invoked_subcommand is None:
            raise UserInputError

    @commands.command(name="apply", aliases=["a"])
    @Permission.apply_jobs.check
    @guild_only()
    async def apply_job(self, ctx: Context, job_name: str):
        """
        apply for a job
        """
        embed = Embed(title=translations.apply, colour=0xCF0606)
        if await Settings.get(str, "apply_channel") is None:
            embed.description = translations.no_apply_chanel_defined + " " + translations.apply_canceld
            await ctx.send(embed=embed)
            return
        if await db_thread(db.first, Jobs, name=job_name) is None:
            embed.description = translations.f_job_not_found(job_name)
            await ctx.send(embed=embed)
            return
        embed.colour = 0x256BE6
        embed.add_field(name=translations.apply_title, value=translations.f_apply_congratulations(job_name),
                        inline=False)
        await send_long_embed(ctx, embed)
        pv_embed = Embed(title=translations.apply, colour=0x256BE6)
        pv_embed.add_field(name=translations.apply_title, value=translations.f_reply_to_questions(job_name),
                           inline=False)
        reply = []

        try:
            await send_long_embed(ctx.author, pv_embed)
            for q in sorted(await db_thread(db.query, Questions, job_name=job_name), key=lambda x: x.order):
                embed = Embed(title=translations.apply, description=q.question, colour=0x256BE6)
                await send_long_embed(ctx.author, embed)
                r, _ = await read_normal_message(self.bot, ctx.author.dm_channel, ctx.author)
                if r == "exit":
                    embed = Embed(title=translations.apply, description=translations.apply_canceld, colour=0xCF0606)
                    await ctx.author.send(embed=embed)
                    return
                reply.append((str(q.question), r))
        except (Forbidden, HTTPException):
            await ctx.send(translations.no_dm)
            return

        embed = Embed(title=translations.apply, colour=0xCF0606)
        channel = self.bot.get_channel(int(await Settings.get(str, "apply_channel")))

        if channel is None:
            embed.description = translations.no_apply_chanel_defined + " " + translations.apply_canceld
            await ctx.author.send(embed=embed)
            return

        try:
            apply_embed = Embed(title=translations.apply,
                                description=translations.f_apply_embed_des(ctx.author.mention),
                                colour=0x256BE6)
            apply_embed.set_footer(text=translations.f_requested_by(ctx.author, ctx.author.id),
                                   icon_url=ctx.author.avatar_url)
            for q, r in reply:
                apply_embed.add_field(name=q, value=r, inline=False)
            await send_long_embed(channel, apply_embed)
            embed.description = translations.successfully_send
            embed.colour = 0x256BE6
            await ctx.author.send(embed=embed)
        except (HTTPException, Forbidden):
            embed.description = translations.no_apply_chanel_defined + " " + translations.apply_canceld
            embed.colour = 0xCF0606
            await ctx.author.send(embed=embed)
            return

    @job.command(name="list", aliases=["l"])
    @Permission.list_jobs.check
    @guild_only()
    async def list_jobs(self, ctx: Context):
        """
        list all jobs to apply
        """

        out = []
        for job in await db_thread(db.query, Jobs):
            out.append(f"`{job.name}` - {job.description}")

        embed = Embed(title=translations.job_list_title, colour=0xCF0606)
        if not out:
            embed.description = translations.no_jobs
            await ctx.send(embed=embed)
            return

        embed.colour = 0x256BE6
        embed.add_field(name=translations.job_list_description, value="\n".join(sorted(out)), inline=False)

        await send_long_embed(ctx, embed)

    @job.command(name="create", aliases=["add", "c", "+"])
    @Permission.manage_jobs.check
    @guild_only()
    async def create_jobs(self, ctx: Context):
        """
        create an job to apply
        """

        await ctx.send(translations.ask_job_name)
        job_name, _ = await read_normal_message(self.bot, ctx.channel, ctx.author)

        if await db_thread(db.first, Jobs, name=job_name) is not None:
            await ctx.send(translations.job_exist)
            return

        await ctx.send(translations.ask_job_description)
        job_description, _ = await read_normal_message(self.bot, ctx.channel, ctx.author)
        questions = []

        while True:
            await ctx.send(translations.ask_question)
            q, _ = await read_normal_message(self.bot, ctx.channel, ctx.author)
            if q == "exit":
                questions = []
                break
            elif q == "save":
                break
            questions.append(q)

        if len(questions) == 0:
            await ctx.send(translations.no_questions_defined)
            return

        await db_thread(Jobs.create, job_name, job_description)

        for i, q in enumerate(questions):
            await db_thread(Questions.create, job_name, q, i)

        await ctx.send(translations.job_saved)

    @job.command(name="delete", aliases=["d", "-"])
    @Permission.manage_jobs.check
    @guild_only()
    async def delete_jobs(self, ctx: Context, job_name: str):
        """
        delete an job to apply
        """
        embed = Embed(title=translations.delete_title, colour=0xCF0606)
        job = await db_thread(db.first, Jobs, name=job_name)
        qus = await db_thread(db.all, Questions, job_name=job_name)
        if job is None or qus is None:
            embed.description = translations.f_job_not_exists(job_name)
            await ctx.send(embed=embed)
            return
        await db_thread(db.delete, job)
        for q in qus:
            await db_thread(db.delete, q)
        embed.colour = 0x256BE6
        embed.description = translations.f_deleted_successfully(job_name)
        await ctx.send(embed=embed)

    @job.command()
    @Permission.manage_jobs.check
    @guild_only()
    async def set_apply_channel(self, ctx: Context, channel: TextChannel):
        """
        set apply text channel
        """
        await Settings.set(str, "apply_channel", str(channel.id))
        embed = Embed(title=translations.apply_channel,
                      description=translations.f_successfully_set_apply_channel(channel.mention), colour=0x256BE6)
        await ctx.send(embed=embed)

    @job.command()
    @Permission.manage_jobs.check
    @guild_only()
    async def get_apply_channel(self, ctx: Context):
        """
        get apply text channel
        """
        embed = Embed(title=translations.apply_channel, colour=0x256BE6)
        channel = await Settings.get(str, "apply_channel")
        if channel is not None:
            embed.description = translations.f_apply_channel_list(channel)
        else:
            embed.description = translations.no_apply_chanel_defined
            embed.colour = 0xCF0606
        await ctx.send(embed=embed)
