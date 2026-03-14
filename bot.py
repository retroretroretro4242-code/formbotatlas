import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import os
from datetime import timedelta
import time

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

VOICE_CHANNEL_ID = 1482421665890570290

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

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

ticket_counter = 0
warnings = {}
join_tracker = []

# =========================
# YETKİLİ KONTROL
# =========================

def is_yetkili(member):
    return any(role.id in YETKILI_ROLLER for role in member.roles)

# =========================
# CEZA SİSTEMİ
# =========================

async def ceza_ver(member, reason):

    guild = member.guild
    log = guild.get_channel(LOG_CHANNEL_ID)

    warnings.setdefault(member.id, 0)
    warnings[member.id] += 1

    level = warnings[member.id]

    if level == 1:
        duration = timedelta(minutes=5)
        text = "1. Uyarı → 5 dakika timeout"

    elif level == 2:
        duration = timedelta(minutes=10)
        text = "2. Uyarı → 10 dakika timeout"

    else:
        duration = timedelta(days=1)
        text = "3. Uyarı → 1 gün mute"

    try:
        await member.timeout(duration, reason=reason)
    except:
        pass

    if log:
        embed = discord.Embed(
            title="⚠️ Otomatik Ceza",
            description=f"{member.mention}\n{text}\nSebep: {reason}",
            color=0xe67e22
        )
        await log.send(embed=embed)

# =========================
# VERIFY BUTTON
# =========================

class VerifyButton(View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(
            label="Doğrulan",
            emoji="✅",
            style=discord.ButtonStyle.green,
            custom_id="verify_button"
        ))

# =========================
# GELİŞMİŞ TICKET SİSTEMİ
# =========================

class TicketKategori(View):

    def __init__(self):
        super().__init__(timeout=None)

        buttons = [
            ("💰 Sipariş","ticket_siparis",discord.ButtonStyle.green),
            ("🛠 Destek","ticket_destek",discord.ButtonStyle.blurple),
            ("📦 Proje","ticket_proje",discord.ButtonStyle.gray),
            ("🎁 Ücretsiz","ticket_ucretsiz",discord.ButtonStyle.success),
            ("❓ Diğer","ticket_diger",discord.ButtonStyle.red)
        ]

        for label,cid,style in buttons:
            self.add_item(Button(label=label,custom_id=cid,style=style))


class TicketKapat(View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(
            label="🔒 Ticket Kapat",
            style=discord.ButtonStyle.red,
            custom_id="ticket_kapat"
        ))

# =========================
# HOŞGELDİN + ANTIRAID
# =========================

@bot.event
async def on_member_join(member):

    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        await member.add_roles(role)

    join_tracker.append(time.time())
    join_tracker[:] = [t for t in join_tracker if time.time()-t < 10]

    if len(join_tracker) >= 5:

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            await log.send("🚨 **ANTI RAID UYARISI! Çok hızlı giriş algılandı.**")

# =========================
# MESAJ KORUMA
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if is_yetkili(message.author):
        await bot.process_commands(message)
        return

    content = message.content
    lower = content.lower()

    # REKLAM
    if any(x in lower for x in ["discord.gg","http://","https://",".gg/"]):

        await message.delete()
        await ceza_ver(message.author,"Reklam")
        return

    # KÜFÜR
    if any(x in lower for x in ["amk","aq","orospu","salak"]):

        await message.delete()
        await ceza_ver(message.author,"Küfür")
        return

    # CAPS LOCK
    if len(content) > 8:

        upper = sum(1 for c in content if c.isupper())

        if upper / len(content) > 0.7:

            await message.delete()
            await ceza_ver(message.author,"Caps spam")
            return

    await bot.process_commands(message)

# =========================
# BUTTON EVENT
# =========================

@bot.event
async def on_interaction(interaction):

    global ticket_counter

    if interaction.type != discord.InteractionType.component:
        return

    cid = interaction.data["custom_id"]

    # VERIFY

    if cid == "verify_button":

        role = interaction.guild.get_role(VERIFY_ROLE_ID)

        await interaction.user.add_roles(role)

        await interaction.response.send_message(
            "✅ Doğrulandın!",
            ephemeral=True
        )
        return

    # TICKET AÇ

    if cid.startswith("ticket_") and cid != "ticket_kapat":

        ticket_counter += 1

        kategori = bot.get_channel(TICKET_KATEGORI_ID)

        kanal = await interaction.guild.create_text_channel(
            name=f"ticket-{ticket_counter}",
            category=kategori
        )

        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_counter}",
            description=(
                f"{interaction.user.mention} ticket açtı.\n\n"
                "📌 Lütfen aşağıdaki bilgileri yaz:\n"
                "• Ne istiyorsunuz?\n"
                "• Proje detayları\n"
                "• Varsa görseller"
            ),
            color=0x2ecc71
        )

        await kanal.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketKapat()
        )

        await interaction.response.send_message(
            f"Ticket oluşturuldu: {kanal.mention}",
            ephemeral=True
        )

        return

    # TICKET KAPAT

    if cid == "ticket_kapat":

        await interaction.response.send_message("🔒 Ticket kapatılıyor...")

        await interaction.channel.delete()

# =========================
# KOMUTLAR
# =========================

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction):

    embed = discord.Embed(
        title="🎫 Destek Merkezi",
        description=(
            "Nova Project destek sistemine hoş geldin.\n\n"
            "Aşağıdaki kategorilerden birini seçerek ticket açabilirsin.\n\n"
            "⏱ Ortalama cevap süresi: 5-15 dakika"
        ),
        color=0x5865F2
    )

    await interaction.response.send_message(
        embed=embed,
        view=TicketKategori()
    )

@bot.tree.command(name="onay-mesaji")
async def verify(interaction):

    ch = bot.get_channel(VERIFY_CHANNEL_ID)

    embed = discord.Embed(
        title="🔐 Sunucu Doğrulama",
        description="Butona basarak doğrulan.",
        color=0x2ecc71
    )

    await ch.send(embed=embed,view=VerifyButton())

    await interaction.response.send_message(
        "Verify panel gönderildi.",
        ephemeral=True
    )

# =========================
# READY
# =========================

@bot.event
async def on_ready():

    print(f"Bot hazır: {bot.user}")

    bot.add_view(VerifyButton())
    bot.add_view(TicketKategori())
    bot.add_view(TicketKapat())

    await bot.tree.sync()

    # 7/24 SES KANALI

    channel = bot.get_channel(VOICE_CHANNEL_ID)

    if channel:

        if not channel.guild.voice_client:

            await channel.connect()

# =========================
# RUN
# =========================

bot.run(TOKEN)
