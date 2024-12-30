import streamlit as st
import torch
from transformers import (
    VisionEncoderDecoderModel, 
    ViTImageProcessor, 
    AutoTokenizer,
    AutoModelForCausalLM,
)
from PIL import Image
import io

# Model configurations
@st.cache_resource
def load_models():
    # Load VIT-GPT2 for initial image captioning
    image_processor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    caption_model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    caption_tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    
    # Load Phi-3.5 for Instagram caption generation
    phi_tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-3.5-mini-instruct", trust_remote_code=True)
    phi_model = AutoModelForCausalLM.from_pretrained(
        "microsoft/phi-3.5-mini-instruct",
        torch_dtype=torch.float16,
        trust_remote_code=True
    )
    
    # Move models to appropriate device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    caption_model.to(device)
    phi_model.to(device)
    
    return (image_processor, caption_model, caption_tokenizer, 
            phi_tokenizer, phi_model)

def generate_initial_caption(image, image_processor, model, tokenizer):
    # Preprocess image
    pixel_values = image_processor(image, return_tensors="pt").pixel_values.to(model.device)
    
    # Generate caption
    output_ids = model.generate(
        pixel_values,
        max_length=30,
        num_beams=4,
        return_dict_in_generate=True
    ).sequences
    
    # Decode caption
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)

def generate_instagram_caption(initial_caption, phi_tokenizer, phi_model):
    prompt = f"generate one instagram post caption for image description {initial_caption}"
    
    inputs = phi_tokenizer(prompt, return_tensors="pt", add_special_tokens=True)
    inputs = {k: v.to(phi_model.device) for k, v in inputs.items()}
    
    outputs = phi_model.generate(
        **inputs,
        max_length=200,
        num_beams=4,
        temperature=0.7,
        top_p=0.9,
        pad_token_id=phi_tokenizer.pad_token_id
    )
    
    return phi_tokenizer.decode(outputs[0], skip_special_tokens=True)

def suggest_music(caption):
    # Simple mood-based music suggestion
    music_mapping = {
        'beautiful': 'Ambient Piano Melodies',
        'sunset': 'Chill Evening Beats',
        'nature': 'Forest Ambience',
        'city': 'Urban Lofi Mix',
        'beach': 'Tropical House Vibes',
        'people': 'Feel Good Pop',
        'food': 'Cafe Jazz',
        'night': 'Deep House Mix'
    }
    
    caption = caption.lower()
    for keyword, music in music_mapping.items():
        if keyword in caption:
            return music
    return 'Chill Beats Mix'  # Default suggestion

# Initialize Streamlit app
st.title('PicTunes')
st.text('Your AI-Powered Creative Partner for Instagram Posts.')

# Initialize session state
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False

# Load models
if not st.session_state.model_loaded:
    try:
        with st.spinner('Starting App'):
            models = load_models()
            (st.session_state.image_processor, 
             st.session_state.caption_model,
             st.session_state.caption_tokenizer,
             st.session_state.phi_tokenizer,
             st.session_state.phi_model) = models
            st.session_state.model_loaded = True
    except Exception as e:
        st.error(f'Error loading models: {str(e)}')
        st.stop()

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

        # Generate initial caption
        with st.spinner('Analyzing your image...'):
            initial_caption = generate_initial_caption(
                image,
                st.session_state.image_processor,
                st.session_state.caption_model,
                st.session_state.caption_tokenizer
            )
            
            # Generate Instagram caption
            instagram_caption = generate_instagram_caption(
                initial_caption,
                st.session_state.phi_tokenizer,
                st.session_state.phi_model
            )

        # Display the description
        st.write("### Generated Caption:")
        st.text(instagram_caption)

        # Generate music suggestion
        with st.spinner('Suggesting the perfect music for your post...'):
            suggested_music = suggest_music(initial_caption)

        st.write("### Music Suggestion:")
        st.info(f"🎵 {suggested_music}")

        # Show success and balloons
        st.success('Done!')
        st.balloons()

    except Exception as e:
        st.error(f'Error processing image: {str(e)}')
        st.write("Full error details:", str(e))

st.divider()
st.text("Created by Sushant Garudkar | Powered by AI")