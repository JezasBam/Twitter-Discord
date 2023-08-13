import tweepy
from tweepy.errors import TweepyException
import config
import requests
import os
import json
import asyncio

# Configure Twitter authentication
auth = tweepy.Client(consumer_key=config.TWITTER_API_KEY,
                                consumer_secret=config.TWITTER_API_SECRET_KEY,
                                access_token=config.TWITTER_ACCESS_TOKEN,
                                access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
                                bearer_token=config.TWITTER_BEARER_TOKEN)

api = tweepy.API(auth)

# Main function
async def async_main():
    coin_values = get_coin_values()
    update_price_status(coin_values)
    twitter_message = format_twitter_message(coin_values)

    await send_twitter_message(twitter_message)

    print("Process completed successfully!")

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
def format_twitter_message(coin_values):
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



# Send Twitter message
async def send_twitter_message(message):
    try:
        auth.create_tweet(text=message)
        print("Posted on Twitter successfully!")
    except tweepy.errors.TweepyException as e:
        print(f"Error posting on Twitter: {e}")
# Run the async function
async def main():
    try:
        await async_main()
    except KeyboardInterrupt:
        print("\nProcess has been stopped by the user.")

# Run the async function using asyncio
if __name__ == "__main__":
    asyncio.run(main())