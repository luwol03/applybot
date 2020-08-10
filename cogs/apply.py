from PyDrocsid.database import db_thread, db
from PyDrocsid.help import send_help
from PyDrocsid.translations import translations
from PyDrocsid.util import read_normal_message, send_long_embed
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, Bot, guild_only, Context

from models.apply import Jobs, Questions
from permissions import Permission


class ApplyCog(Cog, name="apply"):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_ready(self):
        pass

    @commands.group(name="jobs", aliases=["j"])
    @guild_only()
    async def jobs(self, ctx: Context):
        """
        create and apply for jobs
        """

        if ctx.invoked_subcommand is None:
            await send_help(ctx, self.jobs)

    @jobs.command(name="list", aliases=["l"])
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

    @jobs.command(name="create", aliases=["add", "a", "c", "+"])
    @Permission.manage_jobs.check
    @guild_only()
    async def create_jobs(self, ctx: Context):
        """
        create an job to apply
        """

        await ctx.send(translations.ask_job_name)
        job_name, _ = await read_normal_message(self.bot, ctx.channel, ctx.author)
        await ctx.send(translations.ask_job_description)
        job_description, _ = await read_normal_message(self.bot, ctx.channel, ctx.author)
        questions = []

        while True:
            await ctx.send(translations.ask_question)
            q, _ = await read_normal_message(self.bot, ctx.channel, ctx.author)
            if q == ".exit":
                questions = []
                break
            elif q == ".save":
                break
            questions.append(q)

        if len(questions) == 0:
            await ctx.send(translations.no_questions_defined)
            return

        if await db_thread(db.first, Jobs, name=job_name) is not None:
            await ctx.send(translations.job_exist)
            return

        await db_thread(Jobs.create, job_name, job_description)

        for i, q in enumerate(questions):
            await db_thread(Questions.create, job_name, q, i)

        await ctx.send(translations.job_saved)
