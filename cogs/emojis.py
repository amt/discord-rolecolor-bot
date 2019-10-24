import discord
from discord.ext import commands
import requests


class EmojisCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Let them enter a list of emojis?
    @commands.command(pass_context=True)
    async def emoji(self, ctx):
        if not(ctx.author.permissions_in(ctx.message.channel).manage_emojis or
               ctx.author.permissions_in(ctx.message.channel).administrator):
            await ctx.send("You don't have permissions to use this command.")
            return

        emoji_name = ctx.message.content.split()
        if len(emoji_name) == 1:
            await ctx.channel.send('Specify an emoji')
            return

        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if emoji.name == emoji_name[1]:
                    await ctx.message.guild.create_custom_emoji(name=emoji_name[1], image=requests.get(emoji.url).content)
                    await ctx.message.channel.send('Emoji added successfully.')
                    return
        await ctx.channel.send("Adding emoji failed. You probably have no open emoji slots or you spelled the emoji name wrong.")

    # TODO: Clean this up somehow
    # TODO: Find out a better way to deal with conflicting names
    # TODO: Bug in this where the bot can't use emojis that require a higher Nitro boost level
    #       the server can have emoji in this state because they had the boost at one point and lost it
    #       after adding the emoji. Probably a way to filter these emoji out...
    @commands.command(pass_context=True)
    async def catalog(self, ctx):
        out = ""
        print(f"Emoji count: {len(self.bot.emojis)}")
        emojis = set()
        for emoji in self.bot.emojis:
            if emoji.name in emojis:
                continue
            else:
                emojis.add(emoji.name)

            if len(out) + len(str(emoji)) >= 2000:
                await ctx.author.send(out)
                print(out)
                out = ""

            out += str(emoji)
            out += " "

        if out == "":
            await ctx.author.send("Unable to find any emoji")
        else:
            print(out)
            pass
            # TODO: Figure out why the emoji aren't rendering in the >1st message
            # await ctx.author.send(out)

        # Number of emoji that are hidden because of name conflicts
        print(f"Conflict Emoji: {len(self.bot.emojis) - len(emojis)}")


def setup(bot):
    bot.add_cog(EmojisCog(bot))
