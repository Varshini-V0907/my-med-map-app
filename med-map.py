import streamlit as st
import csv
import os
import hashlib

# --- Security and data storage ---

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def save_user_data(username, password, role):
    hashed_pwd = hash_password(password)
    with open('users.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed_pwd, role])

def verify_user(username, password):
    hashed_pwd = hash_password(password)
    if not os.path.exists('users.csv'):
        return None
    with open('users.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username and row[1] == hashed_pwd:
                return row[2]  # return role
    return None

def save_token(token):
    with open('user_token.bin', 'wb') as file:
        file.write(token)

def read_token():
    if not os.path.exists('user_token.bin'):
        return None
    with open('user_token.bin', 'rb') as file:
        return file.read()

# --- Accessibility and Localization ---

def set_accessibility_settings():
    st.sidebar.header('Accessibility Settings')
    voice = st.sidebar.checkbox('Voice Mode')
    contrast = st.sidebar.checkbox('High Contrast Mode')
    large_font = st.sidebar.checkbox('Large Font Mode')
    return voice, contrast, large_font

def apply_accessibility_css(contrast, large_font):
    if contrast:
        st.markdown(
            """
            <style>body {background-color: #000; color: #fff;}</style>
            """, unsafe_allow_html=True)
    if large_font:
        st.markdown(
            """
            <style>body {font-size: 22px;}</style>
            """, unsafe_allow_html=True)

languages = ['English', 'Tamil', 'Hindi', 'Telugu']
symptoms = ['Fever', 'Headache', 'Cough', 'Chest Pain', 'Nausea', 'Dizziness']

# --- Mock Patient Triage Data ---
triage_cases = [
    {'name':'John Smith', 'age':38, 'status':'New', 'urgency':'High', 'notes':'Chest pain, shortness of breath, dizziness for past hour.'},
    {'name':'Jane Doe', 'age':45, 'status':'In Review', 'urgency':'Medium', 'notes':'High fever (103F), persistent cough, aches.'},
    {'name':'Emily White', 'age':29, 'status':'Awaiting Action', 'urgency':'High', 'notes':'Abdominal pain, nausea for two days.'},
    {'name':'Carlos Garcia', 'age':52, 'status':'New', 'urgency':'Low', 'notes':'Mild headache, fatigue, minor joint pain.'},
    {'name':'Aisha Khan', 'age':67, 'status':'In Review', 'urgency':'Medium', 'notes':'Sudden confusion, slurred speech.'},
]

# --- Main App ---

st.title("AI Health Triage for All")

voice_mode, high_contrast_mode, large_font_mode = set_accessibility_settings()
apply_accessibility_css(high_contrast_mode, large_font_mode)

username = st.text_input('Username')
password = st.text_input('Password', type='password')

col1, col2 = st.columns(2)
with col1:
    if st.button('Sign up'):
        role_option = st.selectbox('Select role for sign up:', ['Patient', 'Health Worker'])
        save_user_data(username, password, role_option)
        st.success('User registered successfully! Please sign in.')

with col2:
    if st.button('Sign in'):
        user_role = verify_user(username, password)
        if user_role:
            st.success(f'Signed in as {user_role} successfully!')
            save_token(b'user_logged_in_token')
            st.session_state['role'] = user_role
        else:
            st.error('Invalid username or password.')

if read_token() == b'user_logged_in_token':
    role = st.session_state.get('role', 'Patient')
    st.write(f"You are signed in as: *{role}*")

    # Language selection
    st.subheader("Select Your Language")
    lang = st.radio("Preferred language:", languages)

    # Role-based UI
    if role == 'Patient':
        st.subheader("Select Your Symptoms - Step 1 of 4")
        selected_symptoms = st.multiselect("Please select all symptoms that apply:", symptoms)
        if st.button("Next"):
            st.write("Analyzing your symptoms...")
            urgency = st.slider("Potential urgency level", 0, 100, 50)
            if urgency < 40:
                st.success("Normal urgency")
            elif urgency < 70:
                st.warning("Moderate urgency")
            else:
                st.error("Critical urgency")

        st.subheader("Health Services")
        st.button("Find Doctor")
        st.button("First Aid")
        st.button("Hygiene & Cleanliness")
        st.button("Maternal Health")
        st.button("Child Vaccinations")
        st.button("Nutrition Info")

    elif role == 'Health Worker':
        st.subheader("Patient Triage Management")
        status_filter = st.selectbox("Filter by case status", ['All', 'New', 'In Review', 'Awaiting Action'])
        urgency_sort = st.checkbox("Sort by urgency")

        filtered_cases = triage_cases
        if status_filter != 'All':
            filtered_cases = [c for c in filtered_cases if c['status'] == status_filter]

        if urgency_sort:
            urgency_order = {'High': 1, 'Medium': 2, 'Low': 3}
            filtered_cases.sort(key=lambda c: urgency_order.get(c['urgency'], 4))

        for case in filtered_cases:
            st.markdown(f"{case['name']}, {case['age']} - Status: {case['status']} - Urgency: {case['urgency']}")
            st.write(f"Notes: {case['notes']}")
            if st.button(f"Mark {case['name']} as Treated"):
                st.success(f"{case['name']} marked as treated")

    # Simple voice input UI simulation
    st.subheader("Voice Input Mode" if voice_mode else "")
    if voice_mode:
        if st.button("Start Recording"):
            st.info("Voice recording started... (simulation)")
        if st.button("Stop Recording"):
            st.info("Voice recording stopped.")

else:
    st.info("Please sign in to continue.")
