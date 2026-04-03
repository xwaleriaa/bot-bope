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

class RegistroModal(Modal, title="📋 Registro — BOPE FRANÇA"):
    nome = TextInput(label="Nome no Jogo", placeholder="Ex: João_Silva", max_length=50, required=True)
    rg   = TextInput(label="RG", placeholder="Ex: 12.345.678-9", max_length=20, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        cargo = interaction.guild.get_role(CARGO_AGUARDANDO_ID)
        if cargo:
            await interaction.user.add_roles(cargo, reason="Registro concluído")
        embed = discord.Embed(title="✅ Registro Concluído!", color=discord.Color.green(),
            description=f"**Nome no Jogo:** {self.nome.value}\n**RG:** {self.rg.value}\n\nAgora vá para <#{CANAL_PATENTE_ID}> e solicite sua patente!")
        embed.set_footer(text="Bem-vindo ao BOPE FRANÇA!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RegistroView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Registrar-se", style=discord.ButtonStyle.success, custom_id="btn_registrar")
    async def registrar(self, interaction: discord.Interaction, button: Button):
        cargo = interaction.guild.get_role(CARGO_AGUARDANDO_ID)
        if cargo and cargo in interaction.user.roles:
            await interaction.response.send_message("⚠️ Você já está registrado!", ephemeral=True)
            return
        await interaction.response.send_modal(RegistroModal())

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")
    bot.add_view(RegistroView())
    await asyncio.sleep(3)
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print(f"❌ Servidor não encontrado!")
        return
    print(f"✅ Servidor: {guild.name}")
    canal = guild.get_channel(CANAL_PORTARIA_ID)
    if not canal:
        print(f"❌ Canal não encontrado!")
        return
    print(f"✅ Canal: {canal.name}")
    async for msg in canal.history(limit=20):
        if msg.author == bot.user:
            await msg.delete()
            await asyncio.sleep(0.3)
    embed = discord.Embed(title="🏛️ Bem-vindo à Portaria!", color=discord.Color.blurple(),
        description="Para ter acesso ao servidor, você precisa se registrar.\n\n**Clique no botão abaixo** e preencha:\n• **Nome no Jogo**\n• **RG**\n\nApós o registro, o canal de patente será liberado para você!")
    embed.set_footer(text="Sistema de Registro Automático — BOPE FRANÇA")
    await canal.send(embed=embed, view=RegistroView())
    print("✅ Mensagem enviada!")

@bot.event
async def on_member_join(member: discord.Member):
    try:
        await member.send(f"👋 Olá, {member.name}! Vá para **#⚠️-registra-se** e clique em **Registrar-se**!")
    except discord.Forbidden:
        pass

bot.run(TOKEN)