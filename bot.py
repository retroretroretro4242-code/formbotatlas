import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import os

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

# =========================
# YETKİLİ ROLLER
# =========================

YETKILI_ROLLER = [
1482030116036149319,
1482030233056968827,
1482030334877896796
]

# =========================
# BOT
# =========================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# HOŞGELDİN
# =========================

@bot.event
async def on_member_join(member):

    role = member.guild.get_role(AUTO_ROLE_ID)

    if role:
        await member.add_roles(role)

    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    embed = discord.Embed(
        title=f"👋 Hoş geldin, {member.name}!",
        description="LBDev | Software @2026 ailesine katıldığın için mutluyuz.",
        color=0x8e44ad
    )

    embed.add_field(
        name="",
        value=(
            "🎮 FiveM & Minecraft yazılım çözümleri\n"
            "🌐 Web sitesi tasarım ve geliştirme\n"
            "🤖 Özel Discord bot geliştirme\n"
            "🛡️ 8+ yıl tecrübe · 150+ sunucu · 2.000+ sipariş"
        ),
        inline=False
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    if channel:
        await channel.send(embed=embed)

    try:
        await member.send(embed=embed)
    except:
        pass

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

        embed = discord.Embed(
            title="✅ Doğrulama Başarılı",
            description="LBDev | Software @2026 sunucusunda başarıyla doğrulandın!",
            color=0x2ecc71
        )

        embed.add_field(
            name="",
            value=(
                "💚 Artık tüm kanallara erişim sağlayabilirsin\n"
                "📩 Yardıma ihtiyacın olursa destek talebi oluşturabilirsin\n"
                "🎉 Topluluğumuza hoş geldin!"
            ),
            inline=False
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        try:
            await member.send(embed=embed)
        except:
            pass

# =========================
# REKLAM KORUMA
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    reklam = ["discord.gg","http://","https://"]

    if any(x in message.content.lower() for x in reklam):

        if not any(role.id in YETKILI_ROLLER for role in message.author.roles):

            await message.delete()

    await bot.process_commands(message)

# =========================
# TICKET
# =========================

class TicketView(View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(label="Ekip Alım",style=discord.ButtonStyle.green,custom_id="ticket_ekip"))
        self.add_item(Button(label="Yetkili Alım",style=discord.ButtonStyle.blurple,custom_id="ticket_yetkili"))
        self.add_item(Button(label="Diğer",style=discord.ButtonStyle.gray,custom_id="ticket_diger"))

class CloseTicket(View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(label="Ticket Kapat",style=discord.ButtonStyle.red,custom_id="ticket_kapat"))

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 Ticket Paneli",
        description="Butona basarak ticket oluşturabilirsiniz.",
        color=0xf1c40f
    )

    await interaction.response.send_message(embed=embed,view=TicketView())

# =========================
# BUTTON EVENT
# =========================

@bot.event
async def on_interaction(interaction: discord.Interaction):

    if interaction.type != discord.InteractionType.component:
        return

    cid = interaction.data["custom_id"]

    if cid.startswith("ticket_") and cid != "ticket_kapat":

        kategori = bot.get_channel(TICKET_KATEGORI_ID)

        kanal = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=kategori
        )

        embed = discord.Embed(
            title="🎫 Ticket Oluşturuldu",
            description=f"{interaction.user.mention} destek yakında gelecek.",
            color=0xf1c40f
        )

        await kanal.send(interaction.user.mention,embed=embed,view=CloseTicket())

        await interaction.response.send_message(
            f"Ticket oluşturuldu: {kanal.mention}",
            ephemeral=True
        )

    if cid == "ticket_kapat":

        await interaction.channel.delete()

# =========================
# KULLANICI BİLGİ
# =========================

@bot.tree.command(name="kullanici-bilgi")
async def userinfo(interaction: discord.Interaction, member: discord.Member):

    embed = discord.Embed(
        title="👤 Kullanıcı Bilgisi",
        color=0x3498db
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(name="İsim",value=member.name)
    embed.add_field(name="ID",value=member.id)
    embed.add_field(name="Hesap Oluşturma",value=member.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="Sunucuya Katılım",value=member.joined_at.strftime("%d/%m/%Y"))

    await interaction.response.send_message(embed=embed)

# =========================
# MODERASYON
# =========================

def yetkili():

    async def predicate(interaction: discord.Interaction):

        return any(role.id in YETKILI_ROLLER for role in interaction.user.roles)

    return app_commands.check(predicate)

@bot.tree.command(name="ban")
@yetkili()
async def ban(interaction: discord.Interaction, member: discord.Member, sebep: str = "Sebep belirtilmedi"):

    await member.ban(reason=sebep)

    await interaction.response.send_message(f"{member} banlandı.")

@bot.tree.command(name="kick")
@yetkili()
async def kick(interaction: discord.Interaction, member: discord.Member):

    await member.kick()

    await interaction.response.send_message(f"{member} kicklendi.")

@bot.tree.command(name="timeout")
@yetkili()
async def timeout(interaction: discord.Interaction, member: discord.Member, dakika: int):

    from datetime import timedelta

    await member.timeout(timedelta(minutes=dakika))

    await interaction.response.send_message(f"{member} {dakika} dakika timeout aldı.")

@bot.tree.command(name="temizle")
@yetkili()
async def temizle(interaction: discord.Interaction, miktar: int):

    await interaction.channel.purge(limit=miktar)

    await interaction.response.send_message(
        f"{miktar} mesaj silindi.",
        ephemeral=True
    )

# =========================
# READY
# =========================

@bot.event
async def on_ready():

    print(f"Bot hazır: {bot.user}")

    await bot.tree.sync()

# =========================
# RUN
# =========================

bot.run(TOKEN)
