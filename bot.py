import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import time
import json
from datetime import timedelta

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

ISTATISTIK_KANAL_ID = 123456789  # üye sayısı kanalı

# =========================
# YETKİLİ ROLLER
# =========================

YETKILI_ROLLER = [
1482030233056968827,
1482030334877896796
]

# =========================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

warnings = {}
join_tracker = []
spam_tracker = {}

# ticket sayaç dosyası
try:
    with open("ticket.json") as f:
        ticket_counter = json.load(f)
except:
    ticket_counter = 0

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

        button = Button(
            label="Doğrulan",
            emoji="✅",
            style=discord.ButtonStyle.green,
            custom_id="verify_button"
        )

        button.callback = self.verify
        self.add_item(button)

    async def verify(self, interaction: discord.Interaction):

        role = interaction.guild.get_role(VERIFY_ROLE_ID)
        await interaction.user.add_roles(role)

        await interaction.response.send_message(
            "✅ Doğrulandın!",
            ephemeral=True
        )

# =========================
# TICKET SİSTEMİ
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

            button = Button(label=label, custom_id=cid, style=style)
            button.callback = self.create_ticket
            self.add_item(button)

    async def create_ticket(self, interaction: discord.Interaction):

        global ticket_counter

        ticket_counter += 1

        with open("ticket.json","w") as f:
            json.dump(ticket_counter,f)

        kategori = interaction.guild.get_channel(TICKET_KATEGORI_ID)

        kanal = await interaction.guild.create_text_channel(
            name=f"ticket-{ticket_counter}",
            category=kategori
        )

        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_counter}",
            description=f"{interaction.user.mention} ticket açtı.",
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

class TicketKapat(View):

    def __init__(self):
        super().__init__(timeout=None)

        button = Button(
            label="🔒 Ticket Kapat",
            style=discord.ButtonStyle.red,
            custom_id="ticket_kapat"
        )

        button.callback = self.close_ticket
        self.add_item(button)

    async def close_ticket(self, interaction: discord.Interaction):

        if not is_yetkili(interaction.user):

            await interaction.response.send_message(
                "❌ Ticket sadece yetkililer kapatabilir.",
                ephemeral=True
            )
            return

        log = interaction.guild.get_channel(LOG_CHANNEL_ID)

        if log:
            embed = discord.Embed(
                title="🎫 Ticket Kapandı",
                description=f"{interaction.channel.name} kapatıldı\nYetkili: {interaction.user.mention}",
                color=0xe74c3c
            )
            await log.send(embed=embed)

        await interaction.response.send_message("🔒 Ticket kapatılıyor...")
        await interaction.channel.delete()

# =========================
# HOŞGELDİN
# =========================

@bot.event
async def on_member_join(member):

    role = member.guild.get_role(AUTO_ROLE_ID)

    if role:
        await member.add_roles(role)

    join_tracker.append(time.time())
    join_tracker[:] = [t for t in join_tracker if time.time()-t < 10]

    if len(join_tracker) >= 7:

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            await log.send("🚨 Anti raid aktif! Çok hızlı giriş algılandı.")

    kanal = bot.get_channel(ISTATISTIK_KANAL_ID)

    if kanal:
        await kanal.edit(name=f"👥 Üyeler: {member.guild.member_count}")

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

    user_id = message.author.id
    now = time.time()

    spam_tracker.setdefault(user_id, [])
    spam_tracker[user_id].append(now)

    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if now - t < 5]

    if len(spam_tracker[user_id]) >= 6:
        await message.delete()
        await ceza_ver(message.author,"Spam")
        return

    content = message.content.lower()

    if any(x in content for x in ["discord.gg","http://","https://",".gg/"]):
        await message.delete()
        await ceza_ver(message.author,"Reklam")
        return

    if any(x in content for x in ["amk","aq","orospu","salak"]):
        await message.delete()
        await ceza_ver(message.author,"Küfür")
        return

    await bot.process_commands(message)

# =========================
# KOMUTLAR
# =========================

@bot.tree.command(name="warnlar")
async def warnlar(interaction: discord.Interaction, user: discord.Member):

    warns = warnings.get(user.id, 0)

    await interaction.response.send_message(
        f"⚠️ {user.mention} toplam warn: **{warns}**"
    )

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Sebep belirtilmedi"):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    await user.ban(reason=reason)

    log = interaction.guild.get_channel(LOG_CHANNEL_ID)

    if log:
        embed = discord.Embed(
            title="🔨 Ban",
            description=f"{user.mention} banlandı\nYetkili: {interaction.user.mention}\nSebep: {reason}",
            color=0xe74c3c
        )
        await log.send(embed=embed)

    await interaction.response.send_message(
        f"{user.mention} banlandı."
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

    for guild in bot.guilds:
        await bot.tree.sync(guild=guild)

    print("Slash komutlar senkronize edildi.")

bot.run(TOKEN)
