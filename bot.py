import os
import asyncio
import nest_asyncio
from pyrogram import Client
from yt_dlp import YoutubeDL

# Cloud compatibility
nest_asyncio.apply()

# --- Files ---
input_file = "specific_channels_database.txt"
log_file = "uploaded_history.txt"
error_file = "failed_links.txt"

# --- Credentials ---
api_id = 2040
api_hash = "b18441a1ff607e10a989891a5462e627"
bot_token = "8452483914:AAF6ey1lmT6QrZf1Texv2iFDwJFqg2JTX9k"
chat_id = "rhkdjd52" 

async def get_info(link):
    try:
        with YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(link, download=False)
            return {
                'link': link,
                'size': info.get('filesize') or info.get('filesize_approx') or 0,
                'title': info.get('title', 'N/A'),
                'channel': info.get('uploader', 'N/A'),
                'username': info.get('uploader_id', 'N/A'),
                'channel_url': info.get('uploader_url', 'N/A')
            }
    except: return None

async def start_transfer():
    app = Client("koyeb_session", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
    async with app:
        print("✅ Fast Mode Start!")
        
        while True:
            if not os.path.exists(input_file):
                print("Waiting for file...")
                await asyncio.sleep(10)
                continue

            with open(input_file, "r") as f:
                all_links = [line.strip() for line in f if line.strip()]

            uploaded_urls = set()
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    uploaded_urls = set(line.strip() for line in f)

            pending = [l for l in all_links if l not in uploaded_urls]
            
            if not pending:
                print("Done! Waiting 1 minute for new links...")
                await asyncio.sleep(60)
                continue

            for link in pending:
                item = await get_info(link)
                if not item: continue
                
                try:
                    # Fast download
                    ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'quiet': True}
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([item['link']])
                    
                    video_caption = f"📝 **{item['title']}**"
                    detail_text = (f"🔗 **URL:** {item['link']}\n"
                                 f"📺 **Channel:** {item['channel']}")

                    # Sending Document
                    await app.send_document(chat_id=chat_id, document="video.mp4", caption=video_caption)
                    await app.send_message(chat_id=chat_id, text=detail_text)

                    with open(log_file, "a") as log: 
                        log.write(item['link'] + "\n")
                    
                    if os.path.exists("video.mp4"): os.remove("video.mp4")
                    print(f"✅ Sent: {item['title']}")
                    
                    # Minimum delay to avoid ban (5 seconds)
                    await asyncio.sleep(5)
                
                except Exception as e:
                    print(f"❌ Error: {e}")
                    with open(error_file, "a") as err: 
                        err.write(link + "\n")
                    await asyncio.sleep(2)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_transfer())
                    
