import re
import discord
from discord.ext import commands

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

DISCORD_DARK_COLOR = convert_color(sRGBColor.new_from_rgb_hex('2C2F33'), LabColor)
DISCORD_LIGHT_COLOR = convert_color(sRGBColor.new_from_rgb_hex('FFFFFF'), LabColor)

class RoleColorsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        # Run global cleanup once on startup if role color cog is loaded
        for guild in self.bot.guilds:
            await self.cleanup_roles(guild)


    @commands.command(pass_context=True)
    async def color(self, ctx):
        # Important so that we aren't duplicating upper/lowercase versions of the role
        ctx.message.content = ctx.message.content.upper().split()[1]

        # Check validness of color code
        # TODO: Maybe add support for 3 long hexcodes that would just be expanded
        if not re.search(r'^(?:[0-9a-fA-F]){6}$', ctx.message.content):
            await ctx.channel.send('Invalid color\nExample Usage: &color FABCDE')
            return
        
        # Check for similarity to background colors so names are visible still
        test_color = convert_color(
            sRGBColor.new_from_rgb_hex(ctx.message.content), LabColor)

        dark_delta_e = delta_e_cie2000(test_color, DISCORD_DARK_COLOR)

        light_delta_e = delta_e_cie2000(test_color, DISCORD_LIGHT_COLOR)

        if dark_delta_e <= 13.0:
            await ctx.channel.send('Try another color.\nToo similar to Discord\'s dark background.')
            return

        if light_delta_e <= 13.0:
            await ctx.channel.send('Try another color.\n Too similar to Discord\'s light background.')
            return

        # Remove old color roles
        for role in ctx.author.roles:
            if re.search(r'^(?:[0-9a-fA-F]){6}$', role.name):
                await ctx.author.remove_roles(role, reason="Removing old color")
                if len(role.members) == 1:
                    await role.delete(reason="Removing unused color")

        role = discord.utils.get(ctx.guild.roles, name=ctx.message.content)
        # If color exists just assign it to the user
        if role:
            await ctx.author.add_roles(role, reason="Adding existing role to user")
        else:
            new_role = await ctx.guild.create_role(name=ctx.message.content, color=discord.Colour(int(ctx.message.content, 16)))
            await ctx.author.add_roles(new_role, reason="Created new role for user")

        await ctx.channel.send('Added role')
        await self.cleanup_roles(ctx.guild)


    @commands.command(pass_context=True)
    async def clear(self, ctx):
        if ctx.message.content == '&clear':
            for role in ctx.author.roles:
                if re.search(r'^(?:[0-9a-fA-F]){6}$', role.name):
                    await ctx.author.remove_roles(role, reason="Removing user color by request")
                    if len(role.members) == 1:
                        await role.delete(reason="Removing unused color")
            await ctx.message.channel.send('User color managed by bot cleared!')


    async def cleanup_roles(self, guild):
        print(f"\tCleaning up -- {guild}")
        for role in guild.roles:
            if re.search(r'^(?:[0-9a-fA-F]){6}$', role.name) and len(role.members) == 0:
                try:
                    await role.delete(reason="Cleaning up unused roles")
                except:
                    print(f"\t\tFailed to clean up -- {guild}")
                    return

def setup(bot):
    bot.add_cog(RoleColorsCog(bot))