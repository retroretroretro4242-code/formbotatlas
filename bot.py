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

ISTATISTIK_KANAL_ID = 123456789
GUILD_ID = 148202000000000000

IZINLI_ROLE = 1482032881265283244  # roldenban kullanabilen

# =========================
YETKILI_ROLLER = [
    1482030233056968827,
    1482030334877896796
]

# =========================
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

warnings = {}
join_tracker = []
spam_tracker = {}

# =========================
try:
    with open("ticket.json") as f:
        ticket_counter = json.load(f)
except:
    ticket_counter = 0

# =========================
def is_yetkili(member):
    return any(role.id in YETKILI_ROLLER for role in member.roles)

# =========================
async def ceza_ver(member, reason):
    log = member.guild.get_channel(LOG_CHANNEL_ID)

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
# VERIFY
class VerifyButton(View):
    def __init__(self):
        super().__init__(timeout=None)
        button = Button(label="Doğrulan", emoji="✅", style=discord.ButtonStyle.green)
        button.callback = self.verify
        self.add_item(button)

    async def verify(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(VERIFY_ROLE_ID)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ Doğrulandın!", ephemeral=True)

# =========================
# TICKET
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

# =========================
class TicketKapat(View):
    def __init__(self):
        super().__init__(timeout=None)
        button = Button(label="🔒 Ticket Kapat", style=discord.ButtonStyle.red)
        button.callback = self.close_ticket
        self.add_item(button)

    async def close_ticket(self, interaction: discord.Interaction):
        if not is_yetkili(interaction.user):
            await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
            return

        await interaction.channel.delete()

# =========================
# JOIN
@bot.event
async def on_member_join(member):
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        await member.add_roles(role)

# =========================
# MESAJ
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if is_yetkili(message.author):
        await bot.process_commands(message)
        return

    content = message.content.lower()

    if "http" in content or "discord.gg" in content:
        await message.delete()
        await ceza_ver(message.author,"Reklam")
        return

    await bot.process_commands(message)

# =========================
# KOMUTLAR

@bot.tree.command(name="warnlar", guild=discord.Object(id=GUILD_ID))
async def warnlar(interaction: discord.Interaction, user: discord.Member):
    warns = warnings.get(user.id, 0)
    await interaction.response.send_message(f"{user.mention} warn: {warns}")

@bot.tree.command(name="ban", guild=discord.Object(id=GUILD_ID))
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Sebep yok"):
    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok", ephemeral=True)
        return
    await user.ban(reason=reason)
    await interaction.response.send_message(f"{user.mention} banlandı")

# 🔥 TEMİZLE KOMUTU
@bot.tree.command(name="temizle", description="Mesaj siler", guild=discord.Object(id=GUILD_ID))
async def temizle(interaction: discord.Interaction, miktar: int):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=miktar)

    await interaction.followup.send(f"🧹 {len(deleted)} mesaj silindi", ephemeral=True)

# 🔥 ROLDEN BAN
@bot.tree.command(name="roldenban", guild=discord.Object(id=GUILD_ID))
async def roldenban(interaction: discord.Interaction):

    if not any(role.id == IZINLI_ROLE for role in interaction.user.roles):
        await interaction.response.send_message("❌ Kullanamazsın", ephemeral=True)
        return

    TARGET_ROLE_ID = 1482031063936139264
    role = interaction.guild.get_role(TARGET_ROLE_ID)

    members = role.members

    await interaction.response.send_message(f"{len(members)} kişi banlanacak. onay yaz", ephemeral=True)

    def check(m):
        return m.author == interaction.user and m.content.lower() == "onay"

    try:
        await bot.wait_for("message", timeout=15, check=check)
    except:
        return

    for m in members:
        try:
            await m.ban(reason="Toplu ban")
        except:
            pass

    await interaction.followup.send("✅ Bitti", ephemeral=True)

# =========================
@bot.event
async def on_ready():
    print(f"Bot hazır: {bot.user}")

    bot.add_view(VerifyButton())
    bot.add_view(TicketKategori())
    bot.add_view(TicketKapat())

    guild = bot.get_guild(GUILD_ID)
    if guild:
        await bot.tree.sync(guild=guild)

# =========================
bot.run(TOKEN)
