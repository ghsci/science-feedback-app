import streamlit as st
import google.generativeai as genai
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="Science Procedure Feedback Assistant",
    page_icon="🧪",
    layout="centered"
)

# --- Model Procedures ---
# This data is stored in a dictionary for easy access.
MODEL_PROCEDURES = {
    "Light": {
        "full_name": "Investigation: Light is necessary for photosynthesis",
        "procedure": """1. Destarch a potted plant by putting it in the dark for 1 or 2 days.
2. Cut off a leaf and do an iodine test to ensure that the plant is destarched.
3. Cover part of a leaf from the plant with aluminium foil.
4. Put the potted plant under bright light for 4 hours.
5. Cut off the leaf and remove the aluminium foil. Do an iodine test.
6. Record the colour change of the leaf."""
    },
    "Carbon Dioxide": {
        "full_name": "Investigation: Carbon dioxide is necessary for photosynthesis",
        "procedure": """1. Destarch a potted plant by putting it in the dark for 1 or 2 days.
2. Cut off a leaf and do an iodine test to ensure that the plant is destarched.
3. Choose two leaves of similar size on the plant. Put a transparent plastic bag around each of them. In one of the bags, put a few pieces of soda lime granules.
4. Put the potted plant under bright light for 4 hours.
5. Cut off the two leaves from the plant and do an iodine test.
6. Record the colour change of the leaf."""
    },
    "Chlorophyll": {
        "full_name": "Investigation: Chlorophyll is necessary for photosynthesis",
        "procedure": """1. Destarch a potted plant with variegated leaves by putting it in the dark for 1 or 2 days.
2. Cut off a variegated leaf and do an iodine test to ensure that the plant is destarched.
3. Put the potted plant under bright light for 4 hours.
4. Cut off a variegated leaf from the plant and do an iodine test.
5. Record the colour change of the leaf."""
    }
}

# --- Main App Interface ---
st.title("🧪 Scientific Procedure Feedback Assistant")
st.markdown("Get instant, AI-powered feedback on your experimental procedures for S.2 Integrated Science.")

# Step 1: Experiment Selection
experiment_options = list(MODEL_PROCEDURES.keys())
selected_experiment_key = st.selectbox(
    "**1. Choose your experiment:**",
    options=experiment_options,
    format_func=lambda key: MODEL_PROCEDURES[key]["full_name"]
)

# Step 2: Procedure Input
student_procedure = st.text_area(
    "**2. Enter your procedure below:**",
    height=250,
    placeholder="Describe the procedure step by step..."
)

# Step 3: Feedback Button
if st.button("Get Feedback", type="primary"):
    # Input validation
    if not student_procedure.strip():
        st.warning("Please enter your procedure before getting feedback.", icon="⚠️")
    elif 'google_api_key' not in st.secrets:
        st.error("API Key not found. Please ask your teacher to configure the application's secrets.", icon="🚨")
    else:
        try:
            # --- AI Feedback Generation ---
            with st.spinner("Analyzing your procedure... Please wait."):
                # Configure the Gemini model
                genai.configure(api_key=st.secrets["google_api_key"])
                
                system_prompt = """You are a helpful S.2 Integrated Science teacher's assistant. Your task is to give feedback on a student's written procedure.
    
**IMPORTANT: Be very concise and use simple bullet points.** Students find long text difficult to read. Get straight to the point.

The feedback must be structured in two sections:
1.  **Well Done:** Briefly mention 1-2 things the student did correctly. Start this section with '### Well Done'.
2.  **Areas for Improvement:** Give specific, numbered suggestions for improvement based on the model procedure. Start this section with '### Areas for Improvement'."""
                
                # Prepare the user query
                model_procedure_text = MODEL_PROCEDURES[selected_experiment_key]["procedure"]
                user_query = f"**Model Procedure:**\n{model_procedure_text}\n\n---\n\n**Student's Procedure:**\n{student_procedure}"

                # Initialize the model with the system prompt
                model = genai.GenerativeModel(
                    'gemini-2.5-flash-preview-05-20',
                    system_instruction=system_prompt
                )

                # Generate content
                response = model.generate_content(
                    user_query,
                    generation_config=genai.types.GenerationConfig(temperature=0.7)
                )
                
                feedback_text = response.text

            # --- Display Feedback ---
            st.divider()
            st.subheader("💡 Your Feedback")

            # Use regex to split the feedback into sections for styling
            well_done_match = re.search(r"### Well Done([\s\S]*?)### Areas for Improvement", feedback_text)
            improvement_match = re.search(r"### Areas for Improvement([\s\S]*)", feedback_text)

            if well_done_match:
                st.success("**What you did well:**", icon="✅")
                st.markdown(well_done_match.group(1).strip())

            if improvement_match:
                st.info("**How you can improve:**", icon="📝")
                st.markdown(improvement_match.group(1).strip())
            
            if not well_done_match and not improvement_match:
                 st.markdown(feedback_text)


        except Exception as e:
            st.error(f"An error occurred while getting feedback: {e}", icon="🚨")

