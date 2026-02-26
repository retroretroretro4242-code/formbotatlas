import discord
from discord.ext import commands
from discord import app_commands
import os

# Bot token'ı environment variable'dan alınıyor
TOKEN = os.getenv("TOKEN")  # Eğer environment variable kullanıyorsanız

# Eğer doğrudan token yazıyorsanız:
# TOKEN = "YOUR_DISCORD_BOT_TOKEN" 

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Yetkili rollerin ID'lerini belirliyoruz
YETKILI_ROLLER = [
    1384294618195169311,
    1474830960393453619,
    1474831019017371678,
    1474831132062122005,
    1474831132062122005
]

# ✅ Plugin Paylaşım Modal
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

# ✅ Pack Paylaşım Modal
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

# ✅ Sunucu Paylaşım Modal
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

# ✅ Discord Bot Paylaşım Modal
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

# ✅ Partner Başvuru Modal
class PartnerBasvuruModal(discord.ui.Modal, title="Partner Başvuru Formu"):
    partner_isim = discord.ui.TextInput(label="Partner İsmi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    sunucu_uyelik = discord.ui.TextInput(label="Sunucu Üyelik (Sayı)", placeholder="Örneğin: 1500")

    async def on_submit(self, interaction: discord.Interaction):
        # 'sunucu_uyelik' alanındaki değeri sayıya dönüştürmeden önce kontrol edelim
        try:
            sunucu_uyelik = int(self.sunucu_uyelik.value)  # Sayıya dönüştürme
        except ValueError:
            # Eğer kullanıcı geçerli bir sayı girmezse hata mesajı verelim
            await interaction.response.send_message("Sunucu üyelik sayısını geçerli bir sayı olarak girmeniz gerekiyor!", ephemeral=True)
            return

        # Başvuruyu embed olarak gönderme
        embed = discord.Embed(title="🤝 Partner Başvurusu", color=0x2ecc71)
        embed.add_field(name="Partner İsmi", value=self.partner_isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Sunucu Üyelik", value=str(sunucu_uyelik), inline=False)

        # Partner başvurusu bilgilerini partner-onay kanalına gönder
        channel = discord.utils.get(interaction.guild.text_channels, name="partner-onay")
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message(embed=embed)

# Yetki Kontrolü
def kullanici_yetkili():
    async def predicate(interaction: discord.Interaction):
        return any(role.id in YETKILI_ROLLER for role in interaction.user.roles)
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Bot hazır: {bot.user}")  # Botun adı ve ID'si
    await bot.tree.sync()  # Komutları senkronize et
    print("Komutlar senkronize edildi.")

# Slash Komutlar
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

@bot.tree.command(name="partnerbasvurusu")
async def partnerbasvurusu(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerBasvuruModal())

# Hata durumunda bilgiyi loglamak için
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Error occurred in event: {event}")
    print(f"Error details: {args}, {kwargs}")

# Botu çalıştırma
bot.run(TOKEN)
