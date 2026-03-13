import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from datetime import datetime
import os

TOKEN = os.getenv("TOKEN")

# =========================
# SUNUCU & KANAL & ROL ID
# =========================
SUNUCU_ID = 1482021160425357365
LOG_CHANNEL_ID = 1482028188639952933
WELCOME_CHANNEL_ID = 1482033833091010661
ONAY_KANAL_ID = 1482033954445066341
ISTEK_KANAL_ID = 1482034060678140015
PARTNER_KANAL_ID = 1482021582665678979
PARTNER_BASVURU_KANAL_ID = 1482021699020132486

TICKET_KATEGORI_ID = 1482030116036149319

YETKILI_ROLLER = [
    1482030116036149319,
    1482030233056968827,
    1482030334877896796,
]

# =========================
# BOT INTENTS
# =========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# REKLAM KORUMA
# =========================
REKLAM_KORUMA = True

# =========================
# MODALS
# =========================
class PartnerBasvuruModal(discord.ui.Modal, title="Partner Başvuru Formu"):
    partner_isim = discord.ui.TextInput(label="Partner İsmi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    sunucu_uyelik = discord.ui.TextInput(label="Sunucu Üyelik (Sayı)", placeholder="150")
    sunucu_link = discord.ui.TextInput(label="Sunucu Linki", placeholder="https://")

    async def on_submit(self, interaction: discord.Interaction):

        try:
            uyelik = int(self.sunucu_uyelik.value)
        except:
            await interaction.response.send_message("Üyelik sayısı geçerli sayı olmalı!", ephemeral=True)
            return

        if uyelik < 150:
            await interaction.response.send_message(
                "❌ Partner için minimum **150 üye** gerekli.",
                ephemeral=True
            )
            return

        embed = discord.Embed(title="🤝 Partner Başvurusu", color=0x2ecc71)

        embed.add_field(name="Partner İsmi", value=self.partner_isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Sunucu Üyelik", value=str(uyelik), inline=False)
        embed.add_field(name="Sunucu Linki", value=self.sunucu_link.value, inline=False)

        channel = bot.get_channel(PARTNER_BASVURU_KANAL_ID)

        if channel:

            view = discord.ui.View()

            onay = Button(label="Onayla", style=discord.ButtonStyle.green, custom_id="onay")
            red = Button(label="Reddet", style=discord.ButtonStyle.red, custom_id="red")

            view.add_item(onay)
            view.add_item(red)

            await channel.send(embed=embed, view=view)

        await interaction.response.send_message("Başvurunuz alındı!", ephemeral=True)

class PartnerPaylasModal(discord.ui.Modal, title="Partner Paylaşım Formu"):

    partner_isim = discord.ui.TextInput(label="Partner İsmi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):

        embed = discord.Embed(title="🤝 Partner Paylaşımı", color=0x3498db)

        embed.add_field(name="Partner İsmi", value=self.partner_isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)

        await interaction.response.send_message(embed=embed)

# =========================
# TICKET PANEL
# =========================
class TicketView(View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(label="Ekip Alım", style=discord.ButtonStyle.green, custom_id="ekip_alim"))
        self.add_item(Button(label="Yetkili Alım", style=discord.ButtonStyle.blurple, custom_id="yetkili_alim"))
        self.add_item(Button(label="Diğer", style=discord.ButtonStyle.gray, custom_id="diger"))

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 Ticket Paneli",
        description="Aşağıdaki butonlardan başvuru türünü seçebilirsiniz.",
        color=discord.Color.orange()
    )

    await interaction.response.send_message(embed=embed, view=TicketView())

# =========================
# WELCOME SİSTEMİ
# =========================
@bot.event
async def on_member_join(member):

    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    embed = discord.Embed(
        title=f"👋 Hoş geldin {member.name}!",
        color=0x2ecc71
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(
        name="Bilgi",
        value=f"{member.mention} Sunucuda **{member.guild.member_count}. üyemizsin.**",
        inline=False
    )

    if channel:
        await channel.send(embed=embed)

# =========================
# LEAVE LOG
# =========================
@bot.event
async def on_member_remove(member):

    channel = bot.get_channel(LOG_CHANNEL_ID)

    embed = discord.Embed(
        title="🚪 Sunucudan Ayrıldı",
        description=f"{member} sunucudan ayrıldı.",
        color=0xe74c3c
    )

    if channel:
        await channel.send(embed=embed)

# =========================
# REKLAM KORUMA
# =========================
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if REKLAM_KORUMA:

        reklam = ["discord.gg", "discord.com/invite", "http://", "https://"]

        if any(x in message.content.lower() for x in reklam):

            if not any(role.id in YETKILI_ROLLER for role in message.author.roles):

                try:
                    await message.delete()

                    embed = discord.Embed(
                        title="🚫 Reklam Engellendi",
                        description=f"{message.author.mention} reklam göndermeye çalıştı.",
                        color=0xe74c3c
                    )

                    log = bot.get_channel(LOG_CHANNEL_ID)

                    if log:
                        await log.send(embed=embed)

                except:
                    pass

    await bot.process_commands(message)

# =========================
# BUTTON HANDLER
# =========================
@bot.event
async def on_interaction(interaction: discord.Interaction):

    if interaction.type != discord.InteractionType.component:
        return

    cid = interaction.data["custom_id"]

    if cid in ["ekip_alim", "yetkili_alim", "diger"]:

        kategori = bot.get_channel(TICKET_KATEGORI_ID)

        kanal = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=kategori
        )

        embed = discord.Embed(
            title="🎫 Ticket Oluşturuldu",
            description=f"{interaction.user.mention} yetkililer yakında sizinle ilgilenecek.",
            color=0xf1c40f
        )

        await kanal.send(interaction.user.mention, embed=embed)

        await interaction.response.send_message(
            f"Ticket oluşturuldu: {kanal.mention}",
            ephemeral=True
        )

    if cid == "onay":

        fields = interaction.message.embeds[0].fields

        embed = discord.Embed(
            title="🤝 Yeni Partner",
            color=0x2ecc71
        )

        embed.add_field(name="Partner İsmi", value=fields[0].value, inline=False)
        embed.add_field(name="Açıklama", value=fields[1].value, inline=False)
        embed.add_field(name="Sunucu Üyelik", value=fields[2].value, inline=False)
        embed.add_field(name="Sunucu Linki", value=fields[3].value, inline=False)

        kanal = bot.get_channel(PARTNER_KANAL_ID)

        if kanal:
            await kanal.send(embed=embed)

        await interaction.response.send_message("Başvuru onaylandı!", ephemeral=True)

    if cid == "red":
        await interaction.response.send_message("Başvuru reddedildi.", ephemeral=True)

# =========================
# READY
# =========================
@bot.event
async def on_ready():

    print(f"Bot hazır: {bot.user}")

    await bot.tree.sync()

    print("Komutlar senkronize edildi.")

# =========================
# RUN
# =========================
bot.run(TOKEN)
