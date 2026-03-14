import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import time
from datetime import timedelta

TOKEN = os.getenv("TOKEN")

# =========================
# ID AYARLARI
# =========================

WELCOME_CHANNEL_ID = 1482033833091010661
LOG_CHANNEL_ID = 1482028188639952933

VERIFY_CHANNEL_ID = 1482031063936139264
VERIFY_ROLE_ID = 1482021882378059876

AUTO_ROLE_ID = 1482031140897292563

TICKET_KATEGORI_ID = 1482030116036149319

VOICE_CHANNEL_ID = 1482421665890570290

# =========================
# YETKİLİ ROLLER
# =========================

YETKILI_ROLLER = [
1482030116036149319,
1482030233056968827,
1482030334877896796
]

# =========================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

warnings = {}
join_tracker = []
ticket_counter = 0

# =========================
# YETKİLİ KONTROL
# =========================

def is_yetkili(member):
    return any(role.id in YETKILI_ROLLER for role in member.roles)

# =========================
# CEZA SİSTEMİ
# =========================

async def ceza_ver(member, reason):

    guild = member.guild
    log = guild.get_channel(LOG_CHANNEL_ID)

    warnings.setdefault(member.id, 0)
    warnings[member.id] += 1

    level = warnings[member.id]

    if level == 1:
        duration = timedelta(minutes=5)
        text = "1. Uyarı → 5 dakika timeout"

    elif level == 2:
        duration = timedelta(minutes=10)
        text = "2. Uyarı → 10 dakika timeout"

    else:
        duration = timedelta(days=1)
        text = "3. Uyarı → 1 gün mute"

    try:
        await member.timeout(duration, reason=reason)
    except:
        pass

    if log:
        embed = discord.Embed(
            title="⚠️ Otomatik Ceza",
            description=f"{member.mention}\n{text}\nSebep: {reason}",
            color=0xe67e22
        )
        await log.send(embed=embed)

# =========================
# VERIFY BUTTON
# =========================

class VerifyButton(View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(
            label="Doğrulan",
            emoji="✅",
            style=discord.ButtonStyle.green,
            custom_id="verify_button"
        ))

# =========================
# TICKET SİSTEMİ
# =========================

class TicketKategori(View):

    def __init__(self):
        super().__init__(timeout=None)

        buttons = [
            ("💰 Sipariş","ticket_siparis",discord.ButtonStyle.green),
            ("🛠 Destek","ticket_destek",discord.ButtonStyle.blurple),
            ("📦 Proje","ticket_proje",discord.ButtonStyle.gray),
            ("🎁 Ücretsiz","ticket_ucretsiz",discord.ButtonStyle.success),
            ("❓ Diğer","ticket_diger",discord.ButtonStyle.red)
        ]

        for label,cid,style in buttons:
            self.add_item(Button(label=label,custom_id=cid,style=style))


class TicketKapat(View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(
            label="🔒 Ticket Kapat",
            style=discord.ButtonStyle.red,
            custom_id="ticket_kapat"
        ))

# =========================
# HOŞGELDİN
# =========================

@bot.event
async def on_member_join(member):

    role = member.guild.get_role(AUTO_ROLE_ID)

    if role:
        await member.add_roles(role)

    try:

        embed = discord.Embed(
            title=f"👋 Hoş geldin, {member.name}!",
            description="**Project Nova** ailesine katıldığın için mutluyuz.",
            color=0x5865F2
        )

        embed.add_field(
            name="🚀 Hizmetlerimiz",
            value=(
                "🎮 FiveM & Minecraft yazılım çözümleri\n"
                "🌐 Web sitesi tasarım ve geliştirme\n"
                "🤖 Özel Discord bot geliştirme\n"
                "🏆 8+ yıl tecrübe · 150+ sunucu · 2000+ sipariş"
            ),
            inline=False
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await member.send(embed=embed)

    except:
        pass

    # ANTIRAID

    join_tracker.append(time.time())
    join_tracker[:] = [t for t in join_tracker if time.time()-t < 10]

    if len(join_tracker) >= 5:

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            await log.send("🚨 **ANTI RAID UYARISI! Çok hızlı giriş algılandı.**")

# =========================
# MESAJ KORUMA
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if is_yetkili(message.author):
        await bot.process_commands(message)
        return

    content = message.content.lower()

    if any(x in content for x in ["discord.gg","http://","https://",".gg/"]):
        await message.delete()
        await ceza_ver(message.author,"Reklam")
        return

    if any(x in content for x in ["amk","aq","orospu","salak"]):
        await message.delete()
        await ceza_ver(message.author,"Küfür")
        return

    if len(message.content) > 8:

        upper = sum(1 for c in message.content if c.isupper())

        if upper / len(message.content) > 0.7:

            await message.delete()
            await ceza_ver(message.author,"Caps spam")
            return

    await bot.process_commands(message)

# =========================
# BUTTON EVENT
# =========================

@bot.event
async def on_interaction(interaction):

    global ticket_counter

    if interaction.type != discord.InteractionType.component:
        return

    cid = interaction.data["custom_id"]

    # VERIFY

    if cid == "verify_button":

        role = interaction.guild.get_role(VERIFY_ROLE_ID)

        await interaction.user.add_roles(role)

        await interaction.response.send_message(
            "✅ Doğrulandın!",
            ephemeral=True
        )

        try:

            embed = discord.Embed(
                title=f"👋 Hoş geldin, {interaction.user.name}!",
                description="**Project Nova** ailesine katıldığın için mutluyuz.",
                color=0x5865F2
            )

            embed.add_field(
                name="🚀 Hizmetlerimiz",
                value=(
                    "🎮 FiveM & Minecraft yazılım çözümleri\n"
                    "🌐 Web sitesi tasarım ve geliştirme\n"
                    "🤖 Özel Discord bot geliştirme\n"
                    "🏆 8+ yıl tecrübe · 150+ sunucu · 2000+ sipariş"
                ),
                inline=False
            )

            embed.set_thumbnail(url=interaction.user.display_avatar.url)

            await interaction.user.send(embed=embed)

        except:
            pass

        return

    # TICKET AÇ

    if cid.startswith("ticket_") and cid != "ticket_kapat":

        ticket_counter += 1

        kategori = bot.get_channel(TICKET_KATEGORI_ID)

        kanal = await interaction.guild.create_text_channel(
            name=f"ticket-{ticket_counter}",
            category=kategori
        )

        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_counter}",
            description=(
                f"{interaction.user.mention} ticket açtı.\n\n"
                "📌 Lütfen aşağıdaki bilgileri yaz:\n"
                "• Ne istiyorsunuz?\n"
                "• Proje detayları\n"
                "• Varsa görseller"
            ),
            color=0x2ecc71
        )

        await kanal.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketKapat()
        )

        await interaction.response.send_message(
            f"Ticket oluşturuldu: {kanal.mention}",
            ephemeral=True
        )

        return

    # TICKET KAPAT

    if cid == "ticket_kapat":

        if not is_yetkili(interaction.user):

            await interaction.response.send_message(
                "❌ Ticket sadece yetkililer kapatabilir.",
                ephemeral=True
            )
            return

        await interaction.response.send_message("🔒 Ticket kapatılıyor...")

        await interaction.channel.delete()

# =========================
# KOMUTLAR
# =========================

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction):

    embed = discord.Embed(
        title="🎫 Destek Merkezi",
        description=(
            "**Destek Merkezi Hakkında.**\n"
            "Aşağıdaki seçeneklerden uygun olanı seçerek hemen bir ticket oluşturabilirsiniz.\n\n"
            "❤️ Sunucu Bilgisi.\n"
            "Gereksiz ticket açmayın, Sunucu Kurallarını Okumayı Unutmayın."
        ),
        color=0x5865F2
    )

    embed.set_thumbnail(url=interaction.guild.icon.url)

    await interaction.response.send_message(
        embed=embed,
        view=TicketKategori()
    )

@bot.tree.command(name="onay-mesaji")
async def verify(interaction):

    ch = bot.get_channel(VERIFY_CHANNEL_ID)

    embed = discord.Embed(
        title="🔐 Sunucu Doğrulama",
        description="Butona basarak doğrulan.",
        color=0x2ecc71
    )

    await ch.send(embed=embed,view=VerifyButton())

    await interaction.response.send_message(
        "Verify panel gönderildi.",
        ephemeral=True
    )

@bot.event
async def on_ready():

    print(f"Bot hazır: {bot.user}")

    bot.add_view(VerifyButton())
    bot.add_view(TicketKategori())
    bot.add_view(TicketKapat())

    for guild in bot.guilds:
        try:
            await bot.tree.sync(guild=guild)
            print(f"Komutlar senkronize edildi: {guild.name}")
        except Exception as e:
            print(e)

    channel = bot.get_channel(VOICE_CHANNEL_ID)

    if channel:
        vc = discord.utils.get(bot.voice_clients, guild=channel.guild)

        if not vc:
            await channel.connect()
# =========================
# MODERASYON KOMUTLARI
# =========================

@bot.tree.command(name="sil", description="Mesaj sil")
async def sil(interaction: discord.Interaction, miktar: int):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    await interaction.channel.purge(limit=miktar)

    await interaction.followup.send(f"🗑 {miktar} mesaj silindi.")


@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Sebep belirtilmedi"):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    await user.ban(reason=reason)

    await interaction.response.send_message(
        f"🔨 {user.mention} banlandı.\nSebep: {reason}"
    )


@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Sebep belirtilmedi"):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    await user.kick(reason=reason)

    await interaction.response.send_message(
        f"👢 {user.mention} atıldı.\nSebep: {reason}"
    )


@bot.tree.command(name="mute")
async def mute(interaction: discord.Interaction, user: discord.Member, dakika: int):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    duration = timedelta(minutes=dakika)

    await user.timeout(duration)

    await interaction.response.send_message(
        f"🔇 {user.mention} {dakika} dakika susturuldu."
    )


@bot.tree.command(name="unmute")
async def unmute(interaction: discord.Interaction, user: discord.Member):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    await user.timeout(None)

    await interaction.response.send_message(
        f"🔊 {user.mention} susturma kaldırıldı."
    )


@bot.tree.command(name="warn")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str = "Sebep belirtilmedi"):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    warnings.setdefault(user.id, 0)
    warnings[user.id] += 1

    await interaction.response.send_message(
        f"⚠️ {user.mention} uyarıldı.\nSebep: {reason}\nToplam Warn: {warnings[user.id]}"
    )


@bot.tree.command(name="clear")
async def clear(interaction: discord.Interaction, miktar: int):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    await interaction.channel.purge(limit=miktar)

    await interaction.followup.send(f"🧹 {miktar} mesaj temizlendi.")


@bot.tree.command(name="kilit")
async def kilit(interaction: discord.Interaction):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message("🔒 Kanal kilitlendi.")


@bot.tree.command(name="aç")
async def ac(interaction: discord.Interaction):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = True

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message("🔓 Kanal açıldı.")


@bot.tree.command(name="rolver")
async def rolver(interaction: discord.Interaction, user: discord.Member, role: discord.Role):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    await user.add_roles(role)

    await interaction.response.send_message(
        f"✅ {user.mention} kullanıcısına {role.name} rolü verildi."
    )


@bot.tree.command(name="rolal")
async def rolal(interaction: discord.Interaction, user: discord.Member, role: discord.Role):

    if not is_yetkili(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
        return

    await user.remove_roles(role)

    await interaction.response.send_message(
        f"❌ {user.mention} kullanıcısından {role.name} rolü alındı."
    )

bot.run(TOKEN)
