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
SUNUCU_ID = 1384288019426574367
LOG_CHANNEL_ID = 1474827965643886864
WELCOME_CHANNEL_ID = 1479868699463913789
ONAY_KANAL_ID = 1475013100229890159
ISTEK_KANAL_ID = 1475095722864017478
PARTNER_KANAL_ID = 1476535145963192360
PARTNER_BASVURU_KANAL_ID = 1476538995231162418

YETKILI_ROLLER = [
    1474831393644220599,
    1384294618195169311,
    1474830960393453619,
    1474831019017371678,
    1474831132062122005,
    1474831344273068063
]

# =========================
# BOT INTENTS
# =========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# MODALS
# =========================
class PartnerBasvuruModal(discord.ui.Modal, title="Partner Başvuru Formu"):
    partner_isim = discord.ui.TextInput(label="Partner İsmi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    sunucu_uyelik = discord.ui.TextInput(label="Sunucu Üyelik (Sayı)", placeholder="Örneğin: 1500")
    sunucu_link = discord.ui.TextInput(label="Sunucu Linki", placeholder="https://")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            uyelik = int(self.sunucu_uyelik.value)
        except:
            await interaction.response.send_message("Üyelik sayısı geçerli sayı olmalı!", ephemeral=True)
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

class IstekModal(discord.ui.Modal, title="İstek Formu"):
    istek = discord.ui.TextInput(label="İstek", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📨 İstek", color=0xf1c40f)
        embed.add_field(name="İstek", value=self.istek.value, inline=False)
        await interaction.response.send_message(embed=embed)

class PluginModal(discord.ui.Modal, title="Plugin Paylaşım Formu"):
    isim = discord.ui.TextInput(label="Plugin İsmi")
    surum = discord.ui.TextInput(label="Sürüm")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    link = discord.ui.TextInput(label="Link", placeholder="https://")
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔧 Plugin Paylaşımı", color=0x2ecc71)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Sürüm", value=self.surum.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Link", value=self.link.value, inline=False)
        await interaction.response.send_message(embed=embed)

class PackModal(discord.ui.Modal, title="Pack Paylaşım Formu"):
    isim = discord.ui.TextInput(label="Pack İsmi")
    surum = discord.ui.TextInput(label="Sürüm")
    link = discord.ui.TextInput(label="Link", placeholder="https://")
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📦 Pack Paylaşımı", color=0x3498db)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Sürüm", value=self.surum.value, inline=False)
        embed.add_field(name="Link", value=self.link.value, inline=False)
        await interaction.response.send_message(embed=embed)

class SunucuModal(discord.ui.Modal, title="Sunucu Tanıtım Formu"):
    isim = discord.ui.TextInput(label="Sunucu İsmi")
    ip = discord.ui.TextInput(label="IP Adresi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🌐 Sunucu Tanıtımı", color=0xf1c40f)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="IP", value=self.ip.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        await interaction.response.send_message(embed=embed)

class BotModal(discord.ui.Modal, title="Discord Bot Paylaşımı"):
    isim = discord.ui.TextInput(label="Bot İsmi")
    ozellik = discord.ui.TextInput(label="Özellikler", style=discord.TextStyle.paragraph)
    link = discord.ui.TextInput(label="Davet / GitHub Linki", placeholder="https://")
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 Discord Bot Tanıtımı", color=0x9b59b6)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Özellikler", value=self.ozellik.value, inline=False)
        embed.add_field(name="Link", value=self.link.value, inline=False)
        await interaction.response.send_message(embed=embed)

# =========================
# Yetkili & Kanal Kontrolleri
# =========================
def kullanici_yetkili():
    async def predicate(interaction: discord.Interaction):
        return any(role.id in YETKILI_ROLLER for role in interaction.user.roles)
    return app_commands.check(predicate)

def kanal_check(kanal_id):
    async def predicate(interaction: discord.Interaction):
        return interaction.channel.id == kanal_id
    return app_commands.check(predicate)

# =========================
# HOŞGELDİN MESAJI
# =========================
@bot.event
async def on_member_join(member: discord.Member):
    embed = discord.Embed(
        title=f"👋 Hoş geldin, {member.name}!",
        description="**PRX | Prime Raiders** ailesine katıldığın için mutluyuz!",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(
        name="🌐 Takım Olanaklarımız",
        value="• Profesyonel e-spor deneyimi\n• Düzenli turnuvalar\n• Özel Discord topluluğu",
        inline=False
    )
    embed.set_footer(text=f"{member.guild.name} • PRX | Prime Raiders")
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(content=f"🎉 {member.mention} aramıza katıldı!", embed=embed)
    try:
        await member.send(content=f"👋 {member.name}, {member.guild.name} sunucusuna hoş geldin!", embed=embed)
    except:
        pass

# =========================
# Partner Başvuru Onay / Red
# =========================
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return
    cid = interaction.data["custom_id"]
    if cid == "onay":
        embed = discord.Embed(title="✅ Partner Başvurusu Onaylandı", color=0x2ecc71)
        fields = interaction.message.embeds[0].fields
        embed.add_field(name="Partner İsmi", value=fields[0].value, inline=False)
        embed.add_field(name="Açıklama", value=fields[1].value, inline=False)
        embed.add_field(name="Sunucu Üyelik", value=fields[2].value, inline=False)
        embed.add_field(name="Sunucu Linki", value=fields[3].value, inline=False)
        channel = bot.get_channel(ONAY_KANAL_ID)
        if channel:
            await channel.send(embed=embed)
        await interaction.response.send_message("Başvuru onaylandı!", ephemeral=True)
    elif cid == "red":
        await interaction.response.send_message("Başvuru reddedildi.", ephemeral=True)

# =========================
# SLASH KOMUTLAR
# =========================
@bot.tree.command(name="partnerbasvurusu")
async def partnerbasvurusu(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerBasvuruModal())

@bot.tree.command(name="partnerpaylas")
@kullanici_yetkili()
@kanal_check(PARTNER_KANAL_ID)
async def partnerpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerPaylasModal())

@bot.tree.command(name="istek")
@kanal_check(ISTEK_KANAL_ID)
async def istek(interaction: discord.Interaction):
    await interaction.response.send_modal(IstekModal())

@bot.tree.command(name="pluginpaylas")
@kullanici_yetkili()
async def pluginpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(PluginModal())

@bot.tree.command(name="packpaylas")
@kullanici_yetkili()
async def packpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(PackModal())

@bot.tree.command(name="sunucupaylas")
@kullanici_yetkili()
async def sunucupaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(SunucuModal())

@bot.tree.command(name="botpaylas")
@kullanici_yetkili()
async def botpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(BotModal())

# =========================
# Ticket Panel
# =========================
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Ekip Alım", style=discord.ButtonStyle.green, custom_id="ekip_alim"))
        self.add_item(Button(label="Yetkili Alım", style=discord.ButtonStyle.blurple, custom_id="yetkili_alim"))
        self.add_item(Button(label="Diğer", style=discord.ButtonStyle.gray, custom_id="diger"))

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 Ticket Paneli", description="Aşağıdaki butonlardan başvuru türünü seçebilirsiniz.", color=discord.Color.orange())
    await interaction.response.send_message(embed=embed, view=TicketView())

# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    print(f"Bot hazır: {bot.user}")
    await bot.tree.sync()
    print("Komutlar senkronize edildi.")

# =========================
# RUN BOT
# =========================
bot.run(TOKEN)
