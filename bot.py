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

VERIFY_ROLE_ID = 1482021882378059876
AUTO_ROLE_ID = 1482031140897292563

TICKET_KATEGORI_ID = 1482030116036149319
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
        text = "1. uyarı → 5 dk timeout"
    elif level == 2:
        duration = timedelta(minutes=10)
        text = "2. uyarı → 10 dk timeout"
    else:
        duration = timedelta(days=1)
        text = "3. uyarı → 1 gün mute"

    try:
        await member.timeout(duration, reason=reason)
    except:
        pass

    if log:
        embed = discord.Embed(
            title="⚠️ Ceza Sistemi",
            description=f"{member.mention}\n{text}\nSebep: {reason}",
            color=0xe67e22
        )
        await log.send(embed=embed)

# =========================
# VERIFY
class VerifyButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Doğrulan", style=discord.ButtonStyle.green, emoji="✅", custom_id="verify")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(VERIFY_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ Doğrulandın!", ephemeral=True)

# =========================
# TICKET
class TicketKategori(View):
    def __init__(self):
        super().__init__(timeout=None)

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

    @discord.ui.button(label="💰 Sipariş", style=discord.ButtonStyle.green)
    async def siparis(self, interaction, button):
        await self.create_ticket(interaction)

    @discord.ui.button(label="🛠 Destek", style=discord.ButtonStyle.blurple)
    async def destek(self, interaction, button):
        await self.create_ticket(interaction)

    @discord.ui.button(label="📦 Proje", style=discord.ButtonStyle.gray)
    async def proje(self, interaction, button):
        await self.create_ticket(interaction)

    @discord.ui.button(label="🎁 Ücretsiz", style=discord.ButtonStyle.success)
    async def ucretsiz(self, interaction, button):
        await self.create_ticket(interaction)

    @discord.ui.button(label="❓ Diğer", style=discord.ButtonStyle.red)
    async def diger(self, interaction, button):
        await self.create_ticket(interaction)

# =========================
class TicketKapat(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Ticket Kapat", style=discord.ButtonStyle.red)
    async def close(self, interaction, button):
        if not is_yetkili(interaction.user):
            await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
            return

        log = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log:
            await log.send(f"🎫 {interaction.channel.name} kapatıldı ({interaction.user})")

        await interaction.response.send_message("Kapatılıyor...")
        await interaction.channel.delete()

# =========================
# JOIN
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
            await log.send("🚨 Anti raid aktif!")

    kanal = bot.get_channel(ISTATISTIK_KANAL_ID)
    if kanal:
        await kanal.edit(name=f"👥 Üyeler: {member.guild.member_count}")

# =========================
# MESAJ KORUMA
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
        await ceza_ver(message.author, "Spam")
        return

    content = message.content.lower()

    if any(x in content for x in ["discord.gg", "http://", "https://"]):
        await message.delete()
        await ceza_ver(message.author, "Reklam")
        return

    if any(x in content for x in ["amk", "aq", "salak"]):
        await message.delete()
        await ceza_ver(message.author, "Küfür")
        return

    await bot.process_commands(message)

# =========================
# KOMUTLAR
@bot.tree.command(name="warnlar")
async def warnlar(interaction: discord.Interaction, user: discord.Member):
    warns = warnings.get(user.id, 0)
    await interaction.response.send_message(
        f"⚠️ {user.mention} warn: {warns}"
    )

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Sebep yok"):
    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok", ephemeral=True)
        return

    await user.ban(reason=reason)

    log = interaction.guild.get_channel(LOG_CHANNEL_ID)
    if log:
        await log.send(f"🔨 {user} banlandı | Yetkili: {interaction.user} | Sebep: {reason}")

    await interaction.response.send_message(f"{user.mention} banlandı")

# =========================
@bot.event
async def setup_hook():
    await bot.tree.sync()
    print("Slash komutlar yüklendi")

# =========================
@bot.event
async def on_ready():
    print(f"Bot aktif: {bot.user}")

    bot.add_view(VerifyButton())
    bot.add_view(TicketKategori())
    bot.add_view(TicketKapat())

# =========================
bot.run(TOKEN)
