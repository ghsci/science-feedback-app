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

# --- Hints for Guided Learning ---
HINTS = {
    "Light": [
        "**Step 1: Preparation** - Before you start, how can you be sure any starch you find was made *during* the experiment? What's the essential first step?",
        "**Step 2: Setting up the Test** - To make it a fair test, you need to compare a part of the plant that gets light with a part that doesn't. How could you achieve this on a single leaf?",
        "**Step 3: Running the Experiment** - Now that your test is set up, what condition does the plant need to photosynthesize? For how long should you provide this condition?",
        "**Step 4: Checking the Result** - What is the final chemical test you need to perform to see if starch was made?"
    ],
    "Carbon Dioxide": [
        "**Step 1: Preparation** - Just like the other experiments, what's the crucial first step to ensure your results are valid and not from pre-existing starch?",
        "**Step 2: Setting up the Test** - You need one leaf with carbon dioxide and one without. What chemical can absorb CO₂ from the air? How can you isolate the air around the leaves?",
        "**Step 3: Running the Experiment** - After setting up your two conditions, what does the plant need to start photosynthesizing? How long should you wait?",
        "**Step 4: Checking the Result** - How will you check both leaves for the presence of starch at the end?"
    ],
    "Chlorophyll": [
        "**Step 1: Preparation** - What must you do to the plant before starting the experiment to ensure a fair test?",
        "**Step 2: Setting up the Test** - For this experiment, you need a leaf that already has a 'test' and a 'control' built-in. What special type of leaf has both green and non-green parts?",
        "**Step 3: Running the Experiment** - Once prepared, what single condition does this special plant need to begin photosynthesizing?",
        "**Step 4: Checking the Result** - What is the final procedure to check for starch in both the green and the non-green areas of the leaf?"
    ]
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

# Step 2: Procedure Input with Hints
st.markdown("**2. Write your procedure below:**")

with st.expander("Stuck? Click here for some hints!"):
    st.markdown("Read these questions to help you think about the necessary steps.")
    # Display hints for the selected experiment
    for hint in HINTS[selected_experiment_key]:
        st.markdown(f"- {hint}")

student_procedure = st.text_area(
    "Enter your procedure here:",
    height=250,
    placeholder="Describe the procedure step by step...",
    label_visibility="collapsed"
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
                
                system_prompt = """You are an expert S.2 Integrated Science teacher's assistant. Your goal is not to give the answers, but to guide students to think like scientists.

**Your Method:**
When a student's procedure has a weakness (a missing step, a vague description, or a lack of specific conditions), you will:
1.  Acknowledge what they got right.
2.  Point out the area for improvement.
3.  Ask a guiding question that makes them think about the **purpose** of that step or detail.
4.  Avoid giving the direct answer. Instead, prompt them to think about 'why'.

**Example Feedback:**
- If a student forgets to destarch, DO NOT say "You forgot to destarch." INSTEAD, ask: "You've missed an important first step. **Think about this:** How can we be sure that any starch we find at the end was made *during* the experiment, and wasn't already there? What must we do to the plant *before* we start?"
- If a student says "cover a leaf", DO NOT say "Cover only part of the leaf." INSTEAD, ask: "You mentioned covering a leaf. Good! But for this to be a fair test, we need something to compare it with. **Consider:** How could you use just *one leaf* to test a part that gets light against a part that doesn't?"
- If a student forgets a time, DO NOT say "You need to leave it for 4 hours." INSTEAD, ask: "You mentioned putting the plant in the sun. Correct! But a good scientific procedure needs specifics. **Think about this:** How long should it be in the sun? Why is it important to state a clear, specific time?"

**Output Format:**
- Be concise and use simple bullet points.
- Start with '### Well Done' for positive reinforcement.
- Start the next section with '### Areas for Improvement' for your guided questions."""
                
                # Prepare the user query
                model_procedure_text = MODEL_PROCEDURES[selected_experiment_key]["procedure"]
                user_query = f"**Model Procedure:**\n{model_procedure_text}\n\n---\n\n**Student's Procedure:**\n{student_procedure}"

                # Initialize the model with the system prompt
                model = genai.GenerativeModel(
                    'gemini-2.0-flash',
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

