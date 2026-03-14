import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Select
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
TICKET_LOG_CHANNEL = 1482028188639952933

STATS_CATEGORY_ID = 123456789  # İstatistik kategori ID

# =========================
# YETKİLİ ROLLER
# =========================

YETKILI_ROLLER = [
1482030116036149319,
1482030233056968827,
1482030334877896796
]

# =========================
# KORUMA LİSTELERİ
# =========================

KUFURLER = ["amk","aq","orospu","piç","salak","aptal","siktir"]

invite_cache = {}
invite_count = defaultdict(int)

ticket_sayac = 0

# =========================
# BOT
# =========================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# SUNUCU İSTATİSTİK
# =========================

async def update_stats(guild):

    category = bot.get_channel(STATS_CATEGORY_ID)
    if not category:
        return

    total = guild.member_count
    bots = len([m for m in guild.members if m.bot])
    humans = total - bots

    stats = {
        "👥 Toplam": total,
        "🧑 Üyeler": humans,
        "🤖 Botlar": bots
    }

    for name, value in stats.items():

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
# HOŞGELDİN + INVITE
# =========================

@bot.event
async def on_member_join(member):

    guild = member.guild

    # AUTO ROLE
    role = guild.get_role(AUTO_ROLE_ID)
    if role:
        await member.add_roles(role)

    # INVITE TAKİP
    try:
        new_invites = await guild.invites()
        old_invites = invite_cache[guild.id]

        for invite in new_invites:
            if invite.uses > old_invites.get(invite.code, 0):
                inviter = invite.inviter
                invite_count[inviter.id] += 1

        invite_cache[guild.id] = {i.code: i.uses for i in new_invites}
    except:
        pass

    # WELCOME
    embed = discord.Embed(
        title=f"👋 Hoş geldin, {member.name}!",
        description="Nova Project ailesine katıldığın için mutluyuz.",
        color=0x5865F2
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    ch = bot.get_channel(WELCOME_CHANNEL_ID)
    if ch:
        await ch.send(embed=embed)

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

    if role not in member.roles:
        await member.add_roles(role)

# doğrulama mesajı gönder
@bot.tree.command(name="dogrulama-mesaji")
async def verifymsg(interaction: discord.Interaction):

    embed = discord.Embed(
        title="✅ Sunucu Doğrulama",
        description="Aşağıdaki emojiye basarak doğrulan.",
        color=0x2ecc71
    )

    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("✅")

    await interaction.response.send_message(
        "Doğrulama mesajı gönderildi.",
        ephemeral=True
    )

# =========================
# MESAJ KORUMA
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    # REKLAM
    reklam = ["discord.gg","http://","https://"]

    if any(x in message.content.lower() for x in reklam):
        if not any(role.id in YETKILI_ROLLER for role in message.author.roles):
            await message.delete()

    # KÜFÜR
    if any(k in message.content.lower() for k in KUFURLER):
        if not any(role.id in YETKILI_ROLLER for role in message.author.roles):
            await message.delete()
            warn = await message.channel.send(
                f"🚫 {message.author.mention} küfür yasak."
            )
            await warn.delete(delay=5)

    await bot.process_commands(message)

# =========================
# INVITES KOMUTU
# =========================

@bot.tree.command(name="invites")
async def invites(interaction: discord.Interaction,
                  member: discord.Member=None):

    member = member or interaction.user
    count = invite_count[member.id]

    embed = discord.Embed(
        title="📨 Davet Bilgisi",
        description=f"{member.mention} → {count} invite",
        color=0x5865F2
    )

    await interaction.response.send_message(embed=embed)

# =========================
# TICKET SİSTEMİ
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

        super().__init__(placeholder="Kategori seç...",
                         options=options)

    async def callback(self, interaction: discord.Interaction):

        global ticket_sayac
        ticket_sayac += 1

        kategori = bot.get_channel(TICKET_KATEGORI_ID)

        kanal = await interaction.guild.create_text_channel(
            name=f"ticket-{ticket_sayac}",
            category=kategori
        )

        embed = discord.Embed(
            title="🎫 Ticket Açıldı",
            description=f"{interaction.user.mention} destek bekliyor.",
            color=0x2ecc71
        )

        await kanal.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketKapat()
        )

        await interaction.response.send_message(
            f"Ticket: {kanal.mention}",
            ephemeral=True
        )

class TicketPanel(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketKapat(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            Button(label="🔒 Ticket Kapat",
                   style=discord.ButtonStyle.red,
                   custom_id="ticket_kapat")
        )

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

    if interaction.data["custom_id"] == "ticket_kapat":
        await interaction.channel.delete()

# =========================
# MODERASYON
# =========================

def yetkili():
    async def predicate(interaction: discord.Interaction):
        return any(role.id in YETKILI_ROLLER
                   for role in interaction.user.roles)
    return app_commands.check(predicate)

@bot.tree.command(name="ban")
@yetkili()
async def ban(interaction: discord.Interaction,
              member: discord.Member):

    await member.ban()
    await interaction.response.send_message("Banlandı.")

@bot.tree.command(name="kick")
@yetkili()
async def kick(interaction: discord.Interaction,
               member: discord.Member):

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

    # invite cache
    for guild in bot.guilds:
        invites = await guild.invites()
        invite_cache[guild.id] = {i.code:i.uses for i in invites}

bot.run(TOKEN)
