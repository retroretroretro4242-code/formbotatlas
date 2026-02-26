import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")  # veya direkt token yaz

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

YETKILI_ROLLER = [
    1384294618195169311,
    1474830960393453619,
    1474831019017371678,
    1474831132062122005,
    1474831132062122005
]

# ✅ Partner Başvuru Modal
class PartnerBasvuruModal(discord.ui.Modal, title="Partner Başvuru Formu"):
    partner_isim = discord.ui.TextInput(label="Partner İsmi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Partner Başvurusu", color=0x9b59b6)
        embed.add_field(name="Partner İsmi", value=self.partner_isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)

        # Partner başvurusu onaylandığında, belirtilen kanala gönderilecektir.
        partner_channel = discord.utils.get(interaction.guild.text_channels, name="partner-onay")
        if partner_channel:
            await partner_channel.send(embed=embed)

        await interaction.response.send_message("Başvurunuz alındı, yetkililer tarafından değerlendirilecektir.", ephemeral=True)

# ✅ Partner Paylaşım Modal
class PartnerPaylasModal(discord.ui.Modal, title="Partner Paylaşım Formu"):
    isim = discord.ui.TextInput(label="Partner İsmi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Partner Paylaşımı", color=0x9b59b6)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        await interaction.response.send_message(embed=embed)

# ✅ İstek Modal
class IstekModal(discord.ui.Modal, title="İstek Formu"):
    istek = discord.ui.TextInput(label="İsteklerinizi buraya yazın", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"İstekleriniz alındı: {self.istek.value}", ephemeral=True)

# ✅ Slash komutlar
@bot.tree.command(name="pluginpaylas")
async def pluginpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(PluginModal())  # Plugin formu

@bot.tree.command(name="packpaylas")
async def packpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(PackModal())  # Pack formu

@bot.tree.command(name="sunucupaylas")
async def sunucupaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(SunucuModal())  # Sunucu formu

@bot.tree.command(name="botpaylas")
async def botpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(BotModal())  # Bot formu

# ✅ Yeni Slash Komutları
@bot.tree.command(name="partnerbasvurusu")
async def partnerbasvurusu(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerBasvuruModal())  # Partner başvuru formu

@bot.tree.command(name="partnerpaylas")
@commands.has_any_role(*YETKILI_ROLLER)  # Yalnızca yetkili roller için
async def partnerpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerPaylasModal())  # Partner paylaşım formunu gönder

@bot.tree.command(name="istek")
async def istek(interaction: discord.Interaction):
    await interaction.response.send_modal(IstekModal())  # İstek formu

# Bot hazır olduğunda konsola yazdırma
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot hazır: {bot.user}")

bot.run(TOKEN)
