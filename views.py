import discord
from formatter import fmt_hand
from game import MAX_PLAY_CARDS


VIEW_TIMEOUT = 1800


RULES_TEXT = (
    "**🦁 Lion's Bar — Rules**\n\n"
    "🎯 **Table Rank:** Each round, one rank (A, K, or Q) is chosen as the table rank. "
    "All players must *claim* their played cards match that rank — even if they don't!\n\n"
    "🎴 **Playing Cards:** On your turn, play 1–3 cards from your hand. "
    "Jokers are wild and always count as the table rank.\n\n"
    "👀 **After You Play:** The next player must decide: "
    "**Challenge** (flip the cards) or **Pass** (play their own cards).\n\n"
    "🔍 **Challenge Results:**\n"
    "   • Challenge succeeds (someone lied) → the liar loses **1 HP**\n"
    "   • Challenge fails (cards were honest) → the challenger loses **1 HP**\n\n"
    "🔁 **End of Round:** Whenever a challenge happens, the round ends immediately, "
    "new cards are dealt, and a new table rank is chosen.\n\n"
    "👑 **Next Round:** The player who just lost HP goes first. "
    "If that player was eliminated, the next surviving player starts.\n\n"
    "🃏 **Empty Hands:** Players with no cards in hand are skipped. "
    "If only one player has cards left, they *must* challenge.\n\n"
    "🏆 **Winning:** Last player standing wins!\n\n"
    "──────────────────────\n"
    "**🃏 Card Info**\n"
    "A, K, Q — 10 copies each | Joker — 2 copies | **32 cards total**\n"
    "Starting hand: **5 cards** | Starting HP: **5 ♥**\n"
    "Max cards per play: **3**"
)


class JoinView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.cog = cog

    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.primary, emoji="🦁")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.handle_join(interaction)

    @discord.ui.button(label="Start Game", style=discord.ButtonStyle.success, emoji="▶")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.handle_start(interaction)

    @discord.ui.button(label="View Rules", style=discord.ButtonStyle.secondary, emoji="📜", row=1)
    async def rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(RULES_TEXT, ephemeral=True)


class AllHandsView(discord.ui.View):
    def __init__(self, cog, guild_id: int):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.cog = cog
        self.guild_id = guild_id

    @discord.ui.button(label="View My Hand", style=discord.ButtonStyle.primary, emoji="🃏")
    async def show_my_hand(self, interaction: discord.Interaction, button: discord.ui.Button):
        session = self.cog.get_session(self.guild_id)

        if not session:
            await interaction.response.send_message("Game not found.", ephemeral=True)
            return

        player = session.get_player(interaction.user.id)

        if not player:
            await interaction.response.send_message(
                "You are not a player in this game.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Table rank this round: **{session.table_rank}**\n{fmt_hand(player.hand)}",
            ephemeral=True,
        )


class TurnActionView(discord.ui.View):
    def __init__(self, cog, guild_id: int, current_player_id: int):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.cog = cog
        self.guild_id = guild_id
        self.current_player_id = current_player_id

    @discord.ui.button(label="Play Cards", style=discord.ButtonStyle.success, emoji="🎴")
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.current_player_id:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        session = self.cog.get_session(self.guild_id)

        if not session:
            await interaction.response.send_message("Game not found.", ephemeral=True)
            return

        player = session.get_player(interaction.user.id)

        if not player:
            await interaction.response.send_message(
                "You are not a player in this game.", ephemeral=True
            )
            return

        if len(player.hand) == 0:
            await interaction.response.send_message(
                "You have no cards left this round.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Table rank this round: **{session.table_rank}**\n"
            f"{fmt_hand(player.hand)}\n"
            f"Select 1–{MAX_PLAY_CARDS} cards. You will claim they are all **{session.table_rank}**.",
            view=HandView(self.cog, self.current_player_id, player.hand),
            ephemeral=True,
        )


class HandView(discord.ui.View):
    def __init__(self, cog, current_player_id: int, hand: list[str]):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.cog = cog
        self.current_player_id = current_player_id
        self.selected_indices: list[int] = []

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
            label="Confirm Play",
            style=discord.ButtonStyle.success,
            emoji="✔",
            row=1,
        )
        confirm_button.callback = self.confirm_play
        self.add_item(confirm_button)

    def _make_card_callback(self, index: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.current_player_id:
                await interaction.response.send_message(
                    "These are not your cards!", ephemeral=True
                )
                return

            if index in self.selected_indices:
                self.selected_indices.remove(index)
            else:
                if len(self.selected_indices) >= MAX_PLAY_CARDS:
                    await interaction.response.send_message(
                        f"You can only select up to {MAX_PLAY_CARDS} cards at once.",
                        ephemeral=True,
                    )
                    return
                self.selected_indices.append(index)

            self._refresh_buttons()
            await interaction.response.edit_message(view=self)

        return callback

    async def confirm_play(self, interaction: discord.Interaction):
        if interaction.user.id != self.current_player_id:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        if not self.selected_indices:
            await interaction.response.send_message(
                "Please select at least one card first!", ephemeral=True
            )
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
    def __init__(self, cog, doubter_id: int, allow_pass: bool):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.cog = cog
        self.doubter_id = doubter_id

        doubt_button = discord.ui.Button(
            label="Challenge!",
            style=discord.ButtonStyle.danger,
            emoji="🔍",
            row=0,
        )
        doubt_button.callback = self.doubt
        self.add_item(doubt_button)

        if allow_pass:
            pass_button = discord.ui.Button(
                label="Pass & Play",
                style=discord.ButtonStyle.secondary,
                emoji="✅",
                row=0,
            )
            pass_button.callback = self.pass_turn
            self.add_item(pass_button)

    async def doubt(self, interaction: discord.Interaction):
        if interaction.user.id != self.doubter_id:
            await interaction.response.send_message(
                "It's not your turn to challenge!", ephemeral=True
            )
            return

        self.stop()
        await self.cog.handle_doubt(interaction)

    async def pass_turn(self, interaction: discord.Interaction):
        if interaction.user.id != self.doubter_id:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        self.stop()
        await self.cog.handle_pass(interaction)
