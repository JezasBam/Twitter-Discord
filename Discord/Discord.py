import discord
import config
import requests
import os
import json

# Initialize Discord client
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)

# Main function
async def async_main():
    coin_values = get_coin_values()
    update_price_status(coin_values)
    discord_message = format_discord_message(coin_values)

    await send_discord_message(discord_message)

    print("Process completed successfully!")

@client.event
async def on_ready():
    print(f"Connected to Discord API successfully as {client.user}!")
    await async_main()

# Get current coin values
def get_coin_values():
    coins = ['elrond-erd-2']
    values = []

    for coin in coins:
        r = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd%2Ceur&include_last_updated_at=%20')
        format_json = r.json()
        coin_usd_value = round(format_json[coin]['usd'], 2)
        coin_eur_value = round(format_json[coin]['eur'], 5)
        values.append((coin_usd_value, coin_eur_value))

    r = requests.get('https://api.onedex.app/prices')
    data = r.json()

    estar_data = next((item for item in data if item["identifier"] == "ESTAR-461bab"), None)
    if estar_data:
        price_usdc = float(estar_data['priceUsdc'])
        price_wegld = float(estar_data['priceWegld'])
        values.append((price_usdc, price_wegld))

    return values

# Update price status
def update_price_status(coin_values):
    status = []

    if os.path.exists('price_status.json'):
        with open('price_status.json', 'r') as file:
            status = json.load(file)

    for i, (usd, eur) in enumerate(coin_values):
        if i < len(status):
            prev_usd, prev_eur = status[i]
            if usd > prev_usd:
                status[i] = (usd, 'up')
            elif usd < prev_usd:
                status[i] = (usd, 'down')
            else:
                status[i] = (usd, 'stagnate')
        else:
            status.append((usd, 'stagnate'))

    with open('price_status.json', 'w') as file:
        json.dump(status, file)

# ...

# Format Discord message
def format_discord_message(coin_values):
    coin_names = ['**$EGLD**', '**$ESTAR -> OneDex**']
    lines = ["🚀 **​🇪​​🇬​​🇱​​🇩​ & ​🇪​​🇸​​🇹​​🇦​​🇷​** 🚀"]

    with open('price_status.json', 'r') as file:
        status = json.load(file)

    for i, (usd, eur) in enumerate(coin_values):
        price_status = status[i][1]
        price_indicator_usd = ''
        price_indicator_eur = ''

        if price_status == 'up':
            price_indicator_usd = '🟢'
            price_indicator_eur = '🟢'
        elif price_status == 'down':
            price_indicator_usd = '🔴'
            price_indicator_eur = '🔴'
        else:
            price_indicator_usd = '⏸️'
            price_indicator_eur = '⏸️'

        if i == 0:
            usd_str = f"{price_indicator_usd} {usd:.2f} **$USD** 💵"
            eur_str = f"{price_indicator_eur} {eur:.2f} **$EUR** 💶"
        else:
            usd_str = f"{price_indicator_usd} {usd:.5f} **$USD** 💵"
            eur_str = f"{price_indicator_eur} {eur:.5f} **$wEGLD Swap** 🔄"

        if i < len(coin_names):
            lines.append(f"\n{coin_names[i]}")
            lines.append(f"  {usd_str}")
            lines.append(f"  {eur_str}")

    lines.append("\n👀 **ᴜᴘᴅᴀᴛᴇꜱ ᴇᴠᴇʀʏ 6 ʜᴏᴜʀꜱ !**👀")
    return "\n".join(lines)

# ...



# Discord message
async def send_discord_message(message):
    for channel_id in config.DISCORD_CHANNEL_IDS:
        channel = client.get_channel(channel_id)
        if channel:
            try:
                await channel.send(message)
                print(f"Posted on Discord successfully in channel ID {channel_id}!")
            except discord.DiscordException as e:
                print(f"Error posting on Discord in channel ID {channel_id}: {e}")
        else:
            print(f"Channel ID {channel_id} not found or bot doesn't have access.")
    print("Message was sent to all specified Discord channels.")

# Run the Discord client
try:
    client.run(config.DISCORD_BOT_TOKEN)
except KeyboardInterrupt:
    print("\nBot has been stopped by the user.")
