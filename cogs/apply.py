from typing import Dict

from PyDrocsid.database import db_thread, db
from PyDrocsid.translations import translations
from PyDrocsid.util import read_normal_message, send_long_embed
from discord import Embed, Forbidden, HTTPException, Member, TextChannel
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

    @job.command(name="apply", aliases=["a"])
    @Permission.apply_jobs.check
    @guild_only()
    async def apply_job(self, ctx: Context, job_name: str):
        """
        apply for a job
        """
        embed = Embed(title=translations.apply, colour=0xCF0606)
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
                if r == ".exit":
                    embed = Embed(title=translations.apply, description=translations.apply_canceld, colour=0xCF0606)
                    await ctx.author.send(embed=embed)
                    return
                reply.append({q: str(q.question), r: r})
        except (Forbidden, HTTPException):
            await ctx.send(translations.no_dm)
            return

        print(reply)

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
            if q == ".exit":
                questions = []
                break
            elif q == ".save":
                break
            questions.append(q)

        if len(questions) == 0:
            await ctx.send(translations.no_questions_defined)
            return

        await db_thread(Jobs.create, job_name, job_description)

        for i, q in enumerate(questions):
            await db_thread(Questions.create, job_name, q, i)

        await ctx.send(translations.job_saved)
