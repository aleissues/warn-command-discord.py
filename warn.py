import discord, aiofiles
from discord.ext import commands

client = commands.Bot(command_prefix=".")

role = 843538178816081960

@client.event 
async def on_ready():
    for guild in client.guilds:
        async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp:
            pass
        client.warnings[guild.id] = {}
        
    for guild in client.guilds:
        async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
            lines = await file.readlines()
            
            for line in lines:
                data = line.split(" ")
                member_id = int(data[0])
                admin_id = int(data[1])
                reason = " ".join(data[2:]).strip("\n")
                
                try:
                    client.warnings[guild.id][member_id][0] += 1
                    client.warnings[guild.id][member_id][1].append((admin_id, reason))
                except KeyError:
                    client.warnings[guild.id][member_id] = [1, [(admin_id, reason)]]
    print(f"Bot is online | {client.user}")

@client.command()
@commands.has_role(role)
async def warn(ctx, member : discord.Member=None, *, reason=None):
    if member == ctx.message.author:
        embed=discord.Embed(color=0xff0000)
        embed.add_field(name="ERROR", value="You cannot warn yourself!", inline=False)
        await ctx.send(embed=embed)
        return
    
    if member is None:
        embed=discord.Embed(color=0xff0000)
        embed.add_field(name="ERROR", value="You must specify a member you wish to warn!", inline=False)
        await ctx.send(embed=embed)
        return
    
    if reason is None:
        embed=discord.Embed(color=0xff0000)
        embed.add_field(name="ERROR", value="You must specify a valid reason!", inline=False)
        await ctx.send(embed=embed)
        return
    
    try:
        first_warning = False
        client.warnings[ctx.guild.id][member.id][0] += 1
        client.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, reason))
        
    except KeyError:
        first_warning = True
        client.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, reason)]]
    
    count = client.warnings[ctx.guild.id][member.id][0]
    async with aiofiles.open(f"{member.guild.id}.txt", mode="a") as file:
        await file.write(f"{member.id} {ctx.author.id} {reason}\n")
    embed=discord.Embed(color=0x00ff62)
    embed.add_field(name="Member was warned", value=f"{member.mention} was warned for `{reason}`", inline=False)
    embed.set_footer(text=f"They now have {count} {'warning' if first_warning else 'warnings'}")
    await ctx.send(embed=embed)
    embed=discord.Embed(color=0x00ff62)
    embed.add_field(name="You have received a warning", value=f"Reason: `{reason}`", inline=False)
    embed.set_footer(text=f"You have {count} {'warning' if first_warning else 'warnings'}")
    await member.send(embed=embed)


@client.command()
@commands.has_role(role)
async def checkwarns(ctx, member: discord.Member=None):
    if member is None:
        embed=discord.Embed(color=0xff0000)
        embed.add_field(name="ERROR", value="You must specify a member you wish to check warnings on!", inline=False)
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(title=f"Warnings for {member}/{member.id}", description="", colour=discord.Colour.red())
    try:
        i = 1
        for admin_id, reason in client.warnings[ctx.guild.id][member.id][1]:
            admin = ctx.guild.get_member(admin_id)
            embed.description += f"Case: `#{i}` | Issued by: {admin.mention} | Reason: `{reason}` \n"
            i += 1
        await ctx.send(embed=embed)
        
    except KeyError:
        embed=discord.Embed(color=0xff0000)
        embed.add_field(name="CLEAN HISTORY", value="The user you mentioned has no active warnings!", inline=False)
        await ctx.send(embed=embed)
