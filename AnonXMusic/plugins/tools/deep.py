from pyrogram import filters, types
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultAudio
from AnonXMusic import app
import yt_dlp
import re

# Function to search YouTube using yt-dlp
def search_youtube(query):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestaudio',
        'noplaylist': False,  # Allow playlists
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search YouTube for the query
            result = ydl.extract_info(f"ytsearch5:{query}", download=False)
            if 'entries' in result:
                return result['entries']
            return []
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return []

@app.on_inline_query()
async def inline_query_handler(client, query):
    search_text = query.query.strip()
    if not search_text:
        # Return a default response if the query is empty
        results = [
            InlineQueryResultArticle(
                title="Start typing to search for songs!",
                input_message_content=InputTextMessageContent("Type a song, playlist, or radio station name after @BotName"),
                description="Search songs, playlists, or radio stations on YouTube",
                thumb_url="https://i.ytimg.com/vi/default.jpg"
            )
        ]
        await query.answer(results=results, cache_time=1)
        return

    # Perform YouTube search using yt-dlp
    youtube_results = search_youtube(search_text)
    results = []

    for item in youtube_results:
        if not item:
            continue
        title = item.get('title', 'Unknown Title')
        url = item.get('url', item.get('webpage_url', ''))
        uploader = item.get('uploader', 'Unknown Artist')
        is_playlist = item.get('playlist') is not None

        if not is_playlist:
            # Add song as InlineQueryResultAudio
            results.append(
                InlineQueryResultAudio(
                    audio_url=url,
                    title=title,
                    performer=uploader,
                    caption=f"🎵 {title} by {uploader}",
                    reply_markup=types.InlineKeyboardMarkup(
                        [
                            [
                                types.InlineKeyboardButton("Play", callback_data=f"play_{url}"),
                                types.InlineKeyboardButton("Queue", callback_data=f"queue_{url}")
                            ]
                        ]
                    )
                )
            )
        else:
            # Add playlists as articles
            results.append(
                InlineQueryResultArticle(
                    title=f"Playlist: {title}",
                    input_message_content=InputTextMessageContent(f"Check out this playlist: {title}!\nLink: {url}"),
                    description=f"Playlist by {uploader}",
                    thumb_url=item.get('thumbnail', 'https://i.ytimg.com/vi/default.jpg'),
                    reply_markup=types.InlineKeyboardMarkup(
                        [
                            [
                                types.InlineKeyboardButton("Open", url=url),
                                types.InlineKeyboardButton("Share", switch_inline_query=title)
                            ]
                        ]
                    )
                )
            )

    # Answer the inline query with results
    await query.answer(results=results, cache_time=1)

@app.on_callback_query(filters.regex(r"^(play|queue)_"))
async def callback_query_handler(client, callback_query):
    action, url = callback_query.data.split("_", 1)
    if action == "play":
        await callback_query.message.reply(f"Playing song from {url}...")
        # Add logic to play the song in your bot's context
    elif action == "queue":
        await callback_query.message.reply(f"Added {url} to queue!")
        # Add logic to queue the song
    await callback_query.answer()
