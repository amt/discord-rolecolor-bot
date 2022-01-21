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
    'cogs.emojis',
]


# Create instance of bot and remove ugly default help command
bot = commands.Bot(command_prefix=get_prefix,
                   description='Discord ColorBot', help_command=None)


@commands.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title="Commands:", description="", color=0xFF1515)
    # TODO: Move these to the correct cogs and build the embed as cogs are loaded
    embed.add_field(name="&help", value="Prints this message", inline=False)
    # Colors
    embed.add_field(name="&color <color>",
                    value="Assign colors using 6 digit hex codes\nExample Usage: &color FABCDE\nSee: https://www.google.com/search?q=color+picker", inline=False)
    embed.add_field(name="&clear", value="Remove color", inline=False)
    # Emoji
    embed.add_field(name="&catalog",
                    value="List available emojis", inline=False)
    embed.add_field(name="&emoji <emojiName>",
                    value="Tale the specified emoji and add it to this server", inline=False)
    await ctx.message.channel.send(content="", embed=embed)


def main():
    bot.add_command(help)
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

    await bot.change_presence(activity=discord.Game(name='&help'))
    print(f'Successfully logged in and booted...!')

if __name__ == '__main__':
    main()
