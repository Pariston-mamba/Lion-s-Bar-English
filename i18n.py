LANG_AUTO = "auto"
LANG_EN = "en"
LANG_ZH = "zh"


def normalize_language(value: str | None) -> str:
    if value in {LANG_AUTO, LANG_EN, LANG_ZH}:
        return value
    return LANG_AUTO


def locale_to_language(locale) -> str:
    text = str(locale or "").lower()
    if text.startswith("zh"):
        return LANG_ZH
    return LANG_EN


def t(lang: str | None, key: str, **kwargs) -> str:
    selected = lang if lang in {LANG_EN, LANG_ZH} else LANG_EN
    template = TEXT.get(selected, {}).get(key) or TEXT[LANG_EN].get(key) or key
    return template.format(**kwargs)


TEXT = {
    LANG_EN: {
        "game_already_started": "The game has already started. You cannot join now.",
        "room_full": "Room is full. Maximum 6 players.",
        "already_joined": "You are already in the room.",
        "joined_ok": "Joined successfully.",
        "need_two_players": "At least 2 players are required to start.",
        "already_started": "The game has already started.",
        "game_started_ok": "Game started.",
        "not_player": "You are not a player in this game.",
        "not_your_turn": "It's not your turn yet.",
        "eliminated": "You have been eliminated.",
        "select_at_least_one": "Please select at least 1 card.",
        "max_cards": "You can play at most {max} cards at once.",
        "duplicate_card": "Cannot select the same card twice.",
        "invalid_card_index": "Invalid card index.",
        "cards_played_ok": "Cards played successfully.",
        "button_join": "Join Game",
        "button_start": "Start Game",
        "button_rules": "View Rules",
        "button_view_hand": "View My Hand",
        "button_play_cards": "Play Cards",
        "button_confirm_play": "Confirm Play",
        "button_challenge": "Challenge!",
        "button_pass_play": "Pass & Play",
        "create_in_progress": (
            "A game is already in progress! If buttons are stuck or the game froze, "
            "use `/reset` and then `/create`."
        ),
        "room_created": (
            "🦁 **Lion's Bar room created!**\n"
            "Click the button below to join. The game starts once 2-6 players have joined.\n"
            "**Note: Buttons expire after 30 minutes. If things get stuck, use `/reset` then `/create`.**\n\n"
            "{lobby}"
        ),
        "stop_none": "There is no game currently in progress.",
        "stop_done": "The game has been force-ended. You can now use `/create` to start a new one.",
        "reset_done": "Lion's Bar has been reset. You can now use `/create` to start a new game.",
        "status_none": "There is no game currently in progress.",
        "status_text": "Table rank this round: **{rank}**\n\n{board}",
        "rules_text": (
            "**🦁 Lion's Bar - Rules**\n\n"
            "🎯 **Table Rank:** Each round, one rank (A, K, or Q) is chosen as the table rank. "
            "All players must *claim* their played cards match that rank - even if they don't!\n\n"
            "🎴 **Playing Cards:** On your turn, play 1-3 cards from your hand. "
            "Jokers are wild and always count as the table rank.\n\n"
            "👀 **After You Play:** The next player must decide: "
            "**Challenge** (flip the cards) or **Pass** (play their own cards).\n\n"
            "🔍 **Challenge Results:**\n"
            "   • Challenge succeeds (someone lied) -> the liar loses **1 HP**\n"
            "   • Challenge fails (cards were honest) -> the challenger loses **1 HP**\n\n"
            "🔁 **End of Round:** Whenever a challenge happens, the round ends immediately, "
            "new cards are dealt, and a new table rank is chosen.\n\n"
            "👑 **Next Round:** The player who just lost HP goes first. "
            "If that player was eliminated, the next surviving player starts.\n\n"
            "🃏 **Empty Hands:** Players with no cards in hand are skipped. "
            "If only one player has cards left, they *must* challenge.\n\n"
            "🏆 **Winning:** Last player standing wins!\n\n"
            "──────────────────────\n"
            "**🃏 Card Info**\n"
            "The deck is rebuilt each round based on the number of alive players:\n"
            "2 players: A/K/Q x3 each + Joker x1 = **10 cards**\n"
            "3 players: A/K/Q x4 each + Joker x3 = **15 cards**\n"
            "4 players: A/K/Q x6 each + Joker x2 = **20 cards**\n"
            "5 players: A/K/Q x7 each + Joker x4 = **25 cards**\n"
            "6 players: A/K/Q x9 each + Joker x3 = **30 cards**\n"
            "Starting hand: **5 cards** | Starting HP: **5 ♥**\n"
            "Max cards per play: **3**"
        ),
        "help_text": (
            "**🦁 Lion's Bar - Commands**\n\n"
            "`/create` - Create a new game room (2-6 players)\n"
            "`/stop` - Force end the current game\n"
            "`/reset` - Reset a stuck or broken game\n"
            "`/status` - View current HP standings mid-game\n"
            "`/rules` - View detailed game rules\n"
            "`/language` - Set this server's language\n"
            "`/help` - Show this message\n\n"
            "**How to play in short:**\n"
            "Create a room -> players join -> start game -> take turns playing cards and "
            "claiming they match the table rank -> challenge or get caught lying -> "
            "last player standing wins! 🏆"
        ),
        "language_set_auto": (
            "Language set to **Auto**. Public game text follows the room creator's Discord language; "
            "private replies follow each player's language."
        ),
        "language_set_en": "Language set to **English** for this server.",
        "language_set_zh": "Language set to **中文** for this server.",
        "joined_room": "✅ **{name}** joined the room!\n\n{lobby}",
        "start_no_session": "Please use `/create` to open a room first.",
        "game_start": (
            "🎮 **Lion's Bar - Game Start!**\n"
            "Table rank this round: **{rank}**\n\n"
            "{board}\n"
            "All players can click below to view their hand."
        ),
        "play_no_session": "Game not found. Please use `/create` to start a new one.",
        "cards_played": "Cards played!",
        "all_others_out": "All other players are out of cards. Round over - dealing new cards.",
        "must_challenge": "<@{player_id}> You are the only player left with cards - you must challenge!",
        "doubt_prompt": "<@{player_id}> Do you want to **challenge**, or **pass and play your own cards**?",
        "nothing_to_challenge": "There is nothing to challenge right now.",
        "revealing": "Revealing cards!",
        "passed_play": "✅ Passed - your turn to play.",
        "new_round": (
            "New round! Table rank: **{rank}**\n"
            "All players can click below to view their new hand."
        ),
        "turn_prompt": (
            "<@{player_id}> It's your turn! "
            "You must claim your cards are **{rank}** this round."
        ),
        "game_not_found": "Game not found.",
        "not_in_game": "You are not a player in this game.",
        "view_hand": "Table rank this round: **{rank}**\n{hand}",
        "play_cards_prompt": (
            "Table rank this round: **{rank}**\n"
            "{hand}\n"
            "Select 1-{max} cards. You will claim they are all **{rank}**."
        ),
        "not_turn_short": "It's not your turn!",
        "not_turn_challenge": "It's not your turn to challenge!",
        "not_your_cards": "These are not your cards!",
        "no_cards_left": "You have no cards left this round.",
        "select_limit": "You can only select up to {max} cards at once.",
        "select_card_first": "Please select at least one card first!",
        "hp_status": "── HP Status ──",
        "formatter_eliminated": "Eliminated",
        "formatter_cards": "({count} card(s))",
        "hand_empty": "You have no cards left this round.",
        "your_hand": "Your hand:",
        "verdict_liar": "LIAR!",
        "verdict_honest": "HONEST!",
        "loses_hp": "{name} loses 1 HP!",
        "claimed": "Claimed: {rank} × {count}",
        "actual": "Actual:  ",
        "play_announce": "{name} played {count} card(s), claiming {rank}",
        "hp_remaining": "{name} has {hp} HP remaining",
        "game_over": "🏆 Game Over!",
        "winner": "Winner: {name}!",
        "no_players": "No players have joined yet.",
        "room_players": "── Room Players ──",
        "players_count": "Players: {count} / 6",
    },
    LANG_ZH: {
        "game_already_started": "遊戲已經開始，不能加入。",
        "room_full": "房間已滿，最多 6 人。",
        "already_joined": "你已經在房間裡了。",
        "joined_ok": "加入成功。",
        "need_two_players": "至少需要 2 位玩家才能開始。",
        "already_started": "遊戲已經開始。",
        "game_started_ok": "遊戲開始。",
        "not_player": "你不是本局玩家。",
        "not_your_turn": "還沒輪到你。",
        "eliminated": "你已經被淘汰。",
        "select_at_least_one": "請至少選擇 1 張牌。",
        "max_cards": "一次最多只能出 {max} 張牌。",
        "duplicate_card": "不能重複選同一張牌。",
        "invalid_card_index": "手牌索引錯誤。",
        "cards_played_ok": "出牌成功。",
        "button_join": "加入遊戲",
        "button_start": "開始遊戲",
        "button_rules": "查看規則",
        "button_view_hand": "查看我的手牌",
        "button_play_cards": "出牌",
        "button_confirm_play": "確認出牌",
        "button_challenge": "質疑！",
        "button_pass_play": "不質疑，繼續出牌",
        "create_in_progress": "已經有遊戲在進行中！如果按鈕失效或遊戲卡住，請先用 `/reset`，再用 `/create`。",
        "room_created": (
            "🦁 **Lion's Bar 房間已建立！**\n"
            "點下方按鈕加入，集齊 2-6 人後開始遊戲。\n"
            "**提示：按鈕 30 分鐘後會失效；如果卡住，請用 `/reset` 後重新 `/create`。**\n\n"
            "{lobby}"
        ),
        "stop_none": "目前沒有進行中的遊戲。",
        "stop_done": "遊戲已強制結束。現在可以重新使用 `/create`。",
        "reset_done": "Lion's Bar 已重置。現在可以重新使用 `/create`。",
        "status_none": "目前沒有進行中的遊戲。",
        "status_text": "本輪桌面牌：**{rank}**\n\n{board}",
        "rules_text": (
            "**🦁 Lion's Bar 規則**\n\n"
            "🎯 **桌面牌：** 每輪會指定一種桌面牌，例如 A、K 或 Q。"
            "所有玩家都只能宣稱自己出的牌符合桌面牌，就算其實不是。\n\n"
            "🎴 **出牌：** 輪到你時，可以從手牌中出 1-3 張牌。"
            "Joker 是萬用牌，永遠可以當作桌面牌。\n\n"
            "👀 **出牌後：** 下一位玩家要先決定："
            "**質疑**（翻開上一位的牌）或 **不質疑**（輪到自己出牌）。\n\n"
            "🔍 **質疑結果：**\n"
            "   • 質疑成功（有人說謊）-> 說謊者扣 **1 HP**\n"
            "   • 質疑失敗（上一位誠實）-> 質疑者扣 **1 HP**\n\n"
            "🔁 **回合結束：** 只要有人質疑並翻牌，該輪立刻結束，重新發牌並指定新的桌面牌。\n\n"
            "👑 **下一輪：** 剛剛扣血的玩家先出牌；如果該玩家被淘汰，則由下一位存活玩家開始。\n\n"
            "🃏 **手牌出光：** 本輪沒有手牌的玩家會被跳過；如果只剩一位玩家有手牌，該玩家必須質疑。\n\n"
            "🏆 **勝利：** 活到最後的人獲勝！\n\n"
            "──────────────────────\n"
            "**🃏 牌組資訊**\n"
            "每輪會依照存活玩家人數重新建立牌組：\n"
            "2 人：A/K/Q 各 3 張 + Joker 1 張 = **10 張**\n"
            "3 人：A/K/Q 各 4 張 + Joker 3 張 = **15 張**\n"
            "4 人：A/K/Q 各 6 張 + Joker 2 張 = **20 張**\n"
            "5 人：A/K/Q 各 7 張 + Joker 4 張 = **25 張**\n"
            "6 人：A/K/Q 各 9 張 + Joker 3 張 = **30 張**\n"
            "起始手牌：**5 張** | 起始血量：**5 ♥**\n"
            "每次最多出牌：**3 張**"
        ),
        "help_text": (
            "**🦁 Lion's Bar 指令**\n\n"
            "`/create` - 建立新房間（2-6 人）\n"
            "`/stop` - 強制結束目前遊戲\n"
            "`/reset` - 重置卡住或壞掉的遊戲\n"
            "`/status` - 查看目前血量與回合狀態\n"
            "`/rules` - 查看詳細規則\n"
            "`/language` - 設定本伺服器語言\n"
            "`/help` - 顯示這則說明\n\n"
            "**簡短玩法：**\n"
            "建立房間 -> 玩家加入 -> 開始遊戲 -> 輪流出牌並宣稱符合桌面牌 -> "
            "質疑或被抓到說謊 -> 活到最後的人獲勝！🏆"
        ),
        "language_set_auto": "語言已設為 **自動**。公開遊戲訊息會跟著開房者語言，私密回覆會跟著各玩家語言。",
        "language_set_en": "本伺服器語言已設為 **English**。",
        "language_set_zh": "本伺服器語言已設為 **中文**。",
        "joined_room": "✅ **{name}** 加入了房間！\n\n{lobby}",
        "start_no_session": "請先用 `/create` 建立房間。",
        "game_start": (
            "🎮 **Lion's Bar 開始！**\n"
            "本輪桌面牌：**{rank}**\n\n"
            "{board}\n"
            "所有玩家可以點下方按鈕查看自己的手牌。"
        ),
        "play_no_session": "找不到遊戲。請用 `/create` 重新建立。",
        "cards_played": "出牌完成！",
        "all_others_out": "其他玩家都已出光手牌，本輪結束並重新發牌。",
        "doubt_prompt": "<@{player_id}> 你要 **質疑**，還是 **不質疑並輪到自己出牌**？",
        "nothing_to_challenge": "目前沒有可質疑的出牌。",
        "revealing": "翻牌！",
        "passed_play": "✅ 選擇不質疑，輪到你出牌。",
        "new_round": (
            "新一輪開始！本輪桌面牌：**{rank}**\n"
            "所有玩家可以點下方按鈕查看自己的新手牌。"
        ),
        "turn_prompt": "<@{player_id}> 輪到你出牌！本輪你只能宣稱自己出的是 **{rank}**。",
        "game_not_found": "找不到遊戲。",
        "not_in_game": "你不是本局玩家。",
        "view_hand": "本輪桌面牌：**{rank}**\n{hand}",
        "play_cards_prompt": (
            "本輪桌面牌：**{rank}**\n"
            "{hand}\n"
            "請選擇 1-{max} 張牌。你將宣稱它們都是 **{rank}**。"
        ),
        "not_turn_short": "還沒輪到你！",
        "not_turn_challenge": "還沒輪到你質疑！",
        "not_your_cards": "這不是你的手牌！",
        "no_cards_left": "你本輪已經沒有手牌。",
        "select_limit": "一次最多只能選 {max} 張牌。",
        "select_card_first": "請先選擇要打出的牌！",
        "hp_status": "── 血量狀態 ──",
        "formatter_eliminated": "淘汰",
        "formatter_cards": "({count} 張)",
        "hand_empty": "你本輪已經沒有手牌。",
        "your_hand": "你的手牌：",
        "verdict_liar": "說謊！",
        "verdict_honest": "誠實！",
        "loses_hp": "{name} 扣 1 HP！",
        "claimed": "聲稱：{rank} × {count}",
        "actual": "實際：",
        "play_announce": "{name} 打出了 {count} 張牌，聲稱是 {rank}",
        "hp_remaining": "{name} 剩餘 {hp} HP",
        "game_over": "🏆 遊戲結束！",
        "winner": "勝者是 {name}！",
        "no_players": "還沒有玩家加入",
        "room_players": "── 房間玩家 ──",
        "players_count": "人數：{count} / 6",
    },
}
