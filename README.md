# Lion's Bar Bot

Lion's Bar is a Discord bluffing card party game for 2-6 players.

Players create a room, join with buttons, view private hands, play cards, challenge bluffs, lose HP, and fight to be the last player standing.

This version supports English and Chinese.

## Commands

| Command | Description |
|---------|-------------|
| `/create` | Create a new Lion's Bar room |
| `/stop` | Force end the current game |
| `/reset` | Reset a stuck or broken game |
| `/status` | View current HP and turn status |
| `/rules` | View detailed game rules |
| `/help` | Show all available commands |
| `/language` | Set language to Auto, English, or Chinese |

## Language

Use:

```txt
/language
```

Options:

```txt
Auto
English
中文
```

Auto mode uses the room creator's Discord language for public game messages.
Private replies, such as hand viewing and error messages, follow the clicking user's Discord language.

## How To Play

1. Use `/create` to open a room.
2. Players click **Join Game**.
3. Start the game when 2-6 players have joined.
4. Each round has a table rank, such as A, K, or Q.
5. On your turn, play 1-3 cards and claim they match the table rank.
6. The next player may **Challenge** or **Pass & Play**.
7. If the played cards do not match the table rank, the player who bluffed loses 1 HP.
8. If the challenge is wrong, the challenger loses 1 HP.
9. After a challenge, a new round begins with fresh hands.
10. The last player alive wins.

## Card Rules

| Rank | Copies |
|------|--------|
| A | 10 |
| K | 10 |
| Q | 10 |
| Joker | 2 wild cards |
| Total | 32 |

- Starting hand: 5 cards per player
- Starting HP: 5
- Max cards played per turn: 3
- New cards are dealt after every challenge

## Files

```txt
bot.py
cog.py
game.py
formatter.py
i18n.py
views.py
requirements.txt
README.md
```

## Environment Variables

For Render, set this in the Environment Variables dashboard:

```txt
DISCORD_TOKEN=your_bot_token_here
```

Do not upload a real `.env` file to GitHub.

## Render Settings

| Field | Value |
|-------|-------|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python bot.py` |
