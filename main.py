import discord
import logging
import re

TOKEN = ''

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord-color-bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Instantiate & Run
client = discord.Client()

@client.event
async def cleanup_roles():
    for guild in client.guilds:
        for role in guild.roles:
            if re.search(r'^(?:[0-9a-fA-F]){6}$', role.name) and len(role.members) == 0:
                await role.delete(reason="Cleaning up unused roles")
    return

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print('Cleaning up unused roles...')
    await cleanup_roles()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Check for &hexcode
    if message.content.startswith('&'):
        # check validness of color code
        if not re.search(r'^(?:[0-9a-fA-F]){6}$', message.content[1:]):
            await message.channel.send('Invalid hex color code. Example: &fffaaa')
            return

        role = discord.utils.get(message.guild.roles, name=message.content[1:])
        # If color exists just assign it to the user
        if role:
            await message.author.add_roles(role, reason="Adding user's role")
            await message.channel.send('Added new role')

        else:
            # Remove old color roles
            for role in message.author.roles:
                if re.search(r'^(?:[0-9a-fA-F]){6}$', role.name):
                    await message.author.remove_roles(role, reason="Removing old color")
                    if len(role.members) == 1:
                        await role.delete(reason="Removing unused color")

            new_role = await message.guild.create_role(name=message.content[1:], color=discord.Colour(int(message.content[1:], 16)))
            await message.author.add_roles(new_role, reason="Adding user's role")
            await message.channel.send('Added new role')


client.run(TOKEN)
