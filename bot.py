import re
import time
import psutil
import requests
import urllib.parse
import configparser
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from base64 import b64decode
from playwright.sync_api import Playwright, sync_playwright
from requests import get as rget
from urllib.parse import quote
from pyrogram.types import Message

# Load config file using configparser
config = configparser.ConfigParser()
config.read('config.env')

# Get environment variables from config file
api_id = int(config['Telegram']['API_ID'])
api_hash = config['Telegram']['API_HASH']
bot_token = config['Telegram']['BOT_TOKEN']
GDTOT_CRYPT = "RzR4ZHZoeG9DSUQrVWg4aG1HaGplQnphVmo0OFFMMzFYMzhmdG14Q2pyVT0%3D"
DRIVE_URL_TEMPLATE = "https://drive.google.com/open?id={}"
INDEX_URL_TEMPLATE = "https://wzml.wzmlcloud.workers.dev/0:/GDToT/{}"

# Create a new Pyrogram client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# MOVIE SEARCH CODE
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

# STATS CODE
# define the command handler for /stats command
@app.on_message(filters.command("stats"))
def get_system_stats(client, message):
    # get system memory and CPU usage
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent()

    # get disk usage stats
    disk = psutil.disk_usage('/')
    disk_total = round(disk.total / (1024*1024*1024), 2)
    disk_used = round(disk.used / (1024*1024*1024), 2)
    disk_free = round(disk.free / (1024*1024*1024), 2)

    # get network usage stats
    network = psutil.net_io_counters()
    sent = round(network.bytes_sent / (1024*1024), 2)
    received = round(network.bytes_recv / (1024*1024), 2)

    # format the system stats message
    stats_message = f"System Stats:\n\nCPU Usage: {cpu}%\nMemory Usage: {memory.percent}%\nDisk Usage: {disk_used}GB / {disk_total}GB ({disk.percent}%)\nNetwork Usage: {sent}MB sent / {received}MB received"

    # send the system stats message
    message.reply_text(stats_message)

# GDTOT CODE
@app.on_message(filters.command(["gdtot"]))
def gdtot_command(client, message):
    try:
        link = message.text.split(" ")[1]

        # Extract the match object from the link using regex
        match = re.findall(r'https?://(.+)\.gdtot\.(.+)\/\S+\/\S+', link)[0]

        with requests.Session() as session:
            # Update the session cookies with the GDTOT crypt value
            session.cookies.update({'crypt': GDTOT_CRYPT})

            # Make a GET request to the GDTOT link
            session.get(link)

            # Make another GET request to fetch the actual download link
            res = session.get(f"https://{match[0]}.gdtot.{match[1]}/dld?id={link.split('/')[-1]}")

            try:
                # Decode the Google Drive ID from the response using base64 decoding
                encoded_string = re.findall('gd=(.*?)&', res.text)[0]
                decoded_id = b64decode((encoded_string + '==').encode()).decode('utf-8')
                drive_link = DRIVE_URL_TEMPLATE.format(decoded_id)
                response = requests.get(link)
                soup = BeautifulSoup(response.text, 'html.parser')
                headings = soup.find_all('h5', {'class': 'm-0 font-weight-bold'})
                results = []
                for heading in headings:
                    string_to_encode = heading.text.strip()
                    encoded_string = urllib.parse.quote(string_to_encode)
                    results.append((drive_link, INDEX_URL_TEMPLATE.format(encoded_string)))
                for result in results:
                    message.reply_text(f"Executing GDTOT link: {result[0]}\n\nExecuting Index link: {result[1]}", disable_web_page_preview=True)
            except (IndexError, TypeError, ValueError) as e:
                message.reply_text(f"Error: {e}")
    except IndexError:
        message.reply_text("Invalid GDTOT link provided. Please check and try again.")

# MKVBYPASS
# Define the process_link function
def process_link(playwright: Playwright, link: str, message: Message) -> str:
    try:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(link)
        page.locator("#soralink-human-verif-main").click()
        page.locator("#generater").click()
        with page.expect_popup() as page1_info:
            page.locator("#showlink").click()
        page1 = page1_info.value
        final_link = page1.url

        # Close the browser and context
        context.close()
        browser.close()

        return final_link
    except Exception as e:
        # Close the browser and context
        try:
            context.close()
        except:
            pass

        try:
            browser.close()
        except:
            pass

        # Raise the exception to handle it in the mkv_command function
        raise e

# Define the mkv_command function
@app.on_message(filters.command("mkv"))
def mkv_command(client: Client, message: Message):
    try:
        # Get the link from the message text
        link = message.text.split(" ")[1]

        # Check if the link contains "mkvcinemas"
        if "mkvcinemas" not in link:
            message.reply_text("Invalid link. Link must be of 'mkvcinemas.com'.")
            return

        # Send processing message
        process_message = message.reply_text("Processing link, please wait...", quote=True)

        with sync_playwright() as playwright:
            final_link = process_link(playwright, link, message)

        # Edit the process message with the final link
        process_message.edit_text(f"Link processed successfully! \n{final_link}", disable_web_page_preview=True)
    except IndexError:
        # When no link is provided in the message
        message.reply_text("Please provide a valid link after the command. For example, `/mkv https://example.com`", quote=True)
    except Exception as e:
        # When an error occurs during the processing of the link
        message.reply_text(f"An error occurred while processing the link: {e}", quote=True)

# Define the mkv_command function
@app.on_message(filters.command("mkva"))
def mkvcinemas(client: Client, message: Message):
    try:
        # Get the link from the message text
        link = message.text.split(" ")[1]

        # Check if the link contains "mkvcinemas"
        if "mkvcinemas" not in link:
            message.reply_text("Invalid link. Link must be of 'mkvcinemas.com'.")
            return

        # Send processing message
        process_message = message.reply_text("Processing link, please wait...", quote=True)

        # Use the requests library to get the HTML content of the link
        response = requests.get(link)
        html_content = response.text
    
        # Use BeautifulSoup to parse the HTML content and extract all links from the page
        soup = BeautifulSoup(html_content, "html.parser")
        links = [a["href"] for a in soup.find_all("a", {"class": "gdlink"}, href=True)]
    
        # Create an empty list to store the final links
        final_links = []

        # Loop through the links and process only those that contain "mkvcinemas" in the URL
        for link in links:
            if "mkvcinemas" in link:
                with sync_playwright() as playwright:
                    final_link = process_link(playwright, link, message)
                    # Extract the title of the link and append it to the final link
                    title = soup.find("a", {"href": link, "class": "gdlink"}).text
                    final_link += f" - {title}\n"
                    final_links.append(final_link)

        # Edit the process message with the final links
        final_links_text = "\n".join(final_links)

        # Split the final links into chunks of up to 10 links per message
        links_per_message = 5
        final_links_chunks = [final_links[i:i+links_per_message] for i in range(0, len(final_links), links_per_message)]

        for i, links_chunk in enumerate(final_links_chunks):
            # Send each chunk of links as a separate message
            message_text = f"Links processed successfully! (Part {i+1}/{len(final_links_chunks)}) \n\n" + "\n".join(links_chunk)
            message.reply_text(message_text, disable_web_page_preview=True)

    except IndexError:
        # When no link is provided in the message
        message.reply_text("Please provide a valid link after the command. For example, `/mkv https://example.com`", quote=True)
    except Exception as e:
        # When an error occurs during the processing of the link
        message.reply_text(f"An error occurred while processing the link: {e}", quote=True)


# Start the bot
app.run()
