import discord
from discord.ext import commands
from discord import app_commands
import os

# Bot token'ını çevresel değişkenden alıyoruz
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

# ✅ Partner Başvuru Modal
class PartnerBasvuruModal(discord.ui.Modal, title="Partner Başvuru Formu"):
    partner_isim = discord.ui.TextInput(label="Partner İsmi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    sunucu_uyelik = discord.ui.TextInput(label="Sunucu Üyelik (Sayı)", placeholder="Örneğin: 1500")

    async def on_submit(self, interaction: discord.Interaction):
        # 'sunucu_uyelik' alanındaki değeri sayıya dönüştürmeden önce kontrol edelim
        try:
            # Kullanıcının girdiği değeri sayıya dönüştürmeye çalışıyoruz
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
        await interaction.response.send_message(embed=embed)

# ✅ Partner Paylaşım Modal
class PartnerPaylasModal(discord.ui.Modal, title="Partner Paylaşım Formu"):
    partner_isim = discord.ui.TextInput(label="Partner İsmi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤝 Partner Paylaşımı", color=0x3498db)
        embed.add_field(name="Partner İsmi", value=self.partner_isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        await interaction.response.send_message(embed=embed)

# ✅ İstek Modal
class IstekModal(discord.ui.Modal, title="İstek Formu"):
    istek = discord.ui.TextInput(label="İstek", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📨 İstek", color=0xf1c40f)
        embed.add_field(name="İstek", value=self.istek.value, inline=False)
        await interaction.response.send_message(embed=embed)

def kullanici_yetkili():
    async def predicate(interaction: discord.Interaction):
        return any(role.id in YETKILI_ROLLER for role in interaction.user.roles)
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Bot hazır: {bot.user}")  # Botun adı ve ID'si
    await bot.tree.sync()  # Komutları senkronize et
    print("Komutlar senkronize edildi.")

# ✅ Slash Komutlar
@bot.tree.command(name="partnerbasvurusu")
async def partnerbasvurusu(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerBasvuruModal())

@bot.tree.command(name="partnerpaylas")
@kullanici_yetkili()
async def partnerpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerPaylasModal())

@bot.tree.command(name="istek")
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

# Hata durumunda bilgiyi loglamak için
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Error occurred in event: {event}")
    print(f"Error details: {args}, {kwargs}")

# Botu çalıştırma
bot.run(TOKEN)
