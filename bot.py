import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")  # Eğer environment variable kullanıyorsanız
# Eğer doğrudan token yazıyorsanız:
# TOKEN = "YOUR_DISCORD_BOT_TOKEN"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Kanal ID'leri
ISTEK_KANAL_ID = 1475095722864017478
PARTNER_KANAL_ID = 1476535145963192360
PARTNER_BASVURU_KANAL_ID = 1476538995231162418
ONAY_KANAL_ID = 1475013100229890159

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
    sunucu_link = discord.ui.TextInput(label="Sunucu Linki", placeholder="https://")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            sunucu_uyelik = int(self.sunucu_uyelik.value)  # Sayıya dönüştürme
        except ValueError:
            await interaction.response.send_message("Sunucu üyelik sayısını geçerli bir sayı olarak girmeniz gerekiyor!", ephemeral=True)
            return

        # Başvuru embed olarak partner başvuru kanalına gönderilecek
        embed = discord.Embed(title="🤝 Partner Başvurusu", color=0x2ecc71)
        embed.add_field(name="Partner İsmi", value=self.partner_isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Sunucu Üyelik", value=str(sunucu_uyelik), inline=False)
        embed.add_field(name="Sunucu Linki", value=self.sunucu_link.value, inline=False)

        # Başvuru bilgilerini partner-onay kanalına gönder
        channel = bot.get_channel(PARTNER_BASVURU_KANAL_ID)
        if channel:
            # Onay ve Red butonları ekleniyor
            view = discord.ui.View()
            onay_button = discord.ui.Button(label="Onayla", style=discord.ButtonStyle.green, custom_id="onay")
            red_button = discord.ui.Button(label="Reddet", style=discord.ButtonStyle.red, custom_id="red")

            view.add_item(onay_button)
            view.add_item(red_button)

            await channel.send(embed=embed, view=view)

        await interaction.response.send_message("Başvurunuz alındı ve onay için yetkililere iletildi.", ephemeral=True)

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

# Yetkili kontrolü
def kullanici_yetkili():
    async def predicate(interaction: discord.Interaction):
        return any(role.id in YETKILI_ROLLER for role in interaction.user.roles)
    return app_commands.check(predicate)

# Kanal kontrolü (istek ve partner komutları için)
def kanal_check(kanal_id):
    async def predicate(interaction: discord.Interaction):
        return interaction.channel.id == kanal_id
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Bot hazır: {bot.user}")
    await bot.tree.sync()  # Komutları senkronize et
    print("Komutlar senkronize edildi.")

# Onay ve Red butonlarının işleyişi
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data["custom_id"] == "onay":
            # Onaylandığında partner başvurusu bilgilerini ONAY_KANAL_ID kanalına gönder
            embed = discord.Embed(title="✅ Partner Başvurusu Onaylandı", color=0x2ecc71)
            embed.add_field(name="Partner İsmi", value=interaction.message.embeds[0].fields[0].value, inline=False)
            embed.add_field(name="Açıklama", value=interaction.message.embeds[0].fields[1].value, inline=False)
            embed.add_field(name="Sunucu Üyelik", value=interaction.message.embeds[0].fields[2].value, inline=False)
            embed.add_field(name="Sunucu Linki", value=interaction.message.embeds[0].fields[3].value, inline=False)
            channel = bot.get_channel(ONAY_KANAL_ID)
            if channel:
                await channel.send(embed=embed)
            await interaction.response.send_message("Başvuru onaylandı ve ilgili kanala gönderildi.", ephemeral=True)

        elif interaction.data["custom_id"] == "red":
            # Red edildiğinde kullanıcıya reddedildi mesajı gönder
            await interaction.response.send_message("Başvuru reddedildi.", ephemeral=True)

# ✅ Slash Komutlar
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

bot.run(TOKEN)
