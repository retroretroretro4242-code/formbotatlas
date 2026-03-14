import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select
import os
from datetime import timedelta
from collections import defaultdict

TOKEN = os.getenv("TOKEN")

# =========================
# ID AYARLARI
# =========================

WELCOME_CHANNEL_ID = 1482033833091010661
LOG_CHANNEL_ID = 1482028188639952933

VERIFY_CHANNEL_ID = 1482031063936139264
VERIFY_ROLE_ID = 1482021882378059876

AUTO_ROLE_ID = 1482031140897292563

TICKET_KATEGORI_ID = 1482030116036149319
STATS_CATEGORY_ID = 123456789  # değiştir

# =========================
# YETKİLİ
# =========================

YETKILI_ROLLER = [
1482030116036149319,
1482030233056968827,
1482030334877896796
]

# =========================
# GLOBAL
# =========================

invite_cache = {}
invite_count = defaultdict(int)

KUFURLER = ["amk","aq","orospu","piç","salak","aptal","siktir"]

ticket_counter = 0

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# İSTATİSTİK
# =========================

async def update_stats(guild):

    category = bot.get_channel(STATS_CATEGORY_ID)
    if not category:
        return

    total = guild.member_count
    bots = len([m for m in guild.members if m.bot])
    humans = total - bots

    data = {
        "👥 Toplam": total,
        "🧑 Üyeler": humans,
        "🤖 Botlar": bots
    }

    for name, value in data.items():

        ch = discord.utils.get(category.voice_channels,
                               name__startswith=name)

        if ch:
            await ch.edit(name=f"{name}: {value}")
        else:
            await guild.create_voice_channel(
                name=f"{name}: {value}",
                category=category
            )

# =========================
# MEMBER JOIN
# =========================

@bot.event
async def on_member_join(member):

    guild = member.guild

    # autorole
    role = guild.get_role(AUTO_ROLE_ID)
    if role:
        await member.add_roles(role)

    # invite system
    try:
        new_invites = await guild.invites()
        old_invites = invite_cache.get(guild.id, {})

        for inv in new_invites:
            if inv.uses > old_invites.get(inv.code, 0):
                invite_count[inv.inviter.id] += 1

        invite_cache[guild.id] = {i.code:i.uses for i in new_invites}
    except:
        pass

    # welcome
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title=f"👋 Hoş geldin {member.name}",
            color=0x5865F2
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

    await update_stats(guild)

@bot.event
async def on_member_remove(member):
    await update_stats(member.guild)

# =========================
# DOĞRULAMA
# =========================

@bot.event
async def on_raw_reaction_add(payload):

    if payload.channel_id != VERIFY_CHANNEL_ID:
        return

    if str(payload.emoji) != "✅":
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if member.bot:
        return

    role = guild.get_role(VERIFY_ROLE_ID)
    if role:
        await member.add_roles(role)

@bot.tree.command(name="dogrulama-mesaji")
async def verifymsg(interaction: discord.Interaction):

    embed = discord.Embed(
        title="✅ Doğrulama",
        description="Doğrulanmak için ✅ bas.",
        color=0x2ecc71
    )

    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("✅")

    await interaction.response.send_message(
        "Gönderildi.", ephemeral=True)

# =========================
# MESAJ KORUMA
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if any(x in message.content.lower()
           for x in ["discord.gg","http://","https://"]):

        if not any(r.id in YETKILI_ROLLER
                   for r in message.author.roles):
            await message.delete()

    if any(k in message.content.lower() for k in KUFURLER):

        if not any(r.id in YETKILI_ROLLER
                   for r in message.author.roles):

            await message.delete()
            warn = await message.channel.send(
                f"🚫 {message.author.mention} küfür yasak."
            )
            await warn.delete(delay=5)

    await bot.process_commands(message)

# =========================
# INVITES
# =========================

@bot.tree.command(name="invites")
async def invites(interaction: discord.Interaction,
                  member: discord.Member=None):

    member = member or interaction.user
    count = invite_count[member.id]

    embed = discord.Embed(
        title="📨 Invite",
        description=f"{member.mention} → {count} invite",
        color=0x5865F2
    )

    await interaction.response.send_message(embed=embed)

# =========================
# TICKET SYSTEM
# =========================

class TicketSelect(Select):

    def __init__(self):

        options = [
            discord.SelectOption(label="Sipariş",emoji="💰",value="siparis"),
            discord.SelectOption(label="Destek",emoji="🛠",value="destek"),
            discord.SelectOption(label="Proje",emoji="📦",value="proje"),
            discord.SelectOption(label="Ücretsiz",emoji="🎁",value="ucretsiz"),
            discord.SelectOption(label="Diğer",emoji="❓",value="diger"),
        ]

        super().__init__(placeholder="Kategori seç",
                         options=options,
                         custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):

        global ticket_counter
        ticket_counter += 1

        category = bot.get_channel(TICKET_KATEGORI_ID)

        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{ticket_counter}",
            category=category
        )

        embed = discord.Embed(
            title="🎫 Ticket Açıldı",
            description=f"{interaction.user.mention} destek bekliyor.",
            color=0x2ecc71
        )

        await channel.send(
            interaction.user.mention,
            embed=embed,
            view=TicketClose()
        )

        await interaction.response.send_message(
            f"Oluşturuldu: {channel.mention}",
            ephemeral=True
        )

class TicketPanel(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketClose(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(
            label="🔒 Ticket Kapat",
            style=discord.ButtonStyle.red,
            custom_id="ticket_close"
        ))

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 Destek Merkezi",
        description="Kategori seçerek ticket aç.",
        color=0x5865F2
    )

    await interaction.response.send_message(
        embed=embed,
        view=TicketPanel()
    )

@bot.event
async def on_interaction(interaction: discord.Interaction):

    if interaction.type != discord.InteractionType.component:
        return

    if interaction.data["custom_id"] == "ticket_close":
        await interaction.channel.delete()

# =========================
# MODERASYON
# =========================

def yetkili():
    async def predicate(interaction: discord.Interaction):
        return any(r.id in YETKILI_ROLLER
                   for r in interaction.user.roles)
    return app_commands.check(predicate)

@bot.tree.command(name="ban")
@yetkili()
async def ban(interaction: discord.Interaction, member: discord.Member):
    await member.ban()
    await interaction.response.send_message("Banlandı.")

@bot.tree.command(name="kick")
@yetkili()
async def kick(interaction: discord.Interaction, member: discord.Member):
    await member.kick()
    await interaction.response.send_message("Kicklendi.")

@bot.tree.command(name="timeout")
@yetkili()
async def timeout(interaction: discord.Interaction,
                  member: discord.Member,
                  dakika:int):

    await member.timeout(timedelta(minutes=dakika))
    await interaction.response.send_message("Timeout verildi.")

# =========================
# READY
# =========================

@bot.event
async def on_ready():

    print(f"Bot hazır: {bot.user}")

    await bot.tree.sync()

    # invite cache yükle
    for guild in bot.guilds:
        try:
            invites = await guild.invites()
            invite_cache[guild.id] = {i.code:i.uses for i in invites}
        except:
            pass

    # persistent views
    bot.add_view(TicketPanel())
    bot.add_view(TicketClose())

bot.run(TOKEN)
