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

# =========================
YETKILI_ROLLER = [
    1482030233056968827,
    1482030334877896796
]

# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

warnings = {}
join_tracker = []
spam_tracker = []

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
    guild = member.guild
    log = guild.get_channel(LOG_CHANNEL_ID)

    warnings.setdefault(member.id, 0)
    warnings[member.id] += 1
    level = warnings[member.id]

    if level == 1:
        duration = timedelta(minutes=5)
        text = "1. Uyarı → 5 dk timeout"
    elif level == 2:
        duration = timedelta(minutes=10)
        text = "2. Uyarı → 10 dk timeout"
    else:
        duration = timedelta(days=1)
        text = "3. Uyarı → 1 gün mute"

    try:
        await member.timeout(duration, reason=reason)
    except:
        pass

    if log:
        embed = discord.Embed(
            title="⚠️ Ceza",
            description=f"{member.mention}\n{text}\nSebep: {reason}",
            color=0xe67e22
        )
        await log.send(embed=embed)

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

    @discord.ui.button(label="Doğrulan", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(VERIFY_ROLE_ID)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ Doğrulandın!", ephemeral=True)

# =========================
class TicketKategori(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💰 Sipariş", style=discord.ButtonStyle.green, custom_id="ticket_siparis")
    async def siparis(self, interaction, button):
        await self.create_ticket(interaction)

    @discord.ui.button(label="🛠 Destek", style=discord.ButtonStyle.blurple, custom_id="ticket_destek")
    async def destek(self, interaction, button):
        await self.create_ticket(interaction)

    async def create_ticket(self, interaction):
        global ticket_counter
        ticket_counter += 1

        with open("ticket.json", "w") as f:
            json.dump(ticket_counter, f)

        kategori = interaction.guild.get_channel(TICKET_KATEGORI_ID)

        kanal = await interaction.guild.create_text_channel(
            name=f"ticket-{ticket_counter}",
            category=kategori
        )

        await kanal.send(
            f"{interaction.user.mention}",
            view=TicketKapat()
        )

        await interaction.response.send_message(
            f"Ticket açıldı: {kanal.mention}",
            ephemeral=True
        )

# =========================
class TicketKapat(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Kapat", style=discord.ButtonStyle.red, custom_id="ticket_kapat")
    async def close(self, interaction, button):
        if not is_yetkili(interaction.user):
            await interaction.response.send_message("❌ Yetkin yok", ephemeral=True)
            return

        await interaction.channel.delete()

# =========================
@bot.event
async def on_member_join(member):
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        await member.add_roles(role)

# =========================
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
        await ceza_ver(message.author, "Reklam")
        return

    await bot.process_commands(message)

# =========================
@bot.tree.command(name="warnlar")
async def warnlar(interaction: discord.Interaction, user: discord.Member):
    warns = warnings.get(user.id, 0)
    await interaction.response.send_message(f"{user.mention} warn: {warns}")

# =========================
@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Sebep yok"):
    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok", ephemeral=True)
        return

    await user.ban(reason=reason)
    await interaction.response.send_message(f"{user.mention} banlandı")

# =========================
@bot.event
async def setup_hook():
    await bot.tree.sync()
    print("Slash komutlar global sync edildi")

# =========================
@bot.event
async def on_ready():
    print(f"Bot aktif: {bot.user}")
    bot.add_view(VerifyButton())
    bot.add_view(TicketKategori())
    bot.add_view(TicketKapat())

# =========================
bot.run(TOKEN)
