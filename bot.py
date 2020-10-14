import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv('.env')

#id = 702406379624988712

colour = ['yellow', 'white', 'red', 'purple', 'pink', 'orange', 'lime', 'green', 'cyan', 'brown', 'blue', 'black']
alive = ['<:auyellow:762553447903264798>', '<:auwhite:762553452886491136>', '<:aured:762553433966247947>', '<:aupurple:762553455272525825>', '<:aupink:762553442471903273>', '<:auorange:762553445097930783>', '<:aulime:762553462855958548>', '<:augreen:762553439916916736>', '<:aucyan:762553460394295326>', '<:aubrown:762553458007474186>', '<:aublue:762553437249863740>', '<:aublack:762553450382491658>']
dead = ['<:auyellowdead:762553478194921522>', '<:auwhitedead:762553483383144459>', '<:aureddead:762553465452756992>', '<:aupurpledead:762553485992132608>', '<:aupinkdead:762553473128333342>', '<:auorangedead:762553475602710538>', '<:aulimedead:762553493617377310>', '<:augreendead:762553470519083038>', '<:aucyandead:762553491066847232>', '<:aubrowndead:762553488152330272>', '<:aubluedead:762553467834859531>', '<:aublackdead:762553480942059540>']
msg_alive  = "Started a new game, react to this message with your colour!"
msg_dead = "React here once you die!"
channels = ["among-us", "bot-spam"]
players = []

message_dead = message_alive = game_commands = embed_alive = embed_dead = embed_game = None


def number(emote):
    for i in range(len(alive)):
        if str(emote) == alive[i]:
            return i

    for j in range(len(dead)):
        if str(emote) == dead[j]:
            return j

class Player:
    global colour
    def __init__(self, username, emote, uid):
        self.username = str(username)
        self.num = number(emote)
        self.colour = colour[self.num]
        self.alive = True
        self.uid = uid

    def update_colour(self, emote):
        self.num = number(emote)
        self.colour = colour[self.num]

    def killed(self):
        self.alive = False

    def not_killed(self):
        self.alive = True


def user_check (pl, username):
    for i in range(len(pl)):
        if pl[i].username == username:
            return i
    return -1

def number_check (pl, number):
    for i in range(len(pl)):
        if pl[i].num == number:
            return i
    return -1

def turn_undead(pl):
    for i in pl:
        i.not_killed()

client = commands.Bot(command_prefix="'")

@client.event
async def on_ready():
    print("Among Us bot in online!")

@client.command(aliases=['new', 'ng'])
async def newgame(ctx):
    global message_dead, message_alive, embed_alive, embed_dead
    embed_alive = discord.Embed(title="Players", description= msg_alive, colour = discord.Colour.green())
    embed_dead = discord.Embed(title="Death Log ☠", description= msg_dead, colour = discord.Colour.red())
    message_alive = await ctx.channel.send(embed=embed_alive)
    for i in alive:
        await message_alive.add_reaction(i)
    message_dead = await ctx.channel.send(embed=embed_dead)
    await ctx.message.delete()

@client.command(aliases=['start', 'sg'])
async def startgame(ctx):
    global players, game_commands, embed_game
    if len(players) >= 4:
        embed_game = discord.Embed(title="Stage of the Game", description="Lobby : 💺 | Meeting : 🔴 | Task = 💳", colour = discord.Colour.green())
        game_commands = await ctx.channel.send(embed=embed_game)
        for i in ["💺", "🔴", "💳"]:
            await game_commands.add_reaction(i)
    else:
        print("Can't start a game with less than 4 players!")
    await ctx.message.delete()

@client.command(aliases=['end', 'eg'])
async def endgame(ctx):
    global message_dead, embed_dead
    if not game_commands:
        ctx.message.channel.send("You can't end a game which never started!")
    else:
        embed_stats = discord.Embed(title="Final Report", description="GAME OVER!", colour = discord.Colour.dark_gold())
        for i in players:
            name, life = i.username[:-5], "alive" if i.alive else "dead"
            embed_stats.add_field(name= name, value= life, inline=False)
        await ctx.message.channel.send(embed= embed_stats)
        turn_undead(players)
        for i in players:
            try:
                await client.get_guild(702406379624988712).get_member(i.uid).edit(mute=False)
            except:
                pass
        embed_dead.clear_fields()
        await message_dead.edit(embed=embed_dead)
        await message_dead.clear_reactions()
        for i in players:
            await message_dead.add_reaction(dead[i.num])
    await ctx.message.delete()

@client.event
async def on_raw_reaction_add(payload):
    global message_dead, message_alive, game_commands, players, embed_alive, embed_game, embed_dead
    msg = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    if str(client.get_user(payload.user_id)) != 'Among Us Bot#4338' and msg==message_alive: #When players chose their colour
        if str(payload.emoji) in alive:
            if user_check(players, str(client.get_user(payload.user_id)))!= -1:
                await message_alive.remove_reaction(alive[players[user_check(players, str(client.get_user(payload.user_id)))].num], client.get_user(payload.user_id))
                players[user_check(players, str(client.get_user(payload.user_id)))].update_colour(str(payload.emoji))
                embed_alive.remove_field(user_check(players, str(client.get_user(payload.user_id))))
            else:
                if number_check(players, number(payload.emoji))!= -1:
                    await message_alive.remove_reaction(payload.emoji, client.get_user(payload.user_id))
                    await client.get_user(payload.user_id).send(f"""{players[number_check(players, number(payload.emoji))].username[:-5]} already chose {players[number_check(players, number(payload.emoji))].colour} choose a different colour""")
                else:
                    players.append(Player(client.get_user(payload.user_id), str(payload.emoji), payload.user_id))
            if user_check(players, str(client.get_user(payload.user_id)))!= -1 and number_check(players, number(payload.emoji))!= -1:
                await message_dead.add_reaction(dead[number(str(payload.emoji))])
                embed_alive.add_field(name = f"""{str(client.get_user(payload.user_id).name)}""", value=f"""chose {players[user_check(players, str(client.get_user(payload.user_id)))].colour}""", inline=False)
                await message_alive.edit(embed=embed_alive)
        else: #unnecessary reactions
            await message_alive.remove_reaction(payload.emoji, client.get_user(payload.user_id))

    elif str(client.get_user(payload.user_id)) != 'Among Us Bot#4338' and msg == game_commands:
        '''
        If I change the state of the game muting and unmuting happens
        '''
        if str(payload.emoji)  == "💺":
            try:
                embed_game.clear_fields()
            except:
                pass
            embed_game.add_field(name="State", value="💺 We are in the lobby right now!", inline=False)
            await game_commands.edit(embed=embed_game)
            # Unmute everyone
            for i in players:
                try:
                    await client.get_guild(702406379624988712).get_member(i.uid).edit(mute=False)
                except:
                    pass
        elif str(payload.emoji)  == "🔴":
            try:
                embed_game.clear_fields()
            except:
                pass
            embed_game.add_field(name="State", value="🔴 We are in a meeting right now! The dead don't talk!", inline=False)
            await game_commands.edit(embed=embed_game)
            #Unmute alive
            for i in players:
                if i.alive:
                    try:
                        await client.get_guild(702406379624988712).get_member(i.uid).edit(mute=False)
                    except:
                        pass
                else:
                    try:
                        await client.get_guild(702406379624988712).get_member(i.uid).edit(mute=True)
                    except:
                        pass
        elif str(payload.emoji)  == "💳":
            try:
                embed_game.clear_fields()
            except:
                pass
            embed_game.add_field(name="State", value="💳 Do your tasks like a good crewmate! AND NO TALKING!", inline=False)
            await game_commands.edit(embed=embed_game)
            #Mute everyone
            for i in players:
                try:
                    await client.get_guild(702406379624988712).get_member(i.uid).edit(mute=True)
                except:
                    pass
        await game_commands.remove_reaction(payload.emoji, client.get_user(payload.user_id))

    elif str(client.get_user(payload.user_id)) != 'Among Us Bot#4338' and msg == message_dead:
        if str(payload.emoji) in dead:
            for i in players:
                if i.num == number(payload.emoji):
                    i.killed()
                    embed_dead.add_field(name = f"""{i.username[:-5]}({alive[i.num]} ➡ {dead[i.num]}) has been killed!""", value= "Fs in the chat", inline=False)
                    await message_dead.edit(embed=embed_dead)
                    break
        else: #unnecessary reactions
            await message_dead.remove_reaction(payload.emoji, client.get_user(payload.user_id))

@client.event
async def on_raw_reaction_remove(payload):
    global message_dead, message_alive, players, embed_alive, embed_dead
    msg = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    if msg == message_alive:
        if user_check(players, client.get_user(payload.user_id)) != -1:
            await message_dead.remove_reaction(dead[number(str(payload.emoji))], msg.author)
        if payload.event_type != 'REACTION_REMOVE':
            embed_alive.remove_field(user_check(players, str(client.get_user(payload.user_id))))
            await message_alive.edit(embed=embed_dead)
            try:
                players.remove(players[user_check(players, str(client.get_user(payload.user_id)))])
            except:
                pass

    elif str(client.get_user(payload.user_id)) != 'Among Us Bot#4338' and msg == message_dead:
        for i in players:
            if i.num == number(payload.emoji):
                i.not_killed()
                embed_dead.add_field(name = f"""{i.username[:-5]}({dead[i.num]} ➡ {alive[i.num]}) was killed""", value = "but their death was greatly exaggerated", inline=False)
                await message_dead.edit(embed=embed_dead)
                break

@client.command(aliases=['tst', 't'])
async def test(ctx,*, arg):
    await ctx.send(arg)
    await ctx.message.delete()

@client.command(aliases=['clr', 'c'])
@commands.has_permissions(manage_messages = True)
async def clear(ctx, amount=2):
    await ctx.channel.purge(limit= amount)

client.run(os.getenv('token'))