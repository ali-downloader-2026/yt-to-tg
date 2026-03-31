import os
import asyncio
import nest_asyncio
from pyrogram import Client
from yt_dlp import YoutubeDL

# یہ لائن کلاؤڈ پر ضروری ہے
nest_asyncio.apply()

# --- فائل کے نام (جو آپ GitHub پر اپلوڈ کریں گے) ---
input_file = "specific_channels_database.txt"
log_file = "uploaded_history.txt"
error_file = "failed_links.txt"

# --- آپ کی بوٹ تفصیلات ---
api_id = 2040
api_hash = "b18441a1ff607e10a989891a5462e627"
bot_token = "8452483914:AAF6ey1lmT6QrZf1Texv2iFDwJFqg2JTX9k"
chat_id = "rhkdjd52"  # اگر یہ یوزر نیم ہے تو شروع میں @ لگائیں جیسے "@rhkdjd52"

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
        print("✅ Cloud Bot Start Ho Gaya Hai...")
        
        while True:  # 24 گھنٹے چلانے کے لیے لوپ
            if not os.path.exists(input_file):
                print(f"Waiting for {input_file}...")
                await asyncio.sleep(60)
                continue

            with open(input_file, "r") as f:
                all_links = [line.strip() for line in f if line.strip()]

            uploaded_urls = set()
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    uploaded_urls = set(line.strip() for line in f)

            pending = [l for l in all_links if l not in uploaded_urls]
            
            if not pending:
                print("😴 Sab links khatam! Naye links ka intezar...")
                await asyncio.sleep(300) # 5 minut break
                continue

            print(f"🚀 Total {len(pending)} naye links par kaam ho raha hai...")

            for link in pending:
                item = await get_info(link)
                if not item: continue
                
                try:
                    ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'quiet': True}
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([item['link']])
                    
                    video_caption = f"📝 **{item['title']}**"
                    detail_text = (f"🔗 **Video URL:** {item['link']}\n"
                                 f"📺 **Channel Name:** {item['channel']}\n"
                                 f"👤 **Channel Username:** @{item['username']}\n"
                                 f"🏠 **Channel URL:** {item['channel_url']}")

                    # Upload as Document
                    await app.send_document(chat_id=chat_id, document="video.mp4", caption=video_caption)
                    # Details message
                    await app.send_message(chat_id=chat_id, text=detail_text)

                    with open(log_file, "a") as log: 
                        log.write(item['link'] + "\n")
                    
                    if os.path.exists("video.mp4"): os.remove("video.mp4")
                    print(f"✅ Successful: {item['title']}")
                    
                    # اکاؤنٹ بچانے کے لیے 30 سیکنڈ کا وقفہ
                    await asyncio.sleep(30)
                
                except Exception as e:
                    print(f"❌ Error: {e}")
                    with open(error_file, "a") as err: 
                        err.write(link + "\n")
                    await asyncio.sleep(10)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_transfer())
    
