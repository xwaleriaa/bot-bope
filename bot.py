import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import asyncio
import os

TOKEN = os.environ.get("TOKEN")
GUILD_ID            = 1489574080309891153
CANAL_PORTARIA_ID   = 1489574082298253394
CANAL_PATENTE_ID    = 1489577108387659846
CARGO_AGUARDANDO_ID = 1489579701801586809

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class RegistroModal(Modal, title="📋 Registro — BOPEANÇA"):
    nome = TextInput(label="Nome no Jogo", placeholder="Ex: João_Silva", max_length=50, required=True)
    rg   = TextInput(label="RG", placeholder="Ex: 12.345.678-9", max_length=20, required=True)

    def __init__(self, notif_message=None, user_id=None):
        super().__init__()
        self.notif_message = notif_message
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        if self.user_id and interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ Você não pode registrar outro membro!", ephemeral=True)
            return

        nome_formatado = self.nome.value.strip().capitalize()
        rg_formatado = self.rg.value.strip()
        novo_apelido = f"{nome_formatado} | {rg_formatado}"

        apelido_aviso = ""
        try:
            await interaction.user.edit(nick=novo_apelido)
        except discord.Forbidden:
            apelido_aviso = "\n\n⚠️ **Não foi possível alterar seu apelido automaticamente.** Altere manualmente para: `" + novo_apelido + "`"
        except discord.HTTPException as e:
            apelido_aviso = f"\n\n⚠️ Erro ao alterar apelido: `{e}`"

        cargo = interaction.guild.get_role(CARGO_AGUARDANDO_ID)
        if cargo:
            await interaction.user.add_roles(cargo, reason="Registro concluído")

        if self.notif_message:
            try:
                await self.notif_message.delete()
            except:
                pass

        embed = discord.Embed(
            title="✅ Registro Concluído!",
            color=discord.Color.green(),
            description=(
                f"**Nome no Jogo:** {nome_formatado}\n"
                f"**RG:** {rg_formatado}\n\n"
                f"Agora vá para <#{CANAL_PATENTE_ID}> e solicite sua patente!"
                f"{apelido_aviso}"
            )
        )
        embed.set_footer(text="Bem-vindo ao BOPE FRANÇA!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class RegistroView(View):
    def __init__(self, user_id=None, notif_message=None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.notif_message = notif_message

    @discord.ui.button(label="📝 Registrar-se", style=discord.ButtonStyle.success, custom_id="btn_registrar")
    async def registrar(self, interaction: discord.Interaction, button: Button):
        cargo = interaction.guild.get_role(CARGO_AGUARDANDO_ID)
        if cargo and cargo in interaction.user.roles:
            await interaction.response.send_message("⚠️ Você já está registrado!", ephemeral=True)
            return
        await interaction.response.send_modal(
            RegistroModal(notif_message=self.notif_message, user_id=self.user_id)
        )


@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")
    bot.add_view(RegistroView())
    await asyncio.sleep(3)
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("❌ Servidor não encontrado!")
        return
    print(f"✅ Servidor: {guild.name}")
    canal = guild.get_channel(CANAL_PORTARIA_ID)
    if not canal:
        print("❌ Canal não encontrado!")
        return
    print(f"✅ Canal: {canal.name}")
    async for msg in canal.history(limit=50):
        if msg.author == bot.user:
            await msg.delete()
            await asyncio.sleep(0.3)
    embed = discord.Embed(
        title="🏛️ Bem-vindo à Portaria!",
        color=discord.Color.blurple(),
        description="Para ter acesso ao servidor, você precisa se registrar.\n\n**Clique no botão abaixo** e preencha:\n• **Nome no Jogo**\n• **RG**\n\nApós o registro, o canal de patente será liberado para você!"
    )
    embed.set_footer(text="Sistema de Registro Automático — BOPE FRANÇA")
    await canal.send(embed=embed, view=RegistroView())
    print("✅ Mensagem enviada!")


@bot.event
async def on_member_join(member: discord.Member):
    canal = member.guild.get_channel(CANAL_PORTARIA_ID)
    if canal:
        notif = await canal.send(
            f"👋 {member.mention}, bem-vindo! Clique no botão abaixo para se registrar.",
            view=RegistroView(user_id=member.id, notif_message=None)
        )
        view = RegistroView(user_id=member.id, notif_message=notif)
        await notif.edit(view=view)

    try:
        await member.send(
            "☠️ **BEM VINDO CAVEIRA!** AGORA VÁ FAZER SEU REGISTRO.\n\n"
            "👉 https://discord.com/channels/1489574080309891153/1489574082298253394"
        )
    except discord.Forbidden:
        pass


bot.run(TOKEN)
