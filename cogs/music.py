import asyncio
import wavelink
import discord

from discord import app_commands
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue = []
        self.position = 0
        self.repeat = False
        self.repeatMode = "NONE"
        self.playingTextChannel = None
        bot.loop.create_task(self.create_nodes())

    async def create_nodes(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host="IP", port="2333", password="youshallnotpass") # Connect to your lavalink server, replace it with your address

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music is ready!")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node <{node.identifier}> is now Ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        try:
            self.queue.pop(0)
        except:
            pass

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        if str(reason) == "FINISHED":
            if not len(self.queue) == 0:
                next_track: wavelink.Track = self.queue[0]
                channel = self.bot.get_channel(self.playingTextChannel)
                try:
                    await player.play(next_track)
                    mbed = discord.Embed(title="Now Playing",color=discord.Color.from_rgb(235, 204, 52))
                    mbed.add_field(name="Song", value=f"{next_track}", inline=False)
                    await channel.send(embed=mbed)
                except:
                    mbed = discord.Embed(title="", description=f"Something went wrong while playing **{next_track.title}**",color=discord.Color.from_rgb(235, 204, 52))
                    return await channel.send(embed=mbed)
            else:
                pass
        else:
            print(reason)

    @app_commands.command(name="join", description="Join the bot to a voice channel")
    @commands.guild_only()
    @app_commands.describe(channel="Select voice channel")
    async def join(self, ctx: discord.Interaction, *,channel: discord.VoiceChannel):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)
        self.channel = channel

        if player is not None:
            if player.is_connected():
                mbed = discord.Embed(title="", description=f"Bot already connected in a voice channel",color=discord.Color.from_rgb(235, 204, 52))
                return await ctx.response.send_message(embed=mbed)
        
        await channel.connect(cls=wavelink.Player)
        await channel.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
        await ctx.response.defer(ephemeral=False)
        mbed = discord.Embed(title="", description=f"Connected to a voice channel!",color=discord.Color.from_rgb(235, 204, 52))
        await ctx.followup.send(embed=mbed)

    @app_commands.command(name="leave", description="Disconnect the bot")
    @commands.guild_only()
    async def leave(self, ctx: discord.Interaction):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            mbed = discord.Embed(title="", description=f"Bot is not connected to any voice channel",color=discord.Color.from_rgb(235, 204, 52))
            await ctx.response.defer(ephemeral=False)
            return await ctx.followup.send(embed=mbed)
        
        await player.disconnect()
        mbed = discord.Embed(title="", description=f"Disconnected",color=discord.Color.from_rgb(235, 204, 52))
        await ctx.response.defer(ephemeral=False)
        await ctx.followup.send(embed=mbed)

    @app_commands.command(name="play", description="Play any song")
    @commands.guild_only()
    @app_commands.describe(song="Enter song title")
    async def play(self, ctx: discord.Interaction, *, song: str):
        self.playingTextChannel = ctx.channel.id
        try:
            song = await wavelink.YouTubeTrack.search(query=song, return_first=True)
        except Exception as err:
            print(err)
            mbed = discord.Embed(title="", description=f"Something went wrong while searching for this track",color=discord.Color.from_rgb(235, 204, 52))
            await ctx.response.send_message(embed=mbed)

        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if not ctx.user.guild.voice_client:
            vc: wavelink.Player = await ctx.user.voice.channel.connect(cls=wavelink.Player)
            await vc.guild.change_voice_state(channel=ctx.user.voice.channel, self_mute=False, self_deaf=True)
        else:
            vc: wavelink.Player = ctx.user.guild.voice_client
        
        if not vc.is_playing():
            try:
                await vc.play(song)
                mbed = discord.Embed(title="Now Playing",color=discord.Color.from_rgb(235, 204, 52))
                mbed.add_field(name="Song", value=f"{song.title}", inline=False)
                await ctx.response.send_message(embed=mbed)
            except:
                mbed = discord.Embed(title="", description=f"Something went wrong while playing for this track",color=discord.Color.from_rgb(235, 204, 52))
                await ctx.response.send_message(embed=mbed)
        else:
            self.queue.append(song)
            mbed = discord.Embed(title="", description=f"Added to queue " + "**"+song.title+"**",color=discord.Color.from_rgb(235, 204, 52))
            await ctx.response.send_message(embed=mbed)

    @app_commands.command(name="pause", description="Pause the music")
    @commands.guild_only()
    async def pause_command(self, ctx: discord.Interaction):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            mbed = discord.Embed(title="", description=f"Bot is not connected to any voice channel",color=discord.Color.from_rgb(235, 204, 52))
            return await ctx.response.send_message(embed=mbed)
        
        if not player.is_paused():
            if player.is_playing():
                await player.pause()
                mbed = discord.Embed(title="", description="Playback Paused",color=discord.Color.from_rgb(235, 204, 52))
                return await ctx.response.send_message(embed=mbed)
            else:
                mbed = discord.Embed(title="", description=f"Nothing is playing right now",color=discord.Color.from_rgb(235, 204, 52))
                return await ctx.response.send_message(embed=mbed)
        else:
            mbed = discord.Embed(title="", description=f"Playback is already paused",color=discord.Color.from_rgb(235, 204, 52))
            return await ctx.response.send_message(embed=mbed)
    
    @app_commands.command(name="resume", description="Resume the music")
    @commands.guild_only()
    async def resume_command(self, ctx: discord.Interaction):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            mbed = discord.Embed(title="", description=f"Bot is not connected to any voice channel",color=discord.Color.from_rgb(235, 204, 52))
            return await ctx.response.send_message(embed=mbed)
        
        if player.is_paused():
            await player.resume()
            mbed = discord.Embed(title="", description="Playback Resumed",color=discord.Color.from_rgb(235, 204, 52))
            return await ctx.response.send_message(embed=mbed)
        else:
            if not len(self.queue) == 0:
                track: wavelink.Track = self.queue[0]
                player.play(track)
                mbed = discord.Embed(title="Now Playing",color=discord.Color.from_rgb(235, 204, 52))
                mbed.add_field(name="Song", value=f"{track.title}", inline=False)
                return await ctx.response.send_message(embed=mbed)

            else:
                mbed = discord.Embed(title="", description=f"Playback is not paused",color=discord.Color.from_rgb(235, 204, 52))
                return await ctx.response.send_message(embed=mbed)

    @app_commands.command(name="playnow", description="Instantly play a song, and skip current playing song")
    @commands.guild_only()
    @app_commands.describe(song="Enter song title to play now")
    async def playnow(self, ctx: discord.Interaction, * , song: str):
        try:
            song = await wavelink.YouTubeTrack.search(query=song, return_first=True)
        except:
            return await ctx.response.send_message(embed=discord.Embed(title="Something went wrong while searching for this track", color=discord.Color.from_rgb(235, 204, 52)))
        
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if not ctx.user.guild.voice_client:
            vc: wavelink.Player = await ctx.user.voice.channel.connect(cls=wavelink.Player)
            await vc.guild.change_voice_state(channel=ctx.user.voice.channel, self_mute=False, self_deaf=True)
        else:
            vc: wavelink.Player = ctx.user.guild.voice_client

        try:
            await vc.play(song)
        except:
            mbed = discord.Embed(title="", description=f"Something went wrong while playing this track",color=discord.Color.from_rgb(235, 204, 52))
            return await ctx.response.send_message(embed=mbed)
            
        mbed = discord.Embed(title="Now Playing",color=discord.Color.from_rgb(235, 204, 52))
        mbed.add_field(name="Song", value=f"{song.title}", inline=False)
        await ctx.response.send_message(embed=mbed)

    @app_commands.command(name="nowplaying", description="Show current playing song")
    @commands.guild_only()
    async def nowplaying(self, ctx: discord.Interaction):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            mbed = discord.Embed(title="", description=f"Discord is not connected to any voice channel",color=discord.Color.from_rgb(235, 204, 52))
            return await ctx.response.send_message(embed=mbed)

        if player.is_playing():
            mbed = discord.Embed(
                title=f"Now Playing: {player.track}",
                #you can add url as one the arugument over here, if you want the user to be able to open the video in youtube
                #url = f"{player.track.info['uri']}"
                color=discord.Color.from_rgb(235, 204, 52)
            )

            t_sec = int(player.track.length)
            hour = int(t_sec/3600)
            min = int((t_sec%3600)/60)
            sec = int((t_sec%3600)%60)
            length = f"{hour}hr {min}min {sec}sec" if not hour == 0 else f"{min}min {sec}sec"

            mbed.add_field(name="Artist", value=player.track.info['author'], inline=False)
            mbed.add_field(name="Length", value=f"{length}", inline=False)

            return await ctx.response.send_message(embed=mbed)
        else:
            mbed = discord.Embed(title="", description=f"Nothing is playing right now",color=discord.Color.from_rgb(235, 204, 52))
            return await ctx.response.send_message(embed=mbed)

    @app_commands.command(name="search", description="Search a song using search engine")
    @commands.guild_only()
    @app_commands.describe(song="Enter song title")
    async def search(self, ctx: discord.Interaction, song: str):
        self.playingTextChannel = ctx.channel.id
        try:
            tracks = await wavelink.YouTubeTrack.search(query=song)
        except:
            mbed = discord.Embed(title="", description=f"Something went wrong while searching for this track",color=discord.Color.from_rgb(235, 204, 52))
            return await ctx.response.send_message(embed=mbed)

        if tracks is None:
            mbed = discord.Embed(title="", description=f"No tracks found",color=discord.Color.from_rgb(235, 204, 52))
            return await ctx.response.send_message(embed=mbed)

        mbed = discord.Embed(
            title="Select the track: ",
            description=("\n".join(f"**{i+1}. {t.title}**" for i, t in enumerate(tracks[:5]))),
            color = discord.Color.from_rgb(235, 204, 52)
        )
        msg = await ctx.response.send_message(embed=mbed)
        full_msg = await ctx.edit_original_response(embed=mbed)

        emojis_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '❌']
        emojis_dict = {
            '1️⃣': 0,
            "2️⃣": 1,
            "3️⃣": 2,
            "4️⃣": 3,
            "5️⃣": 4,
            "❌": -1
        }

        for emoji in list(emojis_list[:min(len(tracks), len(emojis_list))]):
            await full_msg.add_reaction(emoji)

        def check(res, user):
            return(res.emoji in emojis_list and user == ctx.user and res.message.id == full_msg.id)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            return
        else:
            pass

        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        try:
            if emojis_dict[reaction.emoji] == -1: return
            choosed_track = tracks[emojis_dict[reaction.emoji]]
        except:
            return

        vc: wavelink.Player = ctx.user.guild.voice_client or await ctx.user.voice.channel.connect(cls=wavelink.Player)
        await vc.guild.change_voice_state(channel=ctx.user.voice.channel, self_mute=False, self_deaf=True)

        if not vc.is_playing() and not vc.is_paused():
            try:
                await vc.play(choosed_track)
                mbed = discord.Embed(title="Now Playing",color=discord.Color.from_rgb(235, 204, 52))
                mbed.add_field(name="Song", value=f"{choosed_track}", inline=False)
                msg = await ctx.edit_original_response(embed=mbed)
                await msg.clear_reactions()

            except Exception as err:
                print(err)
                mbed = discord.Embed(title="", description=f"Something went wrong while playing this track",color=discord.Color.from_rgb(235, 204, 52))
                msg = await ctx.edit_original_response(embed=mbed)
                await msg.clear_reactions()
        else:
            self.queue.append(choosed_track)
            mbed = discord.Embed(title="", description=f"Added to queue " + "**"+choosed_track.title+"**",color=discord.Color.from_rgb(235, 204, 52))
            msg = await ctx.edit_original_response(embed=mbed)
            await msg.clear_reactions()

    @app_commands.command(name="skip", description="Skip to the next song")
    @commands.guild_only()
    async def skip(self, ctx: discord.Interaction):
        channel = ctx.channel
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if not len(self.queue) == 0:
            next_track: wavelink.Track = self.queue[0]
            try:
                await player.play(next_track)
                mbed = discord.Embed(title="", description=f"Skipped",color=discord.Color.from_rgb(235, 204, 52))
                await ctx.response.send_message(embed=mbed)
            except:
                mbed = discord.Embed(title="", description=f"Something went wrong while playing this track",color=discord.Color.from_rgb(235, 204, 52))
                return await ctx.response.send_message(embed=mbed)
            
            mbed = discord.Embed(title="Now Playing",color=discord.Color.from_rgb(235, 204, 52))
            mbed.add_field(name="Song", value=f"{next_track.title}", inline=False)
            await channel.send(embed=mbed)
        else:
            await player.stop()
            mbed = discord.Embed(title="", description=f"The queue is empty",color=discord.Color.from_rgb(235, 204, 52))
            await ctx.response.send_message(embed=mbed)

    @app_commands.command(name='queue', description="Show song queue list")
    @commands.guild_only()
    async def queue_list(self, ctx: discord.Interaction):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)
        
        if not len(self.queue) == 0:
            mbed = discord.Embed(
                title=f"Now playing: {player.track}" if player.is_playing else "Queue: ",
                description = "\n".join(f"**{i+1}. {track}**" for i, track in enumerate(self.queue[:20])) if not player.is_playing else "**Queue: **\n"+"\n".join(f"**{i+1}. {track}**" for i, track in enumerate(self.queue[:20])),
                color=discord.Color.from_rgb(235, 204, 52)
            )
            return await ctx.response.send_message(embed=mbed)
        else:
            mbed = discord.Embed(title="", description=f"The queue is empty",color=discord.Color.from_rgb(235, 204, 52))
            return await ctx.response.send_message(embed=mbed)

    @app_commands.command(name="delete", description="Delete a song from queue")
    @commands.guild_only()
    @app_commands.describe(index="Select which song you want to delete from the queue")
    async def delete(self, ctx: discord.Interaction, index: int):
        if not len(self.queue) == 0:
            if index > len(self.queue):
                mbed = discord.Embed(title="", description=f"The index is out of range",color=discord.Color.from_rgb(235, 204, 52))
                return await ctx.response.send_message(embed=mbed)
            else:
                del self.queue[index-1]
                mbed = discord.Embed(title="", description=f"Deleted the track at index {index}",color=discord.Color.from_rgb(235, 204, 52))
                return await ctx.response.send_message(embed=mbed)
        else:
            mbed = discord.Embed(title="", description=f"The queue is empty",color=discord.Color.from_rgb(235, 204, 52))
            return await ctx.response.send_message(embed=mbed)

async def setup(bot: commands.Bot) -> None: # Important Code!
  await bot.add_cog(Music(bot)) # add this file as a cog, so the main file can run it