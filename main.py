import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

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

# Sample translations dictionary
translations = {
    "home_title": {"en": "Welcome to Siri Sampada Child Care Clinic"},
    "appointment_title": {"en": "Book Appointment"},
    "sunday_warning": {"en": "Appointments cannot be booked for Sundays."},
    "time_slot": {"en": "Select a Time Slot"},
    "parent_name": {"en": "Parent's Name"},
    "phone_number": {"en": "Phone Number"},
    "address": {"en": "Address"},
    "num_patients": {"en": "Number of Patients"},
    "book_button": {"en": "Book Appointment"},
    "appointment_saved": {"en": "Appointment successfully booked with Token:"},
    "clinic_info": {"en": "Siri Sampada Child Care Clinic"}
}

# Initialize session state variables
if "language" not in st.session_state:
    st.session_state.language = "en"  # Default to English

if "page" not in st.session_state:
    st.session_state.page = "Home"

# Helper function to get available slots (mocked for demo)
def get_available_slots(date):
    return ["10:00 AM", "11:00 AM", "12:00 PM", "2:00 PM", "4:00 PM"]  # Sample slots

# Helper function to save appointments (mock implementation)
def save_appointment(date, parent_name, phone, address, num_patients, patient_details, slot, token):
    st.write(f"Saving appointment: {date}, {parent_name}, {phone}, {address}, {slot}, {token}")
    # Save to Firebase (mocked for simplicity)
    db.collection("appointments").add({
        "date": date,
        "parent_name": parent_name,
        "phone": phone,
        "address": address,
        "num_patients": num_patients,
        "patient_details": patient_details,
        "slot": slot,
        "token": token
    })

# Sidebar navigation
def navigate(page_name):
    st.session_state.page = page_name

st.sidebar.title("Navigation")
st.sidebar.button("Home", on_click=lambda: navigate("Home"))
st.sidebar.button("Book Appointment", on_click=lambda: navigate("Book Appointment"))
st.sidebar.button("Prescription Entry", on_click=lambda: navigate("Prescription Entry"))

# Pages
def home_page():
    st.title(translations["home_title"][st.session_state.language])

    # Welcome message
    st.header(translations["clinic_info"][st.session_state.language])
    st.write("**Phone no. :** 097428 52267")

    # Clinic images
    st.image("clinic_image_1.jpg", caption="Inside of the Clinic", use_container_width=True)
    st.image("clinic_image_2.jpg", caption="Outside of the Clinic", use_container_width=True)

    # About the doctor
    st.subheader("About the Doctor ~ Dr. Keerthi B. J.")
    col1, col2 = st.columns([3, 2])
    with col1:
        st.write("""
        **Dr. Keerthi B. J.**  
        - M.D. (Pediatrics), Fellow in Neonatology  
        - Neonatologist & Pediatrician  
        - Associate Professor in Pediatrics, Mandya District Hospital  
        """)
    with col2:
        st.image("doctor_photo.jpg", caption="Dr. Keerthi B. J.", use_container_width=True)

    # Location and Google Maps button
    st.subheader("Location")
    st.write("Click the button below to open the clinic location in Google Maps:")
    st.markdown("""
            <a href="https://www.google.com/maps?q=Siri+Sampada+Child+Care+Clinic,+2nd+Cross+Rd,+Ashok+Nagar,+Mandya,+Karnataka+571401&hl=en" target="_blank">
                <button style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; cursor:pointer;">
                    View on Google Maps
                </button>
            </a>
        """, unsafe_allow_html=True)

    # Address and phone
    st.write("**Address:** 2nd Cross Rd, Ashok Nagar, Mandya, Karnataka 571401")

def appointment_page():
    st.title(translations["appointment_title"][st.session_state.language])
    st.markdown("Fill in the details below to book an appointment.")

    today = datetime.now().date()

    # Create a list of available dates excluding Sundays
    available_dates = [today + timedelta(days=i) for i in range(7)]
    available_dates = [date for date in available_dates if date.weekday() != 6]  # Remove Sundays

    date = st.date_input("Select Appointment Date", min_value=available_dates[0], max_value=available_dates[-1])
    if date.weekday() == 6:  # 6 is Sunday
        st.warning(translations["sunday_warning"][st.session_state.language])
        return

    available_slots = get_available_slots(date)
    if not available_slots:
        st.warning("No available slots for the selected date.")
        return

    slot = st.selectbox("Select a Time Slot", available_slots)
    parent_name = st.text_input("Parent's Name")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")

    num_patients = st.number_input("Number of Patients", min_value=1, max_value=5)

    patient_details = []
    for i in range(num_patients):
        st.write(f"Details for Patient {i + 1}:")
        patient_name = st.text_input(f"Patient {i + 1} Name")
        patient_age = st.text_input(f"Patient {i + 1} Age")
        patient_details.append({"name": patient_name, "age": patient_age})

    if st.button("Book Appointment"):
        if parent_name and phone and address and all(pd["name"] and pd["age"] for pd in patient_details):
            token = f"TOKEN{datetime.now().strftime('%Y%m%d%H%M%S')}"
            save_appointment(date.strftime("%Y-%m-%d"), parent_name, phone, address, num_patients, patient_details, slot, token)
            st.success(f"Appointment successfully booked with Token: {token}")
        else:
            st.error("Please fill in all details.")

def prescription_page():
    st.title("Prescription Entry")
    st.write("This page is under construction.")

# Main function
def main():
    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Book Appointment":
        appointment_page()
    elif st.session_state.page == "Prescription Entry":
        prescription_page()

main()
