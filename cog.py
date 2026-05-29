import discord
from discord.ext import commands
from game import GameSession, GameState
from formatter import (
    fmt_hp_board, fmt_reveal, fmt_play_announce,
    fmt_eliminated, fmt_winner, fmt_lobby,
)
from views import JoinView, AllHandsView, TurnActionView, DoubtView, RULES_TEXT


class LionsBarCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sessions: dict[int, GameSession] = {}

    def get_session(self, guild_id: int) -> GameSession | None:
        return self.sessions.get(guild_id)

    def get_or_create_session(self, guild_id: int, channel_id: int) -> GameSession:
        if guild_id not in self.sessions:
            self.sessions[guild_id] = GameSession(guild_id, channel_id)
        return self.sessions[guild_id]

    # ── Slash commands ────────────────────────────────────────────────────────

    @discord.app_commands.command(name="create", description="Create a new Lion's Bar game room")
    async def create(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id

        if guild_id in self.sessions and self.sessions[guild_id].state == GameState.PLAYING:
            await interaction.response.send_message(
                "A game is already in progress! "
                "If buttons are stuck or the game froze, use `/reset` and then `/create`.",
                ephemeral=True,
            )
            return

        self.sessions[guild_id] = GameSession(guild_id, interaction.channel_id)

        await interaction.response.send_message(
            "🦁 **Lion's Bar room created!**\n"
            "Click the button below to join. The game starts once 2–6 players have joined.\n"
            "**Note: Buttons expire after 30 minutes. If things get stuck, use `/reset` then `/create`.**\n\n"
            + fmt_lobby(self.sessions[guild_id]),
            view=JoinView(self),
        )

    @discord.app_commands.command(name="stop", description="Force end the current game")
    async def stop(self, interaction: discord.Interaction):
        if interaction.guild_id not in self.sessions:
            await interaction.response.send_message(
                "There is no game currently in progress.", ephemeral=True
            )
            return

        del self.sessions[interaction.guild_id]
        await interaction.response.send_message(
            "The game has been force-ended. You can now use `/create` to start a new one."
        )

    @discord.app_commands.command(name="reset", description="Reset a stuck Lion's Bar game")
    async def reset(self, interaction: discord.Interaction):
        self.sessions.pop(interaction.guild_id, None)
        await interaction.response.send_message(
            "Lion's Bar has been reset. You can now use `/create` to start a new game."
        )

    @discord.app_commands.command(name="status", description="View current HP standings")
    async def status(self, interaction: discord.Interaction):
        session = self.get_session(interaction.guild_id)

        if not session or session.state != GameState.PLAYING:
            await interaction.response.send_message(
                "There is no game currently in progress.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Table rank this round: **{session.table_rank}**\n\n{fmt_hp_board(session)}"
        )

    @discord.app_commands.command(name="rules", description="View Lion's Bar game rules")
    async def rules(self, interaction: discord.Interaction):
        await interaction.response.send_message(RULES_TEXT, ephemeral=True)

    @discord.app_commands.command(name="help", description="Show all available commands")
    async def help_cmd(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "**🦁 Lion's Bar — Commands**\n\n"
            "`/create` — Create a new game room (2–6 players)\n"
            "`/stop`   — Force end the current game\n"
            "`/reset`  — Reset a stuck or broken game\n"
            "`/status` — View current HP standings mid-game\n"
            "`/rules`  — View detailed game rules\n"
            "`/help`   — Show this message\n\n"
            "**How to play in short:**\n"
            "Create a room → players join → start game → take turns playing cards and "
            "claiming they match the table rank → challenge or get caught lying → "
            "last player standing wins! 🏆",
            ephemeral=True,
        )

    # ── Button handlers ───────────────────────────────────────────────────────

    async def handle_join(self, interaction: discord.Interaction):
        session = self.get_or_create_session(interaction.guild_id, interaction.channel_id)
        ok, msg = session.add_player(interaction.user.id, interaction.user.display_name)

        if not ok:
            await interaction.response.send_message(msg, ephemeral=True)
            return

        await interaction.response.send_message(
            f"✅ **{interaction.user.display_name}** joined the room!\n\n{fmt_lobby(session)}"
        )

    async def handle_start(self, interaction: discord.Interaction):
        session = self.get_session(interaction.guild_id)

        if not session:
            await interaction.response.send_message(
                "Please use `/create` to open a room first.", ephemeral=True
            )
            return

        ok, msg = session.start_game()

        if not ok:
            await interaction.response.send_message(msg, ephemeral=True)
            return

        await interaction.response.send_message(
            f"🎮 **Lion's Bar — Game Start!**\n"
            f"Table rank this round: **{session.table_rank}**\n\n"
            f"{fmt_hp_board(session)}\n"
            "All players can click below to view their hand.",
            view=AllHandsView(self, session.guild_id),
        )

        await self._prompt_turn(interaction.channel, session)

    async def handle_play(self, interaction: discord.Interaction, indices: list[int]):
        session = self.get_session(interaction.guild_id)

        if not session:
            await interaction.response.send_message(
                "Game not found. Please use `/create` to start a new one.", ephemeral=True
            )
            return

        ok, msg = session.play_cards(interaction.user.id, indices)

        if not ok:
            await interaction.response.send_message(msg, ephemeral=True)
            return

        claim = session.last_claim

        await interaction.response.edit_message(content="Cards played!", view=None)
        await interaction.channel.send(
            fmt_play_announce(interaction.user.display_name, claim.claimed_rank, claim.claimed_count)
        )

        contenders = session.other_players_with_cards(claim.player_id)

        if not contenders:
            await interaction.channel.send(
                "All other players are out of cards. Round over — dealing new cards."
            )
            session.reset_round()
            await self._announce_new_round(interaction.channel, session)
            await self._prompt_turn(interaction.channel, session)
            return

        if len(contenders) == 1:
            forced = contenders[0]
            session.set_current_player(forced.discord_id)
            await interaction.channel.send(
                f"<@{forced.discord_id}> You are the only player left with cards — you must challenge!",
                view=DoubtView(self, forced.discord_id, allow_pass=False),
            )
            return

        session.advance_turn(skip_empty=True)
        doubter = session.get_current_player()

        await interaction.channel.send(
            f"<@{doubter.discord_id}> Do you want to **challenge**, or **pass and play your own cards**?",
            view=DoubtView(self, doubter.discord_id, allow_pass=True),
        )

    async def handle_doubt(self, interaction: discord.Interaction):
        session = self.get_session(interaction.guild_id)

        if not session:
            await interaction.response.send_message(
                "Game not found. Please use `/create` to start a new one.", ephemeral=True
            )
            return

        claim = session.last_claim

        if not claim:
            await interaction.response.send_message(
                "There is nothing to challenge right now.", ephemeral=True
            )
            return

        is_lying = session.check_lie()
        loser_id = claim.player_id if is_lying else interaction.user.id
        loser = session.get_player(loser_id)

        await interaction.response.edit_message(content="Revealing cards!", view=None)
        await interaction.channel.send(fmt_reveal(claim, is_lying, loser.display_name))

        loser, eliminated = session.apply_damage(loser_id)

        if eliminated:
            await interaction.channel.send(fmt_eliminated(loser.display_name, loser.hp))

        winner = session.check_winner()

        if winner:
            await interaction.channel.send(fmt_hp_board(session))
            await interaction.channel.send(fmt_winner(winner.display_name))
            del self.sessions[interaction.guild_id]
            return

        if loser.is_alive:
            session.set_current_player(loser.discord_id)
        else:
            session.advance_turn(skip_empty=False)

        session.reset_round()

        await interaction.channel.send(fmt_hp_board(session))
        await self._announce_new_round(interaction.channel, session)
        await self._prompt_turn(interaction.channel, session)

    async def handle_pass(self, interaction: discord.Interaction):
        session = self.get_session(interaction.guild_id)

        if not session:
            await interaction.response.send_message(
                "Game not found. Please use `/create` to start a new one.", ephemeral=True
            )
            return

        current = session.get_current_player()

        if interaction.user.id != current.discord_id:
            await interaction.response.send_message("It's not your turn.", ephemeral=True)
            return

        await interaction.response.edit_message(
            content="✅ Passed — your turn to play.", view=None
        )
        await self._prompt_turn(interaction.channel, session)

    # ── Internal helpers ──────────────────────────────────────────────────────

    async def _announce_new_round(self, channel: discord.TextChannel, session: GameSession):
        await channel.send(
            f"New round! Table rank: **{session.table_rank}**\n"
            "All players can click below to view their new hand.",
            view=AllHandsView(self, session.guild_id),
        )

    async def _prompt_turn(self, channel: discord.TextChannel, session: GameSession):
        current = session.get_current_player()

        if len(current.hand) == 0:
            session.advance_turn(skip_empty=True)
            current = session.get_current_player()

        await channel.send(
            f"<@{current.discord_id}> It's your turn! "
            f"You must claim your cards are **{session.table_rank}** this round.",
            view=TurnActionView(self, session.guild_id, current.discord_id),
        )
