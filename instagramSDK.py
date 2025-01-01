from instabot import Bot
import os
import tempfile

def init_instagram_bot(username, password):
    """Initialize Instagram bot with credentials"""
    bot = Bot()
    bot.login(username=username, password=password)
    return bot

def post_to_instagram(bot, image, caption, music):
    """Post image with caption and music to Instagram"""
    # Create temporary file for the image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        image.save(tmp_file, format='JPEG')
        tmp_file_path = tmp_file.name
    
    # Format caption with music
    full_caption = f"{caption}\n\n🎵 Current Mood: {music}\n\n"
    
    # Post to Instagram
    success = bot.upload_photo(tmp_file_path, caption=full_caption)
    
    # Clean up temporary file
    os.unlink(tmp_file_path)
    
    return success