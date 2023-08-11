import tweepy
import discord
import config
import requests
import os

os.chdir('C:\Users\cscat\Desktop\md\twitter_post.py')

# Authenticate for Twitter
authenticate = tweepy.OAuthHandler(config.TWITTER_API_KEY, config.TWITTER_API_SECRET_KEY)
authenticate.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(authenticate, wait_on_rate_limit=True)

# Initialize Discord client
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)

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
    except tweepy.TweepError as e:
        print(f"Error posting on Twitter: {e}")

# Discord post
async def send_discord_message(message):
    for channel_id in config.DISCORD_CHANNEL_IDS:
        channel = client.get_channel(channel_id)
        if channel:
            await channel.send(message)
            print(f"Posted on Discord successfully in channel ID {channel_id}!")
        else:
            print(f"Channel with ID {channel_id} not found on Discord.")

# ...

# Main function
async def main():
    previous_values_file = 'previous_values.txt'
    previous_values = get_previous_values(previous_values_file)
    coin_values = get_coin_values()
    twitter_post = format_posts(coin_values, previous_values)

    post_on_twitter(twitter_post)
    await send_discord_message(twitter_post)  # Aici folosim await pentru a aștepta finalizarea

    save_current_values(previous_values_file, coin_values)

    print("Process completed successfully!")

# Run the main function
if __name__ == "__main__":
    client.loop.run_until_complete(main())  # Folosim loop-ul clientului Discord pentru a rula funcția asincronă
    client.run(config.DISCORD_BOT_TOKEN)
