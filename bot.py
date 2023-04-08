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
    try:
        # Get the link from the message text
        link = message.text.split(" ")[1]

        # Send a waiting message
        wait_message = message.reply_text("Please wait while processing the link...")

        # Call the process_link function to process the link
        run(link, message, wait_message)

    except IndexError:
        # Handle index error (when there is no link provided)
        message.reply_text("Please provide a link after the command, like this: /mkv https://example.com")

    except Exception as e:
        # Handle any other exception
        message.reply_text(f"An error occurred: {e}")

def run(link: str, message, wait_message):
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(link)

            # Wait for the element to become visible and then click it
            page.wait_for_selector("#soralink-human-verif-main")
            page.locator("#soralink-human-verif-main").click()

            # Click the second button after waiting for it to become visible
            page.wait_for_selector("#generater")
            page.locator("#generater").click()

            # Wait for and handle the popup window
            with page.expect_popup() as page1_info:
                page.wait_for_selector("#showlink")
                page.locator("#showlink").click()
            page1 = page1_info.value
            Flink = page1.url

            # Reply with the processed link
            message.reply_text(f"Link processed successfully! {Flink}", disable_web_page_preview=True)

            # Delete the waiting message
            wait_message.delete()

            # ---------------------
            context.close()
            browser.close()

    except Exception as e:
        # Handle any exception that occurred during link processing
        message.reply_text(f"An error occurred while processing the link: {e}")

        # Delete the waiting message
        wait_message.delete()

app.run()
