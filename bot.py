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
    sunucu_ismi = discord.ui.TextInput(label="Sunucu İsmi")
    sunucu_uyelik = discord.ui.TextInput(label="Sunucu Üyelik Sayısı", placeholder="100'den fazla ise everyone zorunlu değil")

    async def on_submit(self, interaction: discord.Interaction):
        sunucu_uyelik = int(self.sunucu_uyelik.value)
        
        # 100'den azsa, everyone zorunlu
        if sunucu_uyelik < 100:
            await interaction.response.send_message(
                f"{interaction.user.mention} başvurunuz alındı. Sunucunuz 100'den az üyeye sahipse **everyone** rolü zorunludur.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} başvurunuz alındı, partnerlik başvurunuz değerlendirilecektir.",
                ephemeral=True
            )

# ✅ Partner Paylaşım Modal
class PartnerPaylasModal(discord.ui.Modal, title="Partner Paylaşım Formu"):
    isim = discord.ui.TextInput(label="Partner İsmi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Partner Paylaşımı", color=0x9b59b6)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        await interaction.response.send_message(embed=embed)

# ✅ Partner Başvurusu Komutu
@bot.tree.command(name="partnerbasvurusu")
async def partnerbasvurusu(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerBasvuruModal())

# ✅ Partner Paylaşım Komutu (Yalnızca kabul edilen partnerler için)
@bot.tree.command(name="partnerpaylas")
@commands.has_any_role(*YETKILI_ROLLER)  # Yalnızca yetkili roller için
async def partnerpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerPaylasModal())  # Partner paylaşım formunu gönder

# ✅ Kullanıcı Yetkili Kontrolü
def kullanici_yetkili():
    async def predicate(interaction: discord.Interaction):
        return any(role.id in YETKILI_ROLLER for role in interaction.user.roles)
    return app_commands.check(predicate)

# Bot hazır olduğunda konsola yazdırma
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot hazır: {bot.user}")

bot.run(TOKEN)
