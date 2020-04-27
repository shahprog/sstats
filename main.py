import discord
from discord.ext import commands
import sqlite3
import dotenv
import os

env_path = os.path.join(os.getcwd(), '.env')
dotenv.load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv("TOKEN")

client = commands.Bot(command_prefix="!")
db = sqlite3.connect("main.db")

client.remove_command('help')

db.execute("""
CREATE TABLE IF NOT EXISTS guild(
id INTEGER PRIMARY KEY,
gid INT NOT NULL,
cat INT NULL,
allchannel INT NULL,
userchannel INT NULL,
botchannel INT NULL,
rolechannel INT NULL,
onlinechannel INT NULL,
offlinechannel INT NULL,
textchannel INT NULL,
voicechannel INT NULL)
""")

@client.event
async def on_ready():
  print("Ready!")

@client.event
async def on_guild_join(guild):
  db.execute(f"INSERT INTO guild(gid) VALUES({guild.id})")
  db.commit()
  
@client.command()
async def ping(ctx):
  await ctx.send("Pong!")

@client.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
  """Setup this bot for a server"""
  
  query = db.execute(f"SELECT * FROM guild WHERE gid = {ctx.guild.id}")
  res = query.fetchone()
  cid = res[2]
  
  cat = discord.utils.get(ctx.guild.channels, id=cid)
  if cat != None:
    await ctx.send("Setup is already done please delete previous channels and category to resetup!")
  else:
    member_count = ctx.guild.member_count
    user_count = 0
    bot_count = 0
  
    for m in ctx.guild.members:
      if m.bot == False:
        user_count += 1
      elif m.bot:
        bot_count += 1
      #await ctx.send(m.name)
    over = {
      ctx.guild.default_role: discord.PermissionOverwrite(connect=False)
    }
  
    
    cat = await ctx.guild.create_category(name="ServerStats", overwrites=over)
    all = await ctx.guild.create_voice_channel(name="Members : " + str(member_count), category=cat)
    user = await ctx.guild.create_voice_channel(name="Users : " + str(user_count), category=cat)
    bot= await ctx.guild.create_voice_channel(name="Bots : " + str(bot_count), category=cat)
    
    await cat.edit(position=1)
    
    db.execute(f"UPDATE guild SET cat = {cat.id}, allchannel = {all.id}, userchannel = {user.id}, botchannel = {bot.id} WHERE gid = {ctx.guild.id}")
    db.commit()
    await ctx.send("Setup completed")

@client.command()
@commands.has_permissions(administrator=True)
async def enable(ctx, arr:str=None):
  """Enable specific counts"""
  query = db.execute(f"SELECT * FROM guild WHERE gid = {ctx.guild.id}")
  res = query.fetchone()
  catid = res[2]
  cat = discord.utils.get(ctx.guild.channels, id=catid)
  #await ctx.send(cat)
  
  if arr.lower() == 'online':
    
    onc = res[7]
    cn = discord.utils.get(ctx.guild.channels, id=onc)
    if cn != None:
      await ctx.send("Online member count already enabled!")
    else:
      sts = [discord.Status.online, discord.Status.idle, discord.Status.dnd]
      on_count = 0
      for m in ctx.guild.members:
        if m.status in sts:
          on_count += 1
    
      onc = await ctx.guild.create_voice_channel(name="Online : " + str(on_count), category=cat)
      db.execute(f"UPDATE guild SET onlinechannel = {onc.id} WHERE gid = {ctx.guild.id}")
      db.commit()
      await ctx.send("Online count enabled!")
    
  elif arr.lower() == 'offline':
    ofc = res[8]
    cn = discord.utils.get(ctx.guild.channels, id=ofc)
    if cn != None:
      await ctx.send("Offline member count already enabled!")
    else:
      sts = [discord.Status.offline, discord.Status.invisible]
      of_count = 0
      for m in ctx.guild.members:
        if m.status in sts:
          of_count += 1
    
      ofc = await ctx.guild.create_voice_channel(name="Offline : " + str(of_count), category=cat)
      db.execute(f"UPDATE guild SET offlinechannel = {ofc.id} WHERE gid = {ctx.guild.id}")
      db.commit()
      await ctx.send("Offline count enabled!")
  
  
  elif arr.lower() == 'bot':
    bc = res[5]
    bcn = discord.utils.get(ctx.guild.channels, id=bc)
    
    if bcn != None:
      await ctx.send("Bot count already enabled")
    else:
      of_count = 0
      for m in ctx.guild.members:
        if m.bot:
          of_count += 1
    
      ofc = await ctx.guild.create_voice_channel(name="Bots : " + str(of_count), category=cat)
      db.execute(f"UPDATE guild SET botchannel = {ofc.id} WHERE gid = {ctx.guild.id}")
      db.commit()
      await ctx.send("Bot count enabled!")
  
  elif arr.lower() == 'all':
    bc = res[3]
    bcn = discord.utils.get(ctx.guild.channels, id=bc)
    
    if bcn != None:
      await ctx.send("All member count already enabled")
    else:
      of_count = ctx.guild.member_count
      
      ofc = await ctx.guild.create_voice_channel(name="Members : " + str(of_count), category=cat)
      db.execute(f"UPDATE guild SET allchannel = {ofc.id} WHERE gid = {ctx.guild.id}")
      db.commit()
      await ctx.send("All member count enabled!")
  
  elif arr.lower() == 'users':
    bc = res[4]
    bcn = discord.utils.get(ctx.guild.channels, id=bc)
    
    if bcn != None:
      await ctx.send("User count already enabled")
    else:
      of_count = 0
      for m in ctx.guild.members:
        if m.bot == False:
          of_count += 1
    
      ofc = await ctx.guild.create_voice_channel(name="Users : " + str(of_count), category=cat)
      db.execute(f"UPDATE guild SET userchannel = {ofc.id} WHERE gid = {ctx.guild.id}")
      db.commit()
      await ctx.send("User member count enabled!")
  else:
    await ctx.send("Invalid type. Try `all`, `users`, `online`, `offline`, `bot`.")
  
  

@client.event
async def on_member_update(before, after):
  q = db.execute(f"SELECT * FROM guild WHERE gid = {after.guild.id}")
  r = q.fetchone()
  ons = [discord.Status.online, discord.Status.idle, discord.Status.dnd]
  
  if before.status in ons and after.status in ons:
    pass
  else:
    onc = r[7]
    ofc = r[8]
   
    on_count = 0
    of_count = 0
  
    for m in after.guild.members:
      if m.status in ons:
        on_count += 1
      else:
        of_count += 1
  
    oncn = discord.utils.get(after.guild.channels, id=onc)
    ofcn = discord.utils.get(after.guild.channels, id=ofc)

    try:
      prev_name = oncn.name
      new_name = prev_name.split(":")[0] + ": " + str(on_count)
      
      await oncn.edit(name=new_name)
    except:
      pass
  
    try:
      prev_name = ofcn.name
      new_name = prev_name.split(":")[0] + ": " + str(of_count)
      
      await ofcn.edit(name=new_name)
      #await ofcn.edit(name="Offline : " + str(of_count))
    except:
      pass
  
@client.event
async def on_member_join(member):
  q = db.execute(f"SELECT * FROM guild WHERE gid = {member.guild.id}")
  r = q.fetchone()
  ons = [discord.Status.online, discord.Status.idle, discord.Status.dnd]
 
  onc = r[7]
  ofc = r[8]
  ac = r[3]
  uc = r[4]
  bc = r[5]
  rc = r[6]
  
  on_count = 0
  of_count = 0
  a_count = member.guild.member_count
  u_count = 0
  b_count = 0
  
  
  for m in member.guild.members:
    if m.bot == False:
      u_count += 1
    elif m.bot:
      b_count += 1
    
    if m.status in ons:
      on_count += 1
    else:
      of_count += 1
  
  oncn = discord.utils.get(member.guild.channels, id=onc)
  ofcn = discord.utils.get(member.guild.channels, id=ofc)
  acn = discord.utils.get(member.guild.channels, id=ac)
  ucn = discord.utils.get(member.guild.channels, id=uc)
  bcn = discord.utils.get(member.guild.channels, id=bc)
  rcn = discord.utils.get(member.guild.channels, id=rc)
  
  try:
      prev_name = oncn.name
      new_name = prev_name.split(":")[0] + ": " + str(on_count)
      
      await oncn.edit(name=new_name)
      
      #await oncn.edit(name="Online : " + str(on_count))
  except:
      pass
      
  try:
      prev_name = ofcn.name
      new_name = prev_name.split(":")[0] + ": " + str(of_count)
      
      await ofcn.edit(name=new_name)
      #await ofcn.edit(name="Offline : " + str(of_count))
  except:
      pass
  
  try:
      prev_name = acn.name
      new_name = prev_name.split(":")[0] + ": " + str(a_count)
      
      await acn.edit(name=new_name)
      #await acn.edit(name="Members : " + str(a_count))
  except:
      pass
  
  try:
      prev_name = ucn.name
      new_name = prev_name.split(":")[0] + ": " + str(u_count)
      
      await ucn.edit(name=new_name)
      #await ucn.edit(name="Users : " + str(u_count))
  except:
      pass
  
  try:
      if member.bot:
          prev_name = bcn.name
          new_name = prev_name.split(":")[0] + ": " + str(b_count)
      
          await bcn.edit(name=new_name)
          #await bcn.edit(name="Bots : " + str(b_count))
  except:
      pass
  
  
  
@client.event
async def on_member_remove(member):
  q = db.execute(f"SELECT * FROM guild WHERE gid = {member.guild.id}")
  r = q.fetchone()
  ons = [discord.Status.online, discord.Status.idle, discord.Status.dnd]
  
  
  onc = r[7]
  ofc = r[8]
  ac = r[3]
  uc = r[4]
  bc = r[5]
  rc = r[6]
  
  on_count = 0
  of_count = 0
  a_count = member.guild.member_count
  u_count = 0
  b_count = 0
  
  for m in member.guild.members:
    if m.bot == True:
      b_count += 1
    
    if m.status in ons:
      on_count += 1
    else:
      of_count += 1
  
  u_count = a_count - b_count
  
  
  oncn = discord.utils.get(member.guild.channels, id=onc)
  ofcn = discord.utils.get(member.guild.channels, id=ofc)
  acn = discord.utils.get(member.guild.channels, id=ac)
  ucn = discord.utils.get(member.guild.channels, id=uc)
  bcn = discord.utils.get(member.guild.channels, id=bc)
  rcn = discord.utils.get(member.guild.channels, id=rc)
  
  try:
      prev_name = oncn.name
      new_name = prev_name.split(":")[0] + ": " + str(on_count)
      
      await oncn.edit(name=new_name)
      
      #await oncn.edit(name="Online : " + str(on_count))
  except:
      pass
      
  try:
      prev_name = ofcn.name
      new_name = prev_name.split(":")[0] + ": " + str(of_count)
      
      await ofcn.edit(name=new_name)
      #await ofcn.edit(name="Offline : " + str(of_count))
  except:
      pass
  
  try:
      prev_name = acn.name
      new_name = prev_name.split(":")[0] + ": " + str(a_count)
      
      await acn.edit(name=new_name)
      #await acn.edit(name="Members : " + str(a_count))
  except:
      pass
  
  try:
      prev_name = ucn.name
      new_name = prev_name.split(":")[0] + ": " + str(u_count)
      
      await ucn.edit(name=new_name)
      #await ucn.edit(name="Users : " + str(u_count))
  except:
      pass
  
  try:
      if member.bot:
          prev_name = bcn.name
          new_name = prev_name.split(":")[0] + ": " + str(b_count)
      
          await bcn.edit(name=new_name)
          #await bcn.edit(name="Bots : " + str(b_count))
  except:
      pass
  

@client.command()
async def isbot(ctx, user:discord.Member):
  """Check a member is bot or not"""
  if user.bot:
    await ctx.send("True")
  else: await ctx.send("False")

@client.command()
async def help(ctx):
  msg = ""
  ttl =  "Help for Server Stats bot\n\n"
  msg += "**!setup** - To setup this bot for your server.\n"
  msg += "**!enable [type]** To enable specific count. e.g **!enable all**\n\nTypes are -"
  msg += "\n`all` - Will enable all member count that includes bot and normal members\n"
  msg += "`users` - Will enable user count. Means who are normal member. No bot.\n"
  msg += "`bot` - Will enable bot count.\n"
  msg += "`online` - Will enable online member count.\n"
  msg += "`offline` - Will enable offline member count.\n"
  
  embed = discord.Embed(color=ctx.author.color, description=msg)
  embed.set_author(name="Help for ServerStats bot", icon_url=client.user.avatar_url)
  
  
  await ctx.send(embed=embed)

client.load_extension("jishaku")
client.run(TOKEN)