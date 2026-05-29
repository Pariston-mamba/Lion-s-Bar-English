import discord
from discord.ext import commands
from game import GameSession, GameState, MAX_PLAY_CARDS
from formatter import (
    fmt_hp_board, fmt_reveal, fmt_play_announce,
    fmt_eliminated, fmt_winner, fmt_lobby,
)
from i18n import LANG_AUTO, LANG_EN, LANG_ZH, locale_to_language, normalize_language, t
from views import JoinView, AllHandsView, TurnActionView, DoubtView


class LionsBarCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sessions: dict[int, GameSession] = {}
        self.guild_languages: dict[int, str] = {}
        self.session_languages: dict[int, str] = {}

    def get_session(self, guild_id: int) -> GameSession | None:
        return self.sessions.get(guild_id)

    def get_or_create_session(self, guild_id: int, channel_id: int) -> GameSession:
        if guild_id not in self.sessions:
            self.sessions[guild_id] = GameSession(guild_id, channel_id)
        return self.sessions[guild_id]

    def private_lang(self, interaction: discord.Interaction) -> str:
        setting = self.guild_languages.get(interaction.guild_id, LANG_AUTO)
        if setting != LANG_AUTO:
            return setting
        return locale_to_language(interaction.locale)

    def public_lang(self, guild_id: int, interaction: discord.Interaction | None = None) -> str:
        setting = self.guild_languages.get(guild_id, LANG_AUTO)
        if setting != LANG_AUTO:
            return setting
        if guild_id in self.session_languages:
            return self.session_languages[guild_id]
        if interaction:
            return locale_to_language(interaction.locale)
        return LANG_EN

    def text_kwargs(self) -> dict[str, int]:
        return {"max": MAX_PLAY_CARDS}

    # ── Slash commands ────────────────────────────────────────────────────────

    @discord.app_commands.command(name="create", description="Create a new Lion's Bar game room")
    async def create(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        lang = self.private_lang(interaction)

        if guild_id in self.sessions and self.sessions[guild_id].state == GameState.PLAYING:
            await interaction.response.send_message(t(lang, "create_in_progress"), ephemeral=True)
            return

        self.session_languages[guild_id] = self.public_lang(guild_id, interaction)
        public_lang = self.public_lang(guild_id, interaction)
        self.sessions[guild_id] = GameSession(guild_id, interaction.channel_id)

        await interaction.response.send_message(
            t(
                public_lang,
                "room_created",
                lobby=fmt_lobby(self.sessions[guild_id], public_lang),
            ),
            view=JoinView(self, public_lang),
        )

    @discord.app_commands.command(name="stop", description="Force end the current game")
    async def stop(self, interaction: discord.Interaction):
        lang = self.private_lang(interaction)

        if interaction.guild_id not in self.sessions:
            await interaction.response.send_message(t(lang, "stop_none"), ephemeral=True)
            return

        del self.sessions[interaction.guild_id]
        self.session_languages.pop(interaction.guild_id, None)
        await interaction.response.send_message(t(lang, "stop_done"))

    @discord.app_commands.command(name="reset", description="Reset a stuck Lion's Bar game")
    async def reset(self, interaction: discord.Interaction):
        lang = self.private_lang(interaction)
        self.sessions.pop(interaction.guild_id, None)
        self.session_languages.pop(interaction.guild_id, None)
        await interaction.response.send_message(t(lang, "reset_done"))

    @discord.app_commands.command(name="status", description="View current HP standings")
    async def status(self, interaction: discord.Interaction):
        lang = self.private_lang(interaction)
        session = self.get_session(interaction.guild_id)

        if not session or session.state != GameState.PLAYING:
            await interaction.response.send_message(t(lang, "status_none"), ephemeral=True)
            return

        await interaction.response.send_message(
            t(lang, "status_text", rank=session.table_rank, board=fmt_hp_board(session, lang))
        )

    @discord.app_commands.command(name="rules", description="View Lion's Bar game rules")
    async def rules(self, interaction: discord.Interaction):
        lang = self.private_lang(interaction)
        await interaction.response.send_message(t(lang, "rules_text"), ephemeral=True)

    @discord.app_commands.command(name="help", description="Show all available commands")
    async def help_cmd(self, interaction: discord.Interaction):
        lang = self.private_lang(interaction)
        await interaction.response.send_message(t(lang, "help_text"), ephemeral=True)

    @discord.app_commands.command(name="language", description="Set Lion's Bar language for this server")
    @discord.app_commands.choices(language=[
        discord.app_commands.Choice(name="Auto", value=LANG_AUTO),
        discord.app_commands.Choice(name="English", value=LANG_EN),
        discord.app_commands.Choice(name="中文", value=LANG_ZH),
    ])
    async def language(self, interaction: discord.Interaction, language: discord.app_commands.Choice[str]):
        selected = normalize_language(language.value)

        if selected == LANG_AUTO:
            self.guild_languages.pop(interaction.guild_id, None)
            self.session_languages.pop(interaction.guild_id, None)
            lang = self.private_lang(interaction)
            await interaction.response.send_message(t(lang, "language_set_auto"), ephemeral=True)
            return

        self.guild_languages[interaction.guild_id] = selected
        self.session_languages[interaction.guild_id] = selected
        await interaction.response.send_message(
            t(selected, f"language_set_{selected}"),
            ephemeral=True,
        )

    # ── Button handlers ───────────────────────────────────────────────────────

    async def handle_join(self, interaction: discord.Interaction):
        private_lang = self.private_lang(interaction)
        public_lang = self.public_lang(interaction.guild_id, interaction)
        session = self.get_or_create_session(interaction.guild_id, interaction.channel_id)
        ok, msg = session.add_player(interaction.user.id, interaction.user.display_name)

        if not ok:
            await interaction.response.send_message(
                t(private_lang, msg, **self.text_kwargs()),
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            t(
                public_lang,
                "joined_room",
                name=interaction.user.display_name,
                lobby=fmt_lobby(session, public_lang),
            )
        )

    async def handle_start(self, interaction: discord.Interaction):
        private_lang = self.private_lang(interaction)
        public_lang = self.public_lang(interaction.guild_id, interaction)
        session = self.get_session(interaction.guild_id)

        if not session:
            await interaction.response.send_message(t(private_lang, "start_no_session"), ephemeral=True)
            return

        ok, msg = session.start_game()

        if not ok:
            await interaction.response.send_message(
                t(private_lang, msg, **self.text_kwargs()),
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            t(
                public_lang,
                "game_start",
                rank=session.table_rank,
                board=fmt_hp_board(session, public_lang),
            ),
            view=AllHandsView(self, session.guild_id, public_lang),
        )

        await self._prompt_turn(interaction.channel, session)

    async def handle_play(self, interaction: discord.Interaction, indices: list[int]):
        private_lang = self.private_lang(interaction)
        public_lang = self.public_lang(interaction.guild_id, interaction)
        session = self.get_session(interaction.guild_id)

        if not session:
            await interaction.response.send_message(t(private_lang, "play_no_session"), ephemeral=True)
            return

        ok, msg = session.play_cards(interaction.user.id, indices)

        if not ok:
            await interaction.response.send_message(
                t(private_lang, msg, **self.text_kwargs()),
                ephemeral=True,
            )
            return

        claim = session.last_claim

        await interaction.response.edit_message(content=t(private_lang, "cards_played"), view=None)
        await interaction.channel.send(
            fmt_play_announce(
                interaction.user.display_name,
                claim.claimed_rank,
                claim.claimed_count,
                public_lang,
            )
        )

        contenders = session.other_players_with_cards(claim.player_id)

        if not contenders:
            await interaction.channel.send(t(public_lang, "all_others_out"))
            session.reset_round()
            await self._announce_new_round(interaction.channel, session)
            await self._prompt_turn(interaction.channel, session)
            return

        if len(contenders) == 1:
            forced = contenders[0]
            session.set_current_player(forced.discord_id)
            await interaction.channel.send(
                t(public_lang, "must_challenge", player_id=forced.discord_id),
                view=DoubtView(self, forced.discord_id, allow_pass=False, lang=public_lang),
            )
            return

        session.advance_turn(skip_empty=True)
        doubter = session.get_current_player()

        await interaction.channel.send(
            t(public_lang, "doubt_prompt", player_id=doubter.discord_id),
            view=DoubtView(self, doubter.discord_id, allow_pass=True, lang=public_lang),
        )

    async def handle_doubt(self, interaction: discord.Interaction):
        private_lang = self.private_lang(interaction)
        public_lang = self.public_lang(interaction.guild_id, interaction)
        session = self.get_session(interaction.guild_id)

        if not session:
            await interaction.response.send_message(t(private_lang, "play_no_session"), ephemeral=True)
            return

        claim = session.last_claim

        if not claim:
            await interaction.response.send_message(t(private_lang, "nothing_to_challenge"), ephemeral=True)
            return

        is_lying = session.check_lie()
        loser_id = claim.player_id if is_lying else interaction.user.id
        loser = session.get_player(loser_id)

        await interaction.response.edit_message(content=t(private_lang, "revealing"), view=None)
        await interaction.channel.send(fmt_reveal(claim, is_lying, loser.display_name, public_lang))

        loser, eliminated = session.apply_damage(loser_id)

        if eliminated:
            await interaction.channel.send(fmt_eliminated(loser.display_name, loser.hp, public_lang))

        winner = session.check_winner()

        if winner:
            await interaction.channel.send(fmt_hp_board(session, public_lang))
            await interaction.channel.send(fmt_winner(winner.display_name, public_lang))
            del self.sessions[interaction.guild_id]
            self.session_languages.pop(interaction.guild_id, None)
            return

        if loser.is_alive:
            session.set_current_player(loser.discord_id)
        else:
            session.advance_turn(skip_empty=False)

        session.reset_round()

        await interaction.channel.send(fmt_hp_board(session, public_lang))
        await self._announce_new_round(interaction.channel, session)
        await self._prompt_turn(interaction.channel, session)

    async def handle_pass(self, interaction: discord.Interaction):
        private_lang = self.private_lang(interaction)
        public_lang = self.public_lang(interaction.guild_id, interaction)
        session = self.get_session(interaction.guild_id)

        if not session:
            await interaction.response.send_message(t(private_lang, "play_no_session"), ephemeral=True)
            return

        current = session.get_current_player()

        if interaction.user.id != current.discord_id:
            await interaction.response.send_message(t(private_lang, "not_turn_short"), ephemeral=True)
            return

        await interaction.response.edit_message(content=t(private_lang, "passed_play"), view=None)
        await self._prompt_turn(interaction.channel, session)

    # ── Internal helpers ──────────────────────────────────────────────────────

    async def _announce_new_round(self, channel: discord.TextChannel, session: GameSession):
        lang = self.public_lang(session.guild_id)
        await channel.send(
            t(lang, "new_round", rank=session.table_rank),
            view=AllHandsView(self, session.guild_id, lang),
        )

    async def _prompt_turn(self, channel: discord.TextChannel, session: GameSession):
        lang = self.public_lang(session.guild_id)
        current = session.get_current_player()

        if len(current.hand) == 0:
            session.advance_turn(skip_empty=True)
            current = session.get_current_player()

        await channel.send(
            t(lang, "turn_prompt", player_id=current.discord_id, rank=session.table_rank),
            view=TurnActionView(self, session.guild_id, current.discord_id, lang),
        )
