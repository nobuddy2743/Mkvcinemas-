from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from requests import get as rget
from bs4 import BeautifulSoup
from urllib.parse import quote
import configparser
import time

# Load config file using configparser
config = configparser.ConfigParser()
config.read('config.env')

# Get environment variables from config file
api_id = int(config['Telegram']['API_ID'])
api_hash = config['Telegram']['API_HASH']
bot_token = config['Telegram']['BOT_TOKEN']

# Create a new Pyrogram client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# # Define command handler for /start command
# @app.on_message(filters.command(["start"]))
# def start_command(client, message):
#     # Define text and image to send
#     text = "Welcome to my bot!"
#     image_url = "https://graph.org/file/241ffc3db65af14e15477.png"

#     # Define inline keyboard with multiple buttons
#     keyboard = [
#             [
#               InlineKeyboardButton("Button 1", callback_data="button1"),
#               InlineKeyboardButton("Button 2", callback_data="button2")
#             ],
#             [
#               InlineKeyboardButton("Button 3", callback_data="button3")
#             ]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)

#     # Send message with image and buttons
#     message.reply_photo(image_url, caption=text, reply_markup=reply_markup)

# Define command handler
@app.on_message(filters.command(["search"]))
def search_command(client, message):
    # Get the movie name to search for
    if len(message.text.split()) > 1:
        movie_name = message.text.split("/search ")[1]
        if movie_name.strip() == "" or "http" in movie_name:
            message.reply_text("Search is wrong. Please enter a valid movie name.")
            return
    else:
        message.reply_text("Please enter a movie name to search.")
        return

    # TODO: Implement movie search code here
    res = rget(f"https://gdbot.xyz/search?q={quote(movie_name)}").text
    soup = BeautifulSoup(res, 'html.parser')
    tsear = soup.select("li")
    if not tsear:
        message.reply_text(f"No results found for '{movie_name}'.")
        return
    msg = ''
    for ss in tsear[4:]:
        b_list = ss.select("a[href*='gdbot.xyz']")
        if not b_list:
            continue
        b = b_list[0]
        msg += f'\n<b>{b.text}</b>'
        msg += f'{ss.select("span")[0].text}'
        resp = rget(b['href']).text
        nsoup = BeautifulSoup(resp, 'html.parser')
        gdtotL = nsoup.select("a[href*='gdtot']")
        if not gdtotL:
            continue
        gdtotL = gdtotL[0]['href']
        msg += f'\n{gdtotL}'
        
        # Split the message if it exceeds 4096 characters
        if len(msg) > 4096:
            message.reply_text(msg[:4096], disable_web_page_preview=True)
            msg = msg[4096:]
            time.sleep(1) # add a delay of 1 second between messages

    # Reply with a message indicating that the search is complete
    if msg:
        message.reply_text(msg, disable_web_page_preview=True)
        message.reply_text(f"Search for '{movie_name}' is complete.", disable_web_page_preview=True)
    else:
        message.reply_text(f"No results found for '{movie_name}'.")


# Start the bot
app.run()
