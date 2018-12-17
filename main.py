import discord
import logging
import re
import colormath
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# TODO: Config file or environment variables for token
TOKEN = ''
DISCORD_DARK_COLOR = convert_color(sRGBColor.new_from_rgb_hex('2C2F33'), LabColor)
DISCORD_LIGHT_COLOR = convert_color(sRGBColor.new_from_rgb_hex('FFFFFF'), LabColor)

# TODO: Max number of colors allowed -> print a list of current colors the user can pick from
# TODO: Clean up after bot/user messages

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord-color-bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Instantiate bot client
client = discord.Client(activity=discord.Game(name='&help'))


@client.event
async def cleanup_roles(guild):
    for role in guild.roles:
        if re.search(r'^(?:[0-9a-fA-F]){6}$', role.name) and len(role.members) == 0:
            await role.delete(reason="Cleaning up unused roles")
    return


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print('Cleaning up unused roles...')
    for guild in client.guilds:
        await cleanup_roles(guild)
    print('Done cleaning up unused roles')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Check for &hexcode
    if not message.content.startswith('&'):
        return

    if message.content == '&help':
        await message.channel.send('Example: &FFFAAA')
        return

    # Important so that we aren't duplicating upper/lowercase versions of the role
    message.content = message.content.upper()

    # Check validness of color code
    # TODO: Maybe add support for 3 long hexcodes that would just be expanded
    if not re.search(r'^(?:[0-9a-fA-F]){6}$', message.content[1:]):
        await message.channel.send('Invalid color\nExample: &FFFAAA')
        return

    # Check for similarity to background colors so names are visible still
    test_color = convert_color(
        sRGBColor.new_from_rgb_hex(message.content[1:]), LabColor)

    dark_delta_e = delta_e_cie2000(test_color, DISCORD_DARK_COLOR)
    logger.debug("Dark DeltaE Test (dark_delta_e, test_color_hex): {} {}".format(str(dark_delta_e), message.content[1:]))

    light_delta_e = delta_e_cie2000(test_color, DISCORD_LIGHT_COLOR)
    logger.debug("Light DeltaE Test (light_delta_e, test_color_hex): {} {}".format(str(light_delta_e), message.content[1:]))

    if dark_delta_e <= 13.0:
        await message.channel.send('That is too similar to Discord\'s dark background.\nTry another color.')
        return

    if light_delta_e <= 13.0:
        await message.channel.send('That is too similar to Discord\'s light background.\nTry another color.')
        return

    # Remove old color roles
    for role in message.author.roles:
        if re.search(r'^(?:[0-9a-fA-F]){6}$', role.name):
            await message.author.remove_roles(role, reason="Removing old color")
            if len(role.members) == 1:
                await role.delete(reason="Removing unused color")

    role = discord.utils.get(message.guild.roles, name=message.content[1:])
    # If color exists just assign it to the user
    if role:
        await message.author.add_roles(role, reason="Adding user's role")
        await message.channel.send('Added new role')
    else:
        new_role = await message.guild.create_role(name=message.content[1:], color=discord.Colour(int(message.content[1:], 16)))
        await message.author.add_roles(new_role, reason="Adding user's role")
        await message.channel.send('Added new role')

    await cleanup_roles(message.guild)


# Run the bot
client.run(TOKEN)
