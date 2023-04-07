from pyrogram import Client, filters
from pyrogram.types import Message
import configparser
import re
from playwright.sync_api import Playwright, sync_playwright

# Load config file using configparser
config = configparser.ConfigParser()
config.read('config.env')

# Get environment variables from config file
api_id = int(config['Telegram']['API_ID'])
api_hash = config['Telegram']['API_HASH']
bot_token = config['Telegram']['BOT_TOKEN']

# Create a new Pyrogram client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("mkv"))
def mkv_command(client: Client, message: Message):
    # Get the link from the message text using regex
    link_match = re.search(r"(?P<url>https?://[^\s]+)", message.text)
    link = link_match.group("url") if link_match else None

    if not link or "mkvcinema" not in link:
        message.reply_text("Invalid URL. Please provide a valid URL containing 'mkvcinema'.")

    else:
        # Send a typing indicator to let the user know that the program is working
        message.reply_chat_action("typing")

        try:
            # Call the process_link function to process the link
            result = run(link)

            # Reply with the processed link
            message.reply_text(f"Link processed successfully! {result}", disable_web_page_preview=True)

            # Send a confirmation message to let the user know that the link can now be used
            message.reply_text("You can now use the link.")

        except Exception as e:
            # Handle any exceptions that may occur
            message.reply_text(f"An error occurred: {str(e)}")

def run(link: str) -> str:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(link)
        page.locator("#soralink-human-verif-main").click()
        page.locator("#generater").click()
        with page.expect_popup() as page1_info:
            page.locator("#showlink").click()
        page1 = page1_info.value
        Flink = page1.url

        # ---------------------
        context.close()
        browser.close()

        return Flink

app.run()
