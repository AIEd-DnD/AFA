import streamlit as st
from password import check_password
import student_responses  # Import your student responses page
import teacher_settings
from PIL import Image

# region <--------- Streamlit Page password --------->
# Check if the password is correct
if not check_password():
    st.stop()
# endregion <--------- Streamlit Page password -------->

# Set page configuration
st.set_page_config(page_title="Annotated Feedback Assistant", page_icon="✅", layout="wide")

# Initialize session state for modal display
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = True  # Start with modal shown

# Sidebar options for navigation
st.sidebar.title("Explore")
page = st.sidebar.selectbox("Select a page",
                             ("✅ About AFA", "⚙️ Teacher: Settings", "✏️ Student: Responses"))

def about_us_page():
    # Page title at the top
    st.title("✅ Annotated Feedback Assistant")
    # Add a subheader
    st.subheader("🔖 Getting Started")
    st.write("Teachers often struggle to find time to provide personalised feedback for students for all their assignments. On the other hand, students would benefit from more detailed feedback that pinpoints specific errors or misconceptions, helping them improve their understanding and close learning gaps.")
    
# Show the modal if it's supposed to be shown
if st.session_state.show_modal:
    with st.expander("Welcome to Annotated Feedback Assistant!", expanded=True):
        st.write("⚠️ **IMPORTANT NOTICE** ⚠️: This web application is developed as a proof-of-concept prototype. The information provided here is **NOT intended for actual usage** and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters. **Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.** Always consult with qualified professionals for accurate and personalised advice.")
        if st.button("I Agree"):
            st.session_state.show_modal = False  # Close the modal

# Load the selected page based on the session state
if not st.session_state.show_modal:
    if page == "✅ About AFA":
        about_us_page()
    elif page == "⚙️ Teacher: Settings":
        teacher_settings.app()
    elif page == "✏️ Student: Responses":
        student_responses.app()
