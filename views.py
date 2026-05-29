import discord
from formatter import fmt_hand
from game import MAX_PLAY_CARDS
from i18n import t


VIEW_TIMEOUT = 1800


class JoinView(discord.ui.View):
    def __init__(self, cog, lang: str):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.cog = cog
        self.lang = lang

        join_button = discord.ui.Button(
            label=t(lang, "button_join"),
            style=discord.ButtonStyle.primary,
            emoji="🦁",
            row=0,
        )
        join_button.callback = self.join
        self.add_item(join_button)

        start_button = discord.ui.Button(
            label=t(lang, "button_start"),
            style=discord.ButtonStyle.success,
            emoji="▶",
            row=0,
        )
        start_button.callback = self.start
        self.add_item(start_button)

        rules_button = discord.ui.Button(
            label=t(lang, "button_rules"),
            style=discord.ButtonStyle.secondary,
            emoji="📜",
            row=1,
        )
        rules_button.callback = self.rules
        self.add_item(rules_button)

    async def join(self, interaction: discord.Interaction):
        await self.cog.handle_join(interaction)

    async def start(self, interaction: discord.Interaction):
        await self.cog.handle_start(interaction)

    async def rules(self, interaction: discord.Interaction):
        lang = self.cog.private_lang(interaction)
        await interaction.response.send_message(t(lang, "rules_text"), ephemeral=True)


class AllHandsView(discord.ui.View):
    def __init__(self, cog, guild_id: int, lang: str):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.cog = cog
        self.guild_id = guild_id
        self.lang = lang

        button = discord.ui.Button(
            label=t(lang, "button_view_hand"),
            style=discord.ButtonStyle.primary,
            emoji="🃏",
        )
        button.callback = self.show_my_hand
        self.add_item(button)

    async def show_my_hand(self, interaction: discord.Interaction):
        lang = self.cog.private_lang(interaction)
        session = self.cog.get_session(self.guild_id)

        if not session:
            await interaction.response.send_message(t(lang, "game_not_found"), ephemeral=True)
            return

        player = session.get_player(interaction.user.id)

        if not player:
            await interaction.response.send_message(t(lang, "not_in_game"), ephemeral=True)
            return

        await interaction.response.send_message(
            t(lang, "view_hand", rank=session.table_rank, hand=fmt_hand(player.hand, lang)),
            ephemeral=True,
        )


class TurnActionView(discord.ui.View):
    def __init__(self, cog, guild_id: int, current_player_id: int, lang: str):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.cog = cog
        self.guild_id = guild_id
        self.current_player_id = current_player_id
        self.lang = lang

        button = discord.ui.Button(
            label=t(lang, "button_play_cards"),
            style=discord.ButtonStyle.success,
            emoji="🎴",
        )
        button.callback = self.play
        self.add_item(button)

    async def play(self, interaction: discord.Interaction):
        lang = self.cog.private_lang(interaction)

        if interaction.user.id != self.current_player_id:
            await interaction.response.send_message(t(lang, "not_turn_short"), ephemeral=True)
            return

        session = self.cog.get_session(self.guild_id)

        if not session:
            await interaction.response.send_message(t(lang, "game_not_found"), ephemeral=True)
            return

        player = session.get_player(interaction.user.id)

        if not player:
            await interaction.response.send_message(t(lang, "not_in_game"), ephemeral=True)
            return

        if len(player.hand) == 0:
            await interaction.response.send_message(t(lang, "no_cards_left"), ephemeral=True)
            return

        await interaction.response.send_message(
            t(
                lang,
                "play_cards_prompt",
                rank=session.table_rank,
                hand=fmt_hand(player.hand, lang),
                max=MAX_PLAY_CARDS,
            ),
            view=HandView(self.cog, self.current_player_id, player.hand, lang),
            ephemeral=True,
        )


class HandView(discord.ui.View):
    def __init__(self, cog, current_player_id: int, hand: list[str], lang: str):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.cog = cog
        self.current_player_id = current_player_id
        self.selected_indices: list[int] = []
        self.lang = lang

        for i, card in enumerate(hand):
            button = discord.ui.Button(
                label=card,
                style=discord.ButtonStyle.secondary,
                custom_id=f"card_{i}",
                row=0,
            )
            button.callback = self._make_card_callback(i)
            self.add_item(button)

        confirm_button = discord.ui.Button(
            label=t(lang, "button_confirm_play"),
            style=discord.ButtonStyle.success,
            emoji="✔",
            row=1,
        )
        confirm_button.callback = self.confirm_play
        self.add_item(confirm_button)

    def _make_card_callback(self, index: int):
        async def callback(interaction: discord.Interaction):
            lang = self.cog.private_lang(interaction)

            if interaction.user.id != self.current_player_id:
                await interaction.response.send_message(t(lang, "not_your_cards"), ephemeral=True)
                return

            if index in self.selected_indices:
                self.selected_indices.remove(index)
            else:
                if len(self.selected_indices) >= MAX_PLAY_CARDS:
                    await interaction.response.send_message(
                        t(lang, "select_limit", max=MAX_PLAY_CARDS),
                        ephemeral=True,
                    )
                    return
                self.selected_indices.append(index)

            self._refresh_buttons()
            await interaction.response.edit_message(view=self)

        return callback

    async def confirm_play(self, interaction: discord.Interaction):
        lang = self.cog.private_lang(interaction)

        if interaction.user.id != self.current_player_id:
            await interaction.response.send_message(t(lang, "not_turn_short"), ephemeral=True)
            return

        if not self.selected_indices:
            await interaction.response.send_message(t(lang, "select_card_first"), ephemeral=True)
            return

        await self.cog.handle_play(interaction, self.selected_indices)

    def _refresh_buttons(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.custom_id and item.custom_id.startswith("card_"):
                index = int(item.custom_id.split("_")[1])
                item.style = (
                    discord.ButtonStyle.primary
                    if index in self.selected_indices
                    else discord.ButtonStyle.secondary
                )


class DoubtView(discord.ui.View):
    def __init__(self, cog, doubter_id: int, allow_pass: bool, lang: str):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.cog = cog
        self.doubter_id = doubter_id
        self.lang = lang

        doubt_button = discord.ui.Button(
            label=t(lang, "button_challenge"),
            style=discord.ButtonStyle.danger,
            emoji="🔍",
            row=0,
        )
        doubt_button.callback = self.doubt
        self.add_item(doubt_button)

        if allow_pass:
            pass_button = discord.ui.Button(
                label=t(lang, "button_pass_play"),
                style=discord.ButtonStyle.secondary,
                emoji="✅",
                row=0,
            )
            pass_button.callback = self.pass_turn
            self.add_item(pass_button)

    async def doubt(self, interaction: discord.Interaction):
        lang = self.cog.private_lang(interaction)

        if interaction.user.id != self.doubter_id:
            await interaction.response.send_message(t(lang, "not_turn_challenge"), ephemeral=True)
            return

        self.stop()
        await self.cog.handle_doubt(interaction)

    async def pass_turn(self, interaction: discord.Interaction):
        lang = self.cog.private_lang(interaction)

        if interaction.user.id != self.doubter_id:
            await interaction.response.send_message(t(lang, "not_turn_short"), ephemeral=True)
            return

        self.stop()
        await self.cog.handle_pass(interaction)
