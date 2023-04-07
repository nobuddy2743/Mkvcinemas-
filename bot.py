from pyrogram import Client, filters
from pyrogram.types import Message
import configparser
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
    # Get the link from the message text
    link = message.text.split(" ")[1]

    # Call the process_link function to process the link
    process_link(link, message)

def process_link(link, message):
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
        print(Flink)

        # ---------------------
        context.close()
        browser.close()

        # Reply with the processed link
        message.reply_text(f"Link processed successfully! {Flink}")

app.run()
