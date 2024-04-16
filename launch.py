import discord
import asyncio 
from discord.ext import commands
from randoms import Randoms
from weather import Weather

description = """KoalaBot!"""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# The command prefix
bot = commands.Bot(command_prefix='$', description=description, intents=intents)

# on startup simply say that it's started up
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.add_cog(Randoms(bot))
    await bot.add_cog(Weather(bot))


# tells the time/date a user joined
@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'{member.name} joined in {member.joined_at}')

@bot.command(pass_context=True)
async def poll(ctx, question, *options: str):
    author = ctx.message.author
    guild = ctx.message.guild

    if not author.guild_permissions.manage_messages:
        return await ctx.send("You don't have the required permissions to use this command.")

    if len(options) < 2:
        return await ctx.send("Error! A poll must have at least two options.")

    if len(options) > 9:
        return await ctx.send("Error! Poll can have no more than nine options.")

    description = ""

    emoji_list = []
    for x, option in enumerate(options):
        if x >= 9:
            break
        desc, emoji = option.split(',', 1)
        description += f'\n {emoji.strip()}: {desc.strip()}'
        emoji_list.append(emoji.strip())

    embed = discord.Embed(title=question, color=discord.Color.blue(), description=description)

    react_message = await ctx.send(embed=embed)

    for emoji in emoji_list:
        await react_message.add_reaction(emoji)

        embed.set_footer(text='Poll ID: {}'.format(react_message.id))

        await react_message.edit(embed=embed)


@bot.command(pass_context=True)
async def pollwinner(ctx, poll_str):
    poll_id = int(poll_str)

    author = ctx.message.author

    if not author.guild_permissions.manage_messages:
        return await ctx.send("You don't have the required permissions to use this command.")

    try:
        poll_message = await ctx.fetch_message(poll_id)
    except:
        return await ctx.send("Error! Invalid poll ID.")

    poll_reactions = poll_message.reactions
    emoji_dict = {}
    for reaction in poll_reactions:
        emoji_dict[str(reaction.emoji)] = reaction.count

    max_votes = 0
    winner_emoji = None

    for emoji, votes in emoji_dict.items():
        num_votes = votes - 1  # Subtract 1 to exclude the bot's own reaction
        if num_votes > max_votes:
            max_votes = num_votes
            winner_emoji = emoji

    if winner_emoji:
        await ctx.send(f'The winner of the poll is: {winner_emoji}')
    else:
        await ctx.send('No votes were cast in this poll.')

bot.run('DISCORD_API_KEY')