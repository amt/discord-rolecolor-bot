import os
import sys
import traceback

import discord
from discord.ext import commands


def get_prefix(bot, message):
    prefixes = ['&']
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_extensions = [
    'cogs.colors',
]

embed = discord.Embed(title="Commands:", description="", color=0xFF1515)

# Create instance of bot and remove ugly default help command
bot = commands.Bot(command_prefix=get_prefix,
                   description='Discord ColorBot', help_command=None)


def main():

    # TODO: Move these to the color cog and build the embed as cogs are loaded
    embed.add_field(name="&help", value="Prints this message", inline=False)
    embed.add_field(name="&color <color>",
                    value="Assign colors using 6 digit hex codes\nExample Usage: &color FABCDE\nSee: https://www.google.com/search?q=color+picker", inline=False)
    embed.add_field(name="&clear", value="Remove color", inline=False)

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)

        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

    bot.run(os.environ.get('DISCORD_COLOR_BOT_TOKEN'), bot=True, reconnect=True)


@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\n')
    print(f'Version: {discord.__version__}')

    await bot.change_presence(activity=discord.Game(name='&help | now on heroku!'))
    print(f'Successfully logged in and booted...!')

if __name__ == '__main__':
    main()
