# Discord RoleColor Bot

## Installation

Uses Python 3.5.2+

Optional:

* ```python3 -m venv env```
* ```source env/bin/activate```

Required:

1. ```pip install -r requirements.txt```

2. Create a discord account for your bot:

    * Follow the steps [here](https://discordpy.readthedocs.io/en/rewrite/discord.html#discord-intro)

## Usage

```sh
python3 main.py
```

## Notes

Discord uses the color of the user's highest role, any role higher than the role assigned by the bot will be the color.

The easiest way to avoid any problems with this is to have no colors for any roles except for the ones that will be made by the bot.

You can check this by making sure all non-bot roles are set to the default:
![alt-text](https://i.imgur.com/oFAyCNv.png)

The bot will delete any unused roles that are valid hex color codes if those are being used as role names.
