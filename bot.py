import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime
from dotenv import load_dotenv

# =========================
# ENV LOAD
# =========================
load_dotenv()
TOKEN = os.getenv("TOKEN")

# =========================
# BOT INTENTS
# =========================
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# KANAL & ROL IDLERI
# =========================
WELCOME_CHANNEL_ID = 1479868699463913789
LOG_CHANNEL_ID = 1474827965643886864
PARTNER_BASVURU_KANAL_ID = 1476538995231162418
ONAY_KANAL_ID = 1475013100229890159
SUNUCU_ID = 1384288019426574367
YETKILI_ROLLER = [
    1384294618195169311,
    1474830960393453619,
    1474831019017371678,
    1474831132062122005,
    1474831344273068063,
    1474831393644220599
]

# =========================
# MODALS
# =========================
class PartnerBasvuruModal(Modal, title="Partner Başvuru Formu"):
    partner_isim = TextInput(label="Partner İsmi")
    aciklama = TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    sunucu_uyelik = TextInput(label="Sunucu Üyelik", placeholder="Örn: 1500")
    sunucu_link = TextInput(label="Sunucu Linki", placeholder="https://")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            uyelik = int(self.sunucu_uyelik.value)
        except ValueError:
            await interaction.response.send_message("Üyelik sayısını geçerli girin!", ephemeral=True)
            return
        embed = discord.Embed(title="🤝 Partner Başvurusu", color=0x2ecc71)
        embed.add_field(name="Partner İsmi", value=self.partner_isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Sunucu Üyelik", value=str(uyelik), inline=False)
        embed.add_field(name="Sunucu Linki", value=self.sunucu_link.value, inline=False)
        channel = bot.get_channel(PARTNER_BASVURU_KANAL_ID)
        if channel:
            view = View()
            view.add_item(Button(label="Onayla", style=discord.ButtonStyle.green, custom_id="onay"))
            view.add_item(Button(label="Reddet", style=discord.ButtonStyle.red, custom_id="red"))
            await channel.send(embed=embed, view=view)
        await interaction.response.send_message("Başvurunuz alındı.", ephemeral=True)

class PartnerPaylasModal(Modal, title="Partner Paylaşım Formu"):
    partner_isim = TextInput(label="Partner İsmi")
    aciklama = TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤝 Partner Paylaşımı", color=0x3498db)
        embed.add_field(name="Partner İsmi", value=self.partner_isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        await interaction.response.send_message(embed=embed)

class IstekModal(Modal, title="İstek Formu"):
    istek = TextInput(label="İstek", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📨 İstek", color=0xf1c40f)
        embed.add_field(name="İstek", value=self.istek.value, inline=False)
        await interaction.response.send_message(embed=embed)

class PluginModal(Modal, title="Plugin Paylaşım Formu"):
    isim = TextInput(label="Plugin İsmi", max_length=100)
    surum = TextInput(label="Sürüm", max_length=50)
    aciklama = TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    link = TextInput(label="İndirme Linki", placeholder="https://")
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔧 Plugin Paylaşımı", color=0x2ecc71)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Sürüm", value=self.surum.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Link", value=self.link.value, inline=False)
        await interaction.response.send_message(embed=embed)

class PackModal(Modal, title="Pack Paylaşım Formu"):
    isim = TextInput(label="Pack İsmi")
    surum = TextInput(label="Sürüm")
    link = TextInput(label="Link", placeholder="https://")
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📦 Pack Paylaşımı", color=0x3498db)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Sürüm", value=self.surum.value, inline=False)
        embed.add_field(name="Link", value=self.link.value, inline=False)
        await interaction.response.send_message(embed=embed)

class SunucuModal(Modal, title="Sunucu Tanıtım Formu"):
    isim = TextInput(label="Sunucu İsmi")
    ip = TextInput(label="IP Adresi")
    aciklama = TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🌐 Sunucu Tanıtımı", color=0xf1c40f)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="IP", value=self.ip.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        await interaction.response.send_message(embed=embed)

class BotModal(Modal, title="Discord Bot Paylaşımı"):
    isim = TextInput(label="Bot İsmi")
    ozellik = TextInput(label="Özellikler", style=discord.TextStyle.paragraph)
    link = TextInput(label="Davet / GitHub Linki", placeholder="https://")
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 Discord Bot Tanıtımı", color=0x9b59b6)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Özellikler", value=self.ozellik.value, inline=False)
        embed.add_field(name="Link", value=self.link.value, inline=False)
        await interaction.response.send_message(embed=embed)

# =========================
# Yetkili kontrol
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
# READY
# =========================
@bot.event
async def on_ready():
    print(f"{bot.user} aktif!")
    await bot.tree.sync()
    print("Komutlar senkronize edildi.")

# =========================
# MEMBER JOIN
# =========================
@bot.event
async def on_member_join(member: discord.Member):
    embed = discord.Embed(
        title=f"👋 Hoş geldin, {member.name}!",
        description="**PRX | Prime Raiders** ailesine katıldığın için mutluyuz.",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🌐 Takım Olanaklarımız",
                    value="• Profesyonel e-spor deneyimi\n• Düzenli turnuvalar\n• Özel Discord topluluğu\n• Takım koçluğu & rehberlik",
                    inline=False)
    embed.add_field(name="🚀 Başarılarımız", value="10+ yıl e-spor tecrübesi • 200+ turnuva • 3000+ aktif oyuncu", inline=False)
    embed.set_footer(text=f"{member.guild.name} • PRX | Prime Raiders")
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(content=f"🎉 {member.mention} aramıza katıldı!", embed=embed)
    try:
        await member.send(content=f"👋 {member.name}, {member.guild.name} sunucusuna hoş geldin!", embed=embed)
    except discord.Forbidden:
        print(f"{member} DM kapalı.")

# =========================
# SLASH COMMANDS
# =========================
@bot.tree.command(name="partnerbasvurusu", description="Partner başvurusu formu aç")
async def partnerbasvurusu(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerBasvuruModal())

@bot.tree.command(name="partnerpaylas")
@kullanici_yetkili()
@kanal_check(PARTNER_BASVURU_KANAL_ID)
async def partnerpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerPaylasModal())

@bot.tree.command(name="istek")
@kanal_check(PARTNER_BASVURU_KANAL_ID)
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
# RUN BOT
# =========================
bot.run(TOKEN)
