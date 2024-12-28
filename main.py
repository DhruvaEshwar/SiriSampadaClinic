import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta, time

# Firebase setup
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "sirisampadaclinic",
    "private_key_id": st.secrets['firebase']['private_key_id'],
    "private_key": st.secrets['firebase']['private_key'],
    "client_email": st.secrets['firebase']['client_email'],
    "client_id": st.secrets['firebase']['client_id'],
    "auth_uri": st.secrets['firebase']['auth_uri'],
    "token_uri": st.secrets['firebase']['token_uri'],
    "auth_provider_x509_cert_url": st.secrets['firebase']['auth_provider_x509_cert_url'],
    "client_x509_cert_url": st.secrets['firebase']['client_x509_cert_url'],
    "universe_domain": st.secrets['firebase']['universe_domain']
})

try:
    firebase_admin.get_app()  # Check if app is already initialized
except ValueError:
    firebase_admin.initialize_app(cred)

db = firestore.client()

if "page" not in st.session_state:
    st.session_state.page = "home"

# Language toggle functions
def translate_to_kannada():
    st.session_state.language = "kannada"

def translate_to_english():
    st.session_state.language = "english"

if "language" not in st.session_state:
    st.session_state.language = "english"  # Default language

# Language strings
translations = {
    "home_title": {
        "english": "Siri Sampada Child Care Clinic",
        "kannada": "ಸಿರಿ ಸಮ್ಪದ ಚೈಲ್ಡ್ ಕೇರ್ ಕ್ಲಿನಿಕ್"
    },
    "appointment_title": {
        "english": "Book an Appointment",
        "kannada": "ಊರಿಗಾಗಿ ನೇಮಕಾತಿ ಬುಕ್ ಮಾಡಿ"
    },
    "parent_name": {
        "english": "Parent's Name",
        "kannada": "ಪೋಷಕನ ಹೆಸರು"
    },
    "phone_number": {
        "english": "Phone Number",
        "kannada": "ದೂರವಾಣಿ ಸಂಖ್ಯೆ"
    },
    "address": {
        "english": "Address",
        "kannada": "ವಿಳಾಸ"
    },
    "num_patients": {
        "english": "Number of Patients",
        "kannada": "ರೋಗಿಯ ಸಂಖ್ಯೆಯು"
    },
    "time_slot": {
        "english": "Select Time Slot",
        "kannada": "ಸಮಯವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ"
    },
    "book_button": {
        "english": "Book Appointment",
        "kannada": "ನೇಮಕಾತಿಯನ್ನು ಬುಕ್ ಮಾಡಿ"
    },
    "appointment_saved": {
        "english": "Appointment booked successfully! Your token number is",
        "kannada": "ನೇಮಕಾತಿಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಬುಕ್ ಮಾಡಲಾಗಿದೆ! ನಿಮ್ಮ ಟೋಕನ್ ಸಂಖ್ಯೆ"
    },
    "clinic_info": {
        "english": "Welcome to Siri Sampada Child Care Clinic",
        "kannada": "ಸಿರಿ ಸಮ್ಪದ ಚೈಲ್ಡ್ ಕೇರ್ ಕ್ಲಿನಿಕ್ ಗೆ ಸ್ವಾಗತ"
    },
    "doctor_info": {
        "english": "Dr. Keerthi B. J. - M.D. (Pediatrics), Fellow in Neonatology",
        "kannada": "ಡಾ. ಕಿರ್ತಿ ಬಿ. ಜೆ - ಎಂ.ಡಿ (ಪೀಡಿಯಾಟ್ರಿಕ್ಸ್), ನಿಯೋನೆಟಾಲಾಜಿಯಲ್ಲಿ ಫೆಲೋ"
    },
    "sunday_warning": {
        "english": "Sunday is a holiday. Please select another day.",
        "kannada": "ಭಾನುವಾರದಂದು ಹೋಳಿ. ದಯವಿಟ್ಟು ಇನ್ನೊಂದು ದಿನವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ."
    },
    "prescription_access": {
        "english": "Prescription Access",
        "kannada": "ಊದವು ಪ್ರವೇಶ"
    },
    "prescription_saved": {
        "english": "Prescription saved successfully!",
        "kannada": "ಊದವು ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ!"
    }
}

# Functions for Firebase interactions
def save_appointment(date, parent_name, phone, address, num_patients, patient_details, slot, token):
    collection = db.collection(date)
    collection.add({
        "parent_name": parent_name,
        "phone": phone,
        "address": address,
        "num_patients": num_patients,
        "patient_details": patient_details,
        "slot": slot,
        "token": token,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

def get_available_slots(date):
    collection = db.collection(date.strftime("%Y-%m-%d"))
    appointments = collection.stream()

    all_slots = {
        "8:00-8:30 AM": time(8, 0),
        "8:30-9:00 AM": time(8, 30),
        "9:00-9:30 AM": time(9, 0),
        "6:00-6:30 PM": time(18, 0),
        "6:30-7:00 PM": time(18, 30),
        "7:00-7:30 PM": time(19, 0),
        "7:30-8:00 PM": time(19, 30)
    }

    current_date = datetime.now().date()
    current_time = datetime.now().time()

    if date == current_date:
        all_slots = {slot: start_time for slot, start_time in all_slots.items() if start_time > current_time}

    slot_counts = {slot: 0 for slot in all_slots}
    for doc in appointments:
        slot = doc.to_dict()["slot"]
        if slot in slot_counts:
            slot_counts[slot] += 1

    available_slots = [slot for slot, count in slot_counts.items() if count < 10]
    return available_slots

def validate_password(password):
    return password == "dse@14"

def get_children_for_today():
    today = datetime.now().strftime("%Y-%m-%d")
    collection = db.collection(today)
    appointments = collection.stream()
    children = []

    for doc in appointments:
        data = doc.to_dict()
        for patient in data["patient_details"]:
            children.append({
                "name": patient["name"],
                "age": patient["age"]
            })
    return children

# Pages
def home_page():
    st.title(translations["home_title"][st.session_state.language])
    st.image("clinic_logo.png", use_container_width=True)

    st.header(translations["clinic_info"][st.session_state.language])
    st.write("**" + translations["doctor_info"][st.session_state.language] + "**")
    st.write("**Phone no. :** 097428 52267")

    st.image("clinic_image_1.jpg", caption="Inside of the Clinic", use_container_width=True)
    st.image("clinic_image_2.jpg", caption="Outside of the Clinic", use_container_width=True)

    st.subheader("Location")
    st.write("Click the button below to open the clinic location in Google Maps:")
    st.markdown("""
        <a href="https://www.google.com/maps?q=Siri+Sampada+Child+Care+Clinic,+2nd+Cross+Rd,+Ashok+Nagar,+Mandya,+Karnataka+571401&hl=en" target="_blank">
            <button style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; cursor:pointer;">
                View on Google Maps
            </button>
        </a>
    """, unsafe_allow_html=True)

def appointment_page():
    st.title(translations["appointment_title"][st.session_state.language])
    st.markdown("Fill in the details below to book an appointment.")

    today = datetime.now().date()

    # Create a list of available dates excluding Sundays
    available_dates = [today + timedelta(days=i) for i in range(7)]
    available_dates = [date for date in available_dates if date.weekday() != 6]  # Remove Sundays

    # Select a date, but only allow available dates (i.e., excluding Sundays)
    date = st.date_input(translations["appointment_title"][st.session_state.language], min_value=available_dates[0], max_value=available_dates[-1])

    # Check if the selected date is a Sunday
    if date.weekday() == 6:  # 6 corresponds to Sunday
        st.warning(translations["sunday_warning"][st.session_state.language])
        return

    available_slots = get_available_slots(date)

    if available_slots:
        slot = st.selectbox(translations["time_slot"][st.session_state.language], available_slots)
        parent_name = st.text_input(translations["parent_name"][st.session_state.language])
        phone = st.text_input(translations["phone_number"][st.session_state.language])
        address = st.text_area(translations["address"][st.session_state.language])

        num_patients = st.number_input(translations["num_patients"][st.session_state.language], min_value=1, max_value=5)

        if st.button(translations["book_button"][st.session_state.language]):
            if parent_name and phone and address:
                token = f"TOKEN{datetime.now().strftime('%Y%m%d%H%M%S')}"
                patient_details = [{"name": st.text_input("Patient Name"), "age": st.text_input("Age")} for _ in range(num_patients)]
                save_appointment(date.strftime("%Y-%m-%d"), parent_name, phone, address, num_patients, patient_details, slot, token)
                st.success(f"{translations['appointment_saved'][st.session_state.language]} {token}")
            else:
                st.error("Please fill in all details.")

def prescription_page():
    st.title(translations["prescription_access"][st.session_state.language])

    children = get_children_for_today()
    for child in children:
        st.write(f"Name: {child['name']}, Age: {child['age']}")

    if st.button(translations["prescription_saved"][st.session_state.language]):
        st.success(translations["prescription_saved"][st.session_state.language])

# Main page selection
def home():
    if st.session_state.language == "english":
        if st.button("Translate to Kannada"):
            translate_to_kannada()
    elif st.session_state.language == "kannada":
        if st.button("Translate Back to English"):
            translate_to_english()

    page = st.selectbox("Select a page", ["Home", "Book Appointment", "Prescription Entry"])

    if page == "Home":
        home_page()
    elif page == "Book Appointment":
        appointment_page()
    elif page == "Prescription Entry":
        prescription_page()

home()





