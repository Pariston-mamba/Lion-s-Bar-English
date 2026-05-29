# Lion's Bar Bot

A Discord bot for playing a bluffing card game inspired by the classic bar game *Liar's Bar*.
Players take turns playing cards and claiming a rank — bluff your way through, or challenge the liar!

## File Structure

```
lionsbar-bot/
├── bot.py          # Main entry point
├── cog.py          # Discord slash commands & button logic
├── game.py         # Core game logic and data structures
├── formatter.py    # ANSI colour formatting helpers
├── views.py        # Discord UI button components
├── requirements.txt
└── .env            # Local development only (do NOT upload to GitHub)
```

## Commands

| Command | Description |
|---------|-------------|
| `/create` | Create a new Lion's Bar room |
| `/stop` | Force end the current game |
| `/reset` | Reset a stuck or broken game |
| `/status` | View current HP standings |
| `/rules` | View detailed game rules |
| `/help` | Show all available commands |

## How to Play

1. `/create` — open a room
2. Players click **Join Game** (2–6 players supported)
3. Any player clicks **Start Game**
4. On your turn: select cards → confirm → claim they are all the table rank
5. The next player chooses **Challenge** or **Pass & Play**
6. Caught bluffing → the liar loses 1 HP; failed challenge → the challenger loses 1 HP
7. Last player standing wins!

## Card Rules

| Rank | Copies |
|------|--------|
| A    | 10     |
| K    | 10     |
| Q    | 10     |
| Joker | 2 (wild) |
| **Total** | **32** |

- Starting hand: **5 cards** per player
- Starting HP: **5 ♥** per player
- Max cards played per turn: **3**
- New cards are dealt after every challenge

## Environment Variables

Create a `.env` file for local development:
```
DISCORD_TOKEN=your_bot_token_here
```

When deploying to Render, set `DISCORD_TOKEN` in the **Environment Variables** dashboard.

## Deployment (Render)

| Field | Value |
|-------|-------|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python bot.py` |
