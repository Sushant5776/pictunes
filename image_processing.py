import streamlit as st
from PIL import Image
import io
import base64
import json

def encode_image(image):
    """Convert PIL Image to base64 string"""
    # Optimize image size before encoding
    max_size = (800, 800)  # Reasonable size for social media
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85)  # Use JPEG with good quality for smaller size
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# def generate_caption_and_music(client, image):
#     """Generate caption and music suggestion using Claude Sonnet"""
#     # Convert image to base64
#     image_base64 = encode_image(image)
    
#     # Updated system prompt with specific Indian music focus
#     system_prompt = """You are a creative assistant that understands both photography and Indian music deeply. 
#     Analyze the image and provide:
#     1. An engaging Instagram caption (2-3 sentences)
#     2. A specific Indian song suggestion that matches the mood, including:
#        - Song name
#        - Artist/Singer
#        - Movie (if applicable)
#        Choose from popular Bollywood songs, Indian pop, or classical music based on the image's mood.
#     Return as JSON: {"caption": "...", "music": {"song": "...", "artist": "...", "movie": "..." (if applicable)}}"""
    
#     # Create the message
#     messages = [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "image",
#                     "source": {
#                         "type": "base64",
#                         "media_type": "image/jpeg",
#                         "data": image_base64
#                     }
#                 },
#                 {
#                     "type": "text",
#                     "text": "Create an Instagram caption and suggest a specific Indian song that matches this image's mood."
#                 }
#             ],
#         }
#     ]
    
#     try:
#         response = client.messages.create(
#             model="claude-3-sonnet-20240229",
#             max_tokens=200,  # Increased for detailed music info
#             temperature=0.7,
#             system=system_prompt,
#             messages=messages
#         )
        
#         # Parse the response
#         result = json.loads(response.content[0].text)
        
#         # Format music suggestion
#         music_info = result['music']
#         music_text = f"{music_info['song']} - {music_info['artist']}"
#         if 'movie' in music_info and music_info['movie']:
#             music_text += f" (from '{music_info['movie']}')"
            
#         return result['caption'], music_text
#     except json.JSONDecodeError:
#         # Fallback parsing if JSON is malformed
#         text = response.content[0].text
#         try:
#             if "caption" in text.lower() and "music" in text.lower():
#                 parts = text.split('\n')
#                 caption = next((p for p in parts if 'caption' in p.lower()), "").split(':')[-1].strip()
#                 music = next((p for p in parts if 'song' in p.lower() or 'music' in p.lower()), "").split(':')[-1].strip()
#                 return caption, music
#         except:
#             pass
#         return "Error parsing response", "Tum Hi Ho - Arijit Singh (from 'Aashiqui 2')"  # Default Indian song
#     except Exception as e:
#         st.error(f"Error from Claude API: {str(e)}")
#         return "Error generating caption", "Tum Hi Ho - Arijit Singh (from 'Aashiqui 2')"  # Default Indian song

def generate_caption_and_music(client, image):
    """Generate caption, hashtags, and music suggestion using Claude Sonnet"""
    image_base64 = encode_image(image)
    
    system_prompt = """You are a creative assistant that understands both photography and Indian music deeply. 
    Analyze the image and provide:
    1. An engaging Instagram caption (2-3 sentences)
    2. 5-7 relevant hashtags
    3. A specific Indian song suggestion that matches the mood, including:
       - Song name
       - Artist/Singer
       - Movie (if applicable)
    
    Return as JSON: {
        "caption": "...",
        "hashtags": ["...", "..."],
        "music": {"song": "...", "artist": "...", "movie": "..."}
    }"""
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64
                    }
                },
                {
                    "type": "text",
                    "text": "Create an Instagram caption with hashtags and suggest a specific Indian song that matches this image's mood."
                }
            ],
        }
    ]
    
    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=300,
            temperature=0.7,
            system=system_prompt,
            messages=messages
        )
        
        result = json.loads(response.content[0].text)
        
        # Format music suggestion
        music_info = result['music']
        music_text = f"{music_info['song']} - {music_info['artist']}"
        if 'movie' in music_info and music_info['movie']:
            music_text += f" (from '{music_info['movie']}')"
        
        # Format caption with hashtags
        full_caption = f"{result['caption']}\n\n" + " ".join(result['hashtags'])
            
        return full_caption, music_text
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "Error generating caption", "Tum Hi Ho - Arijit Singh (from 'Aashiqui 2')"