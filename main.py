import os
import discord

from discord.ext import commands
from discord import app_commands

intents = discord.Intents.all() # Make sure you've enabled your Intents from the discord developer portal
client = commands.Bot(command_prefix='>', intents=intents) # Command prefix can be changed to whatever u want, example "?" "." "<" and more

@client.event
async def on_ready(): # Change discord bot status when it's online
    activity = discord.Game(name="Activity Name | /help", type=3) # discord.Game = Playing status, you can change it to Streaming or Listening, for more info read Discord API Docs 
    await client.change_presence(status=discord.Status.online, activity=activity)
    print("discord bot is running!")
    try:
        for filename in os.listdir('./cogs'): # hook any cogs file in 'cogs' folder
            if filename.endswith('.py'):
                await client.load_extension(f'cogs.{filename[:-3]}')
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@client.event
async def on_message(message): # Create message listener
    if message.author.id == 1234567890: # if you send the message, then the bot will ignore you
        return
    
    # Example code
    if "discord.gg/invite" in message.content: # If someone send invite link
        message.channel.purge(limit=1) # then remove the message, "limit=1" means remove 1 message
        message.author.ban() # if you want to ban him, or u can change it with whatever u want
        message.channel.send(f"{message.author.mention} has been banned, sending invite link with no permission") # you can change this banned/warning message

    await client.process_commands(message) # avoid clashes between prefix command and on_message

    # Write your another logic code here

@client.event
async def on_command_error(ctx, error): # When the user write a wrong command / argument, or doesn't have the permission to use the command
    if isinstance(error, commands.MissingPermissions): # No permission
        mbed = discord.Embed(title="", description=f"You don't have permission to use this command",color=discord.Color.from_rgb(235, 204, 52))
        await ctx.reply(embed=mbed)
    elif isinstance(error, commands.MissingRequiredArgument): # Invalid argument or command usage
        mbed = discord.Embed(title="", description=f"Invalid argument, type /help to see commands list",color=discord.Color.from_rgb(235, 204, 52))
        await ctx.reply(embed=mbed)

    # Write your another error handler, for more info read Discord API Docs

"""Make common commands with a slash "/" command"""
# ban command
@client.tree.command(name="ban", description="Ban a user from the server")
@commands.has_permissions(ban_members=True, kick_members=True) # permission selector
@commands.guild_only() # this command can be used only in discord server, not in dm
@app_commands.describe(user="Mention the user", reason="Ban reason") # when the user type "/" command, they can see the description of the command value
async def ban(ctx: discord.Interaction, user: discord.Member, *, reason: str): # discord.Interaction for slash command, discord.Member for mention the user
    await user.ban(reason=reason)
    mbed = discord.Embed(title="", description=f"{user} has been banned from the server!, {reason}",color=discord.Color.from_rgb(235, 204, 52))
    await ctx.response.defer(ephemeral=False) # if the "ephmeral=True" then only you can see the bot's response, if False, all members can see the response
    await ctx.followup.send(embed=mbed) # Send the message/response

@client.tree.command(name="kick", description="Kick a user from the server")
@commands.has_permissions(kick_members=True)
@commands.guild_only()
@app_commands.describe(user="Mention the user", reason="Kick reason")
async def kick(ctx: discord.Interaction, user: discord.Member, *, reason: str):
    await user.kick(reason=reason)
    mbed = discord.Embed(title="", description=f"{user} has been kicked from the server!, {reason}",color=discord.Color.from_rgb(235, 204, 52))
    await ctx.response.defer(ephemeral=False)
    await ctx.followup.send(embed=mbed)

@client.tree.command(name="unban", description="Unban a user from the server")
@commands.has_permissions(ban_members=True)
@commands.guild_only()
@app_commands.describe(user="Mention the user/input user's id")
async def unban(ctx: discord.Interaction, user: discord.User):
    await ctx.guild.unban(user)
    mbed = discord.Embed(title="", description=f"{user} has been unbanned from the server!",color=discord.Color.from_rgb(235, 204, 52))
    await ctx.response.defer(ephemeral=False)
    await ctx.followup.send(embed=mbed)

@client.tree.command(name="clear", description="Clear a message")
@commands.has_permissions(manage_messages=True)
@commands.guild_only()
@app_commands.describe(total="how many chat you want to clear?")
async def clear(ctx: discord.Interaction, total: int):
    await ctx.channel.purge(limit=1)
    mbed = discord.Embed(title="", description=f"{total} message(s) has been removed",color=discord.Color.from_rgb(235, 204, 52))
    await ctx.response.defer(ephemeral=False)
    await ctx.followup.send(embed=mbed)

@client.tree.command(name="avatar", description="Generate user's avatar")
@commands.guild_only()
@app_commands.describe(user="Mention the user to generate their avatar")
async def avatar(ctx: discord.Interaction, user: discord.Member):
    mbed = discord.Embed(title="Avatar", color=discord.Color.from_rgb(235, 204, 52))
    mbed.add_field(name="i want to stalky stalky", value=f"{user.mention}'s Avatar")
    mbed.set_image(url=user.avatar)
    await ctx.response.defer(ephemeral=False)
    await ctx.followup.send(embed=mbed)

"""Make common commands with a > prefix command"""
# Ban command with prefix
@client.command(name="ban")
@commands.has_permissions(ban_members=True, kick_members=True) # permission selector
@commands.guild_only() # this command can be used only in discord server, not in dm
async def ban(ctx: commands.Context, user: discord.Member, *, reason: str): # commands.Context for prefix command, discord.Member for mention the user
    await user.ban(reason=reason)
    mbed = discord.Embed(title="", description=f"{user} has been banned from the server!, {reason}",color=discord.Color.from_rgb(235, 204, 52))
    await ctx.send(embed=mbed)

@client.command(name="kick")
@commands.has_permissions(kick_members=True)
@commands.guild_only()
async def kick(ctx: commands.Context, user: discord.Member, *, reason: str):
    await user.kick(reason=reason)
    mbed = discord.Embed(title="", description=f"{user} has been kicked from the server!, {reason}",color=discord.Color.from_rgb(235, 204, 52))
    await ctx.send(embed=mbed)

@client.command(name="unban")
@commands.has_permissions(ban_members=True)
@commands.guild_only()
async def unban(ctx: commands.Context, user: discord.User):
    await ctx.guild.unban(user)
    mbed = discord.Embed(title="", description=f"{user} has been unbanned from the server!",color=discord.Color.from_rgb(235, 204, 52))
    await ctx.send(embed=mbed)

@client.command(name="clear")
@commands.has_permissions(manage_messages=True)
@commands.guild_only()
async def clear(ctx: commands.Context, total: int):
    await ctx.channel.purge(limit=1)
    mbed = discord.Embed(title="", description=f"{total} message(s) has been removed",color=discord.Color.from_rgb(235, 204, 52))
    await ctx.send(embed=mbed)

@client.command(name="avatar")
@commands.guild_only()
async def avatar(ctx: commands.Context, user: discord.Member):
    mbed = discord.Embed(title="Avatar", color=discord.Color.from_rgb(235, 204, 52))
    mbed.add_field(name="i want to stalky stalky", value=f"{user.mention}'s Avatar")
    mbed.set_image(url=user.avatar)
    await ctx.send(embed=mbed)

client.run("YOUR TOKEN") # replace it with your bot token
