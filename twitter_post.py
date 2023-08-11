import tweepy
from tweepy import TweepyException
import discord
import config
import requests
import os
import asyncio

# Authenticate for Twitter
try:
    authenticate = tweepy.OAuthHandler(config.TWITTER_API_KEY, config.TWITTER_API_SECRET_KEY)
    authenticate.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(authenticate, wait_on_rate_limit=True)
    print("Connected to Twitter API successfully!")
except Exception as e:
    print(f"Error connecting to Twitter API: {e}")
    api = None

# Initialize Discord client
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)

# Main function
async def async_main():
    previous_values_file = 'previous_values.txt'
    previous_values = get_previous_values(previous_values_file)
    coin_values = get_coin_values()
    twitter_post = format_posts(coin_values, previous_values)

    try:
        post_on_twitter(twitter_post)
    except TweepyException as e:
        print(f"Error posting on Twitter: {e}")
        print("Skipping Twitter posting.")
    except Exception as e:
        print(f"Error connecting to Twitter API: {e}")
        print("Skipping Twitter posting.")

    await send_discord_message(twitter_post)

    save_current_values(previous_values_file, coin_values)

    print("Process completed successfully!")

@client.event
async def on_ready():
    print(f"Connected to Discord API successfully as {client.user}!")
    await async_main()

# Get previous coin values
def get_previous_values(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            previous_values = [tuple(map(float, line.strip().split(','))) for line in file.readlines()]
    else:
        previous_values = None
    return previous_values

# Save current coin values
def save_current_values(file_name, current_values):
    with open(file_name, 'w') as file:
        for value in current_values:
            file.write(f'{value[0]},{value[1]}\n')

# Get current coin values
def get_coin_values():
    coins = ['elrond-erd-2', 'cardano']
    values = []
    for coin in coins:
        r = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd%2Ceur&include_last_updated_at=%20')
        format_json = r.json()
        coin_usd_value = round(format_json[coin]['usd'], 2)
        coin_eur_value = round(format_json[coin]['eur'], 2)
        values.append((coin_usd_value, coin_eur_value))
    return values

# Format Twitter and Discord posts
def format_posts(coin_values, previous_values):
    coin_names = ['eGLD', 'ADA']
    coin_emojis = ['⚡️', '❈']
    lines = ["💹 Crypto Market Update 🚀"]
    
    for i, (usd, eur) in enumerate(coin_values):
        if previous_values is not None:
            if usd > previous_values[i][0]:
                trend_usd = "📈"
            elif usd < previous_values[i][0]:
                trend_usd = "📉"
            else:
                trend_usd = "📊"
            
            if eur > previous_values[i][1]:
                trend_eur = "📈"
            elif eur < previous_values[i][1]:
                trend_eur = "📉"  
            else:
                trend_eur = "📊" 
        else:
            trend_usd, trend_eur = "🔹", "🔹"

        lines.append(f"\n{coin_emojis[i]} ${coin_names[i]} 💎")
        lines.append(f"  {trend_usd} {usd} $USD 💵")
        lines.append(f"  {trend_eur} {eur} $EUR 💶\n")

    lines.append("👀 Updates every 6 hours! 👀\n#LfkinGo #MVX #Cardano")
    return "\n".join(lines)

# Twitter post
def post_on_twitter(twitter_post):
    try:
        api.update_status(twitter_post)
        print("Posted on Twitter successfully!")
    except TweepyException as e:
        print(f"Error posting on Twitter: {e}")
        print("Skipping Twitter posting.")
    except Exception as e:
        print(f"Error connecting to Twitter API: {e}")
        print("Skipping Twitter posting.")

# Discord post
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
    print("Bot has been stopped by the user.")