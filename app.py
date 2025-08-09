import streamlit as st
import google.generativeai as genai
import os

# --- Page and API Configuration ---
st.set_page_config(
    page_title="DSCPL Spiritual Assistant",
    page_icon="✝️",
    layout="centered"
)

# Configure the Gemini API using the key from secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error configuring the Gemini API. Please check your `secrets.toml` file. Details: {e}", icon="🚨")
    st.stop()


# --- State Management ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'category' not in st.session_state:
    st.session_state.category = None
if 'topic' not in st.session_state:
    st.session_state.topic = None
# This list is now ONLY for displaying the chat history on the screen
if 'messages' not in st.session_state:
    st.session_state.messages = []
# NEW: Store the actual chat session object here
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None


# --- Main Application Flow ---

st.title("🧭 DSCPL")
st.caption("Your personal spiritual assistant.")

# ==============================================================================
# ✅ STEP 1: INITIAL SELECTION
# ==============================================================================
if st.session_state.step == 1:
    st.subheader("What do you need today?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✝️ Daily Devotion", use_container_width=True):
            st.session_state.category = "Devotion"
            st.session_state.step = 2
            st.rerun()
        if st.button("🧘 Daily Meditation", use_container_width=True):
            st.session_state.category = "Meditation"
            st.session_state.step = 2
            st.rerun()
        if st.button("💬 Just Chat", use_container_width=True):
            st.session_state.category = "Chat"
            st.session_state.step = 'program_start' # Simplified to one program step
            st.rerun()

    with col2:
        if st.button("🙏 Daily Prayer", use_container_width=True):
            st.session_state.category = "Prayer"
            st.session_state.step = 2
            st.rerun()
        if st.button("🛡️ Daily Accountability", use_container_width=True):
            st.session_state.category = "Accountability"
            st.session_state.step = 2
            st.rerun()

    st.info("The 'Watch video verses' feature is simulated in this demo by recommending video topics.", icon="🎥")

# ==============================================================================
# ✅ STEP 2: TOPIC SELECTION
# ==============================================================================
elif st.session_state.step == 2:
    st.subheader(f"Select a Topic for {st.session_state.category}")
    topics = {
        "Devotion": ["Dealing with Stress", "Overcoming Fear", "Anxiety", "Relationships", "Healing", "Purpose & Calling"],
        "Prayer": ["Personal Growth", "Healing", "Family/Friends", "Forgiveness", "Finances", "Work/Career"],
        "Meditation": ["Peace", "God's Presence", "Strength", "Wisdom", "Faith"],
        "Accountability": ["Pornography", "Alcohol", "Laziness", "Addiction", "Sex", "Drugs"]
    }
    selected_topics = topics.get(st.session_state.category, [])
    for topic in selected_topics:
        if st.button(topic, use_container_width=True):
            st.session_state.topic = topic
            st.session_state.step = 3
            st.rerun()
    if st.button("🔙 Go Back", use_container_width=True):
        st.session_state.step = 1
        st.rerun()

# ==============================================================================
# ✅ STEP 3 & 4: WEEKLY OVERVIEW & CONFIRMATION
# ==============================================================================
elif st.session_state.step == 3:
    st.subheader("Your 7-Day Spiritual Program")
    st.write(f"You've chosen **{st.session_state.category}** focusing on **{st.session_state.topic}**.")
    st.success("By the end of this week, you will feel more connected to God and confident in your journey.", icon="🌱")
    st.write("### Would you like to begin?")
    st.caption("If you proceed, this app would normally schedule daily notifications and add reminders to your Google/Apple Calendar. This functionality is simulated for the demo.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, let's begin!", use_container_width=True):
            st.session_state.step = 'program_start'
            st.rerun()
    with col2:
        if st.button("❌ No, take me back.", use_container_width=True):
            st.session_state.step = 1
            st.session_state.topic = None
            st.session_state.category = None
            st.rerun()

# ==============================================================================
# ✅ STEP 5: DAILY PROGRAM DELIVERY & CHAT (CORRECTED LOGIC)
# ==============================================================================
elif st.session_state.step == 'program_start':
    if st.session_state.category != "Chat":
        st.header(f"{st.session_state.category}: {st.session_state.topic}")
        st.markdown("---")

    # This block runs ONLY ONCE to initialize the chat
    if st.session_state.chat_session is None:
        initial_prompt = ""
        # Define the initial prompt based on user's choice
        if st.session_state.category == "Devotion":
            initial_prompt = f"You are DSCPL, a personal spiritual assistant. The user wants to start a devotional on '{st.session_state.topic}'. Begin Day 1. Follow this structure STRICTLY: 1. **Scripture**: Provide a relevant Bible verse (e.g., Philippians 4:6-7) and write out the full text. 2. **Prayer**: Write a short, related prayer. 3. **Declaration**: Write a powerful faith declaration. 4. **Video Idea**: Suggest a topic for a short video based on the scripture. Keep your entire response concise and uplifting."
        elif st.session_state.category == "Prayer":
            initial_prompt = f"You are DSCPL, a personal spiritual assistant. The user wants a guided prayer for '{st.session_state.topic}'. Guide them using the ACTS model (Adoration, Confession, Thanksgiving, Supplication). Start by explaining the model briefly and then begin with a prompt for **Adoration**."
        elif st.session_state.category == "Meditation":
            initial_prompt = f"You are DSCPL, a personal spiritual assistant. The user wants to meditate on '{st.session_state.topic}'. Guide them. Follow this structure: 1. **Scripture Focus**: Give a key scripture (e.g., Psalm 46:10). 2. **Meditation Prompts**: Ask reflective questions like 'What does this reveal about God?' and 'How can I live this out today?'. 3. **Breathing Guide**: Provide a simple breathing exercise text (e.g., 'Breathe in for 4 seconds, hold for 4, exhale for 4.')."
        elif st.session_state.category == "Accountability":
            initial_prompt = f"You are DSCPL, a personal spiritual assistant. The user needs accountability for '{st.session_state.topic}'. Provide encouragement. Follow this structure: 1. **Scripture for Strength**: Give a powerful verse. 2. **Truth Declarations**: Write an 'I am...' statement. 3. **Alternative Actions**: Suggest a healthy action to take instead of the vice. Finally, let them know they can type 'SOS' for immediate help."
        else: # Handles "Just Chat"
            initial_prompt = "You are DSCPL, a personal spiritual assistant. The user wants to chat. Greet them warmly and ask how you can support them today."

        # Start the chat session and send the initial message
        st.session_state.chat_session = model.start_chat(history=[])
        with st.spinner("Connecting to DSCPL..."):
            response = st.session_state.chat_session.send_message(initial_prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    # Display previous messages from the display list
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Handle user input
    if user_input := st.chat_input("Your message..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Use the SOS prompt if needed
                if st.session_state.category == "Accountability" and user_input.strip().upper() == "SOS":
                    prompt_to_send = f"The user triggered the SOS for '{st.session_state.topic}'. Provide an URGENT, powerful, and immediate message of encouragement, including a scripture and a direct action plan to help them in this very moment. Be direct and strong."
                    response = st.session_state.chat_session.send_message(prompt_to_send)
                    st.warning(response.text, icon="🚨")
                else:
                    response = st.session_state.chat_session.send_message(user_input)
                    st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    # Button to restart the conversation
    if st.button("↩️ Start Over"):
        st.session_state.clear()
        st.rerun()