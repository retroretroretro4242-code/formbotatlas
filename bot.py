import discord
from discord.ext import commands
from discord import app_commands
import random
import os

TOKEN = os.getenv("TOKEN")  # veya direkt token yaz

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

YETKILI_ROLLER = [
    1474568875634065428,
    1425485552504799341,
    1425962500351856693,
    1472172964198744210,
    1425485552504799342
]

# ✅ Plugin Modal
class PluginModal(discord.ui.Modal, title="Plugin Paylaşım Formu"):
    isim = discord.ui.TextInput(label="Plugin İsmi", max_length=100)
    surum = discord.ui.TextInput(label="Sürüm", max_length=50)
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    link = discord.ui.TextInput(label="İndirme Linki", placeholder="https://")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔧 Plugin Paylaşımı", color=0x2ecc71)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Sürüm", value=self.surum.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Link", value=self.link.value, inline=False)
        await interaction.response.send_message(embed=embed)

# ✅ Pack Modal
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

# ✅ Sunucu Modal
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

# ✅ Discord Bot Modal
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

def kullanici_yetkili():
    async def predicate(interaction: discord.Interaction):
        return any(role.id in YETKILI_ROLLER for role in interaction.user.roles)
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot hazır: {bot.user}")

# ✅ Slash komutlar
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

bot.run(TOKEN)
