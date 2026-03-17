import discord
from discord import app_commands
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True  # Üyelere erişim için gerekli

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("TOKEN")

class MyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban_role", description="Belirli bir role sahip tüm üyeleri banlar")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_role(self, interaction: discord.Interaction, role: discord.Role):
        members_banned = 0
        for member in interaction.guild.members:
            if role in member.roles:
                try:
                    await member.ban(reason=f"Banlandı: {role.name} rolü nedeniyle")
                    members_banned += 1
                except:
                    await interaction.response.send_message(f"{member} banlanamadı!", ephemeral=True)
        await interaction.response.send_message(f"{members_banned} üye banlandı!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot hazır! {bot.user}")
    await bot.tree.sync()  # Slash komutlarını sunucuya kaydet

bot.add_cog(MyBot(bot))
bot.run(TOKEN)
