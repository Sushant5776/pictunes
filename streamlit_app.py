import streamlit as st
import anthropic
from PIL import Image
import io
from auth import init_auth, login_user, register_user, logout_user
from config import load_config
from image_processing import generate_caption_and_music
from instagramSDK import init_instagram_bot, post_to_instagram

# Initialize authentication state
init_auth()

# Authentication UI
def show_auth_ui():
    st.title("PicTunes Authentication")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if login_user(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            api_key = st.text_input("Anthropic API Key", type="password")
            submit = st.form_submit_button("Register")
            
            if submit:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not new_username or not new_password or not api_key:
                    st.error("All fields are required")
                else:
                    success, message = register_user(new_username, new_password, api_key)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

def main_app():
    # Initialize Anthropic client if not already initialized
    if st.session_state.client is None:
        config = load_config()
        api_key = config['users'][st.session_state.username]['api_key']
        st.session_state.client = anthropic.Client(api_key=api_key)
    
    st.title('PicTunes')
    st.text('Your AI-Powered Creative Partner for Instagram Posts')
    
    # Sidebar
    with st.sidebar:
        st.success(f"Welcome, {st.session_state.username}!")
        st.info("ℹ️ Using Claude 3 Sonnet (~$0.001 per image)")

        # Instagram login section
        st.subheader("Instagram Connection")
        with st.expander("Connect Instagram"):
            insta_username = st.text_input("Instagram Username", type="default")
            insta_password = st.text_input("Instagram Password", type="password")
            if st.button("Connect"):
                try:
                    st.session_state.insta_bot = init_instagram_bot(insta_username, insta_password)
                    st.success("Connected to Instagram!")
                except Exception as e:
                    st.error(f"Instagram connection failed: {str(e)}")

        if st.button("Logout"):
            logout_user()
            st.rerun()
    
    # Create a placeholder for the image
    image_placeholder = st.empty()

    # File uploader
    uploaded_file = st.file_uploader(label='Upload Image', type=['png', 'jpg', 'jpeg'])

    if uploaded_file is None:
        # Display placeholder image
        placeholder_img = Image.new('RGB', (600, 400), color='lightgray')
        img_byte_arr = io.BytesIO()
        placeholder_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        image_placeholder.image(img_byte_arr, caption='No image uploaded', use_container_width=True)
    else:
        try:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            image_placeholder.image(image, caption='Uploaded Image', use_container_width=True)

            # Generate caption and music suggestion
            with st.spinner('Analyzing your image...'):
                caption, music = generate_caption_and_music(st.session_state.client, image)

            # Display the caption
            st.write("### Post Caption ✍️")
            caption_container = st.container()
            with caption_container:
                st.text_area("Caption", caption, height=150, key="caption_text")

            # Display music suggestion
            st.write("### Vibe Check 🎵")
            st.info(f"{music}")

            # Instagram posting section
            st.write("### Share to Instagram")
            if 'insta_bot' in st.session_state and st.session_state.insta_bot:
                if st.button("🚀 Post to Instagram"):
                    with st.spinner("Posting to Instagram..."):
                        if post_to_instagram(st.session_state.insta_bot, image, caption, music):
                            st.success("Posted successfully to Instagram!")
                            st.balloons()
                        else:
                            st.error("Failed to post to Instagram. Please try again.")
            else:
                st.warning("Please connect your Instagram account in the sidebar to enable posting.")

            st.success('Processing complete!')

        except Exception as e:
            st.error(f'Error processing image: {str(e)}')
            st.write("Full error details:", str(e))

    st.divider()
    st.text("Created by Sushant Garudkar | Powered by Anthropic Claude")

# Main execution
if not st.session_state.authenticated:
    show_auth_ui()
else:
    main_app()