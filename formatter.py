from game import GameSession, MAX_HP, JOKER
from i18n import t

R = "\u001b[31m"
G = "\u001b[32m"
Y = "\u001b[33m"
B = "\u001b[34m"
M = "\u001b[35m"
C = "\u001b[36m"
W = "\u001b[37m"
GRAY = "\u001b[30m"
BOLD = "\u001b[1m"
RESET = "\u001b[0m"


def ansi(text: str) -> str:
    return f"```ansi\n{text}\n```"


def fmt_hp_board(session: GameSession, lang: str = "en") -> str:
    lines = [f"{BOLD}{W}{t(lang, 'hp_status')}{RESET}"]

    for player in session.players:
        is_current = (
            session.state.value == "playing"
            and session.players[session.current_turn].discord_id == player.discord_id
            and player.is_alive
        )

        if not player.is_alive:
            lines.append(
                f"{GRAY}  {player.display_name:<14} ✕ {t(lang, 'formatter_eliminated')}{RESET}"
            )
            continue

        if player.hp >= 4:
            hp_color = G
        elif player.hp >= 2:
            hp_color = Y
        else:
            hp_color = R

        hearts = f"{hp_color}{'♥ ' * player.hp}{RESET}{GRAY}{'♡ ' * (MAX_HP - player.hp)}{RESET}"
        arrow = f"{Y}▶ {RESET}" if is_current else "  "
        hand_count = f"{GRAY}{t(lang, 'formatter_cards', count=len(player.hand))}{RESET}"

        lines.append(f"{arrow}{BOLD}{player.display_name:<14}{RESET} {hearts} {hand_count}")

    return ansi("\n".join(lines))


def fmt_hand(hand: list[str], lang: str = "en") -> str:
    if not hand:
        return ansi(f"{GRAY}{t(lang, 'hand_empty')}{RESET}")

    cards = "  ".join(f"{BOLD}{C}[ {card} ]{RESET}" for card in hand)
    return ansi(f"{W}{t(lang, 'your_hand')}{RESET}\n{cards}")


def fmt_reveal(claim, is_lying: bool, loser_name: str, lang: str = "en") -> str:
    colored = []

    for card in claim.actual_cards:
        if card == claim.claimed_rank or card == JOKER:
            colored.append(f"{G}{card}{RESET}")
        else:
            colored.append(f"{R}{card}{RESET}")

    cards_str = "  ".join(colored)
    verdict_key = "verdict_liar" if is_lying else "verdict_honest"
    verdict_color = R if is_lying else G
    verdict = f"{BOLD}{verdict_color}{t(lang, verdict_key)}{RESET}"
    loser_line = f"{BOLD}{R}{t(lang, 'loses_hp', name=loser_name)}{RESET}"

    lines = [
        f"{Y}{t(lang, 'claimed', rank=claim.claimed_rank, count=claim.claimed_count)}{RESET}",
        f"{W}{t(lang, 'actual')}{RESET}{cards_str}",
        "",
        f"{verdict}  →  {loser_line}",
    ]

    return ansi("\n".join(lines))


def fmt_play_announce(player_name: str, claimed_rank: str, claimed_count: int, lang: str = "en") -> str:
    text = t(
        lang,
        "play_announce",
        name=player_name,
        count=claimed_count,
        rank=claimed_rank,
    )
    return ansi(f"{BOLD}{W}{text}{RESET}")


def fmt_eliminated(player_name: str, hp_left: int, lang: str = "en") -> str:
    if hp_left <= 0:
        return ansi(f"{BOLD}{R}💀 {player_name} {t(lang, 'formatter_eliminated')}!{RESET}")

    return ansi(f"{R}{t(lang, 'hp_remaining', name=player_name, hp=hp_left)}{RESET}")


def fmt_winner(player_name: str, lang: str = "en") -> str:
    return ansi(
        f"{BOLD}{Y}{t(lang, 'game_over')}{RESET}\n"
        f"{BOLD}{G}{t(lang, 'winner', name=player_name)}{RESET}"
    )


def fmt_lobby(session: GameSession, lang: str = "en") -> str:
    if not session.players:
        return ansi(f"{GRAY}{t(lang, 'no_players')}{RESET}")

    lines = [f"{BOLD}{W}{t(lang, 'room_players')}{RESET}"]

    for i, player in enumerate(session.players):
        lines.append(f"  {C}{i + 1}.{RESET} {player.display_name}")

    lines.append(f"\n{GRAY}{t(lang, 'players_count', count=len(session.players))}{RESET}")

    return ansi("\n".join(lines))
