import streamlit as st
import torch
from transformers import (
    VisionEncoderDecoderModel, 
    ViTImageProcessor, 
    AutoTokenizer,
    AutoModelForCausalLM,
)
from PIL import Image

# Load models and tokenizers
@st.cache_resource
def load_models():
    image_processor = ViTImageProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    caption_model = VisionEncoderDecoderModel.from_pretrained("Salesforce/blip-image-captioning-base")
    caption_tokenizer = AutoTokenizer.from_pretrained("Salesforce/blip-image-captioning-base")
    
    phi_tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-128k-instruct", trust_remote_code=True)
    phi_model = AutoModelForCausalLM.from_pretrained(
        "microsoft/Phi-3-mini-128k-instruct",
        torch_dtype=torch.float16,
        trust_remote_code=True
    )
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    caption_model.to(device)
    phi_model.to(device)
    
    return (image_processor, caption_model, caption_tokenizer, phi_tokenizer, phi_model)

def generate_initial_caption(image, image_processor, model, tokenizer):
    pixel_values = image_processor(image, return_tensors="pt").pixel_values.to(model.device)
    output_ids = model.generate(pixel_values, max_length=30, num_beams=4, return_dict_in_generate=True).sequences
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)

def generate_instagram_caption(initial_caption, phi_tokenizer, phi_model):
    prompt = f"generate one instagram post caption for image description: {initial_caption}"
    inputs = phi_tokenizer(prompt, return_tensors="pt", add_special_tokens=True)
    inputs['attention_mask'] = (inputs['input_ids'] != phi_tokenizer.pad_token_id).long()
    
    inputs = {k: v.to(phi_model.device) for k, v in inputs.items()}
    
    outputs = phi_model.generate(
        **inputs,
        max_length=200,
        num_beams=4,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        pad_token_id=phi_tokenizer.pad_token_id
    )
    
    return phi_tokenizer.decode(outputs[0], skip_special_tokens=True)

st.title('PicTunes')
st.text('Your AI-Powered Creative Partner for Instagram Posts.')

if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False

if not st.session_state.model_loaded:
    with st.spinner('Loading models...'):
        models = load_models()
        (st.session_state.image_processor, 
         st.session_state.caption_model,
         st.session_state.caption_tokenizer,
         st.session_state.phi_tokenizer,
         st.session_state.phi_model) = models
        st.session_state.model_loaded = True

uploaded_file = st.file_uploader(label='Upload Image', type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        with st.spinner('Generating initial caption...'):
            initial_caption = generate_initial_caption(
                image,
                st.session_state.image_processor,
                st.session_state.caption_model,
                st.session_state.caption_tokenizer
            )
            st.write("### Initial Caption:")
            st.text(initial_caption)

            with st.spinner('Generating Instagram caption...'):
                instagram_caption = generate_instagram_caption(
                    f'Generate one instagram post caption for image description {initial_caption}',
                    st.session_state.phi_tokenizer,
                    st.session_state.phi_model
                )

            st.write("### Generated Instagram Caption:")
            st.text(instagram_caption)

            st.success('Done!')
            st.balloons()

    except Exception as e:
        st.error(f'Error processing image: {str(e)}')

st.divider()
st.text("Created by Sushant Garudkar | Powered by AI")
