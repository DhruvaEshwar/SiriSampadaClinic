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
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Initialize session state variables if they don't exist
if "language" not in st.session_state:
    st.session_state.language = "en"  # Set default language
if "page" not in st.session_state:
    st.session_state.page = "Home"  # Set default page

if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

# Sidebar
def toggle_sidebar():
    st.session_state.sidebar_open = not st.session_state.sidebar_open

def render_sidebar():
    with st.sidebar:
        st.button("Home", on_click=lambda: setattr(st.session_state, "page", "Home"))
        st.button("Book Appointment", on_click=lambda: setattr(st.session_state, "page", "Book Appointment"))
        st.button("Prescription Entry", on_click=lambda: setattr(st.session_state, "page", "Prescription Entry"))
        st.session_state.language = st.radio("Language", ["en", "kn"], index=["en", "kn"].index(st.session_state.language))

def save_appointment(date, parent_name, phone, address, num_children, child_details, slot, token=None):
    # Use date as the document name (YYYY-MM-DD format)
    date_str = date.strftime('%Y-%m-%d')
    appointment_ref = db.collection("appointments").document(date_str)

    # Get existing appointments for the date (if any)
    existing_appointments = appointment_ref.get()
    if existing_appointments.exists:
        appointments = existing_appointments.to_dict()['appointments']
    else:
        appointments = []

    # If token is not provided, generate it based on existing appointments
    if token is None:
        token = len(appointments) + 1

    # Append new appointment
    appointment_data = {
        "parent_name": parent_name,
        "phone": phone,
        "address": address,
        "num_children": num_children,
        "child_details": child_details,
        "slot": slot,
        "created_at": datetime.now(),
        "token": token
    }
    appointments.append(appointment_data)

    # Save the updated appointments list under the date
    appointment_ref.set({
        "appointments": appointments
    })


def get_available_slots(date):
    # Define time slots (morning and evening)
    time_slots = [
        "08:00 AM", "08:30 AM", "09:00 AM", "09:30 AM",
        "06:00 PM", "06:30 PM", "07:00 PM", "07:30 PM", "08:00 PM", "08:30 PM"
    ]

    # Fetch all appointments for the selected date
    date_str = date.strftime('%Y-%m-%d')
    appointment_ref = db.collection("appointments").document(date_str)
    appointment_data = appointment_ref.get()

    if appointment_data.exists:
        # Get the existing appointments
        appointments = appointment_data.to_dict().get('appointments', [])
    else:
        appointments = []

    # Count the number of appointments for each time slot
    slot_counts = {slot: 0 for slot in time_slots}
    for appointment in appointments:
        slot = appointment.get("slot")
        if slot in slot_counts:
            slot_counts[slot] += 1

    # Filter out fully booked slots (more than or equal to 10 appointments)
    available_slots = [slot for slot, count in slot_counts.items() if count < 10]

    return available_slots



# Pages
def home_page():
    render_sidebar()
    # Add home page content here
    if st.session_state.language == "en":
        st.button("Translate to Kannada / ಕನ್ನಡಕ್ಕೆ ಭಾಷಾಂತರಿಸಿ", on_click=lambda: setattr(st.session_state, "language", "kn"))
    else:
        st.button("Translate to English / ಇಂಗ್ಲೀಷ್‌ಗೆ ಭಾಷಾಂತರಿಸಿ", on_click=lambda: setattr(st.session_state, "language", "en"))

    if st.session_state.language == "en":
        st.title("Welcome to Siri Sampada Child Care Clinic")
        st.header("Siri Sampada Child Care Clinic")
        st.write("**Phone no. :** 097428 52267")
        st.image("clinic_image_1.jpg", caption="Inside of the Clinic", use_container_width=True)
        st.image("clinic_image_2.jpg", caption="Outside of the Clinic", use_container_width=True)
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
        st.subheader("Location")
        st.markdown("""
            <a href="https://www.google.com/maps?q=Siri+Sampada+Child+Care+Clinic,+2nd+Cross+Rd,+Ashok+Nagar,+Mandya,+Karnataka+571401&hl=en" target="_blank">
                <button style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; cursor:pointer;">
                    View on Google Maps
                </button>
            </a>
        """, unsafe_allow_html=True)
        st.write("**Address:** 2nd Cross Rd, Ashok Nagar, Mandya, Karnataka 571401")
    else:
        st.title("ಸಿರಿ ಸಂಪದ ಚೈಲ್ಡ್ ಕೇರ್ ಕ್ಲಿನಿಕ್‌ಗೆ ಸ್ವಾಗತ")
        st.header("ಸಿರಿ ಸಂಪದ ಚೈಲ್ಡ್ ಕೇರ್ ಕ್ಲಿನಿಕ್")
        st.write("**ಫೋನ್ ಸಂಖ್ಯೆ :** 097428 52267")
        st.image("clinic_image_1.jpg", caption="ಕ್ಲಿನಿಕ್ ಒಳಗಿನ ಚಿತ್ರ", use_container_width=True)
        st.image("clinic_image_2.jpg", caption="ಕ್ಲಿನಿಕ್ ಬಾಹ್ಯ ಚಿತ್ರ", use_container_width=True)
        st.subheader("ಡಾ. ಕೀರ್ತಿ ಬಿ. ಜಿ. ಬಗ್ಗೆ ~")
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write("""
            **ಡಾ. ಕೀರ್ತಿ ಬಿ. ಜಿ.**  
            - ಎಂ.ಡಿ. (ಪಿಡಿಯಾಟ್ರಿಕ್ಸ್), ನಿಯೋನೇಟೋಲಾಜಿ ಫೆಲೋ  
            - ನಿಯೋನೇಟೋಲಜಿಸ್ಟ್ ಮತ್ತು ಪೀಡಿಯಾಟ್ರಿಷಿಯನ್  
            - ಮಾಣ್ಡ್ಯಾ ಜಿಲ್ಲೆ ಆಸ್ಪತ್ರೆಯ ಪೀಡಿಯಾಟ್ರಿಕ್ಸ್ ಅಸೋಸಿಯೇಟ್ ಪ್ರೊಫೆಸರ್  
            """)
        with col2:
            st.image("doctor_photo.jpg", caption="ಡಾ. ಕೀರ್ತಿ ಬಿ. ಜಿ.", use_container_width=True)
        st.subheader("ಸ್ಥಳ")
        st.markdown("""
            <a href="https://www.google.com/maps?q=Siri+Sampada+Child+Care+Clinic,+2nd+Cross+Rd,+Ashok+Nagar,+Mandya,+Karnataka+571401&hl=en" target="_blank">
                <button style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; cursor:pointer;">
                    ಗೂಗಲ್ ಮ್ಯಾಪ್ಸ್‌ನಲ್ಲಿ ನೋಡಿ
                </button>
            </a>
        """, unsafe_allow_html=True)
        st.write("**ವಿಳಾಸ:** 2nd ಕ್ರಾಸ್ ರಸ್ತೆ, ಅಶೋಕ್ ನಗರ, ಮಂಡ್ಯ, ಕರ್ನಾಟಕ 571401")

def booking_page():
    render_sidebar()
    st.title("Book an Appointment")
    st.markdown("Fill in the details below to book an appointment.")

    date = st.date_input("Select Appointment Date", min_value=datetime.now().date())

    # Check if the selected date is a Sunday
    if date.weekday() == 6:  # Sunday is 6 in the weekday() method
        st.error("Appointments cannot be booked on Sundays. Please select another day.")
        return

    # Fetch available slots
    available_slots = get_available_slots(date)

    if available_slots:
        slot = st.selectbox("Select Appointment Time", available_slots)
    else:
        st.warning("No slots are available for the selected date. Please choose another day.")
        return

    # Parent details
    parent_name = st.text_input("Parent's Name")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")

    # Child details
    num_children = st.number_input("Number of Children", min_value=1, max_value=5)
    child_details = []
    for i in range(num_children):
        st.write(f"Child {i + 1}:")
        child_name = st.text_input(f"Name of Child {i + 1}")
        child_age = st.number_input(f"Age of Child {i + 1}", min_value=0, max_value=18)
        child_disease = st.text_area(f"Disease (if any) for Child {i + 1}")
        child_details.append({"name": child_name, "age": child_age, "disease": child_disease})

    if st.button("Book Appointment", key=f"book_button_{date}"):
        save_appointment(date, parent_name, phone, address, num_children, child_details, slot)
        st.success(f"Appointment booked successfully for {slot}.")



def prescription_page():
    render_sidebar()

    # Password Authentication
    password = st.text_input("Enter Password to Access Prescription Page", type="password")
    correct_password = "ssclinic"  # Updated password
    if password != correct_password:
        st.warning("Incorrect Password!")
        return

    # Select child with an appointment on that day
    date = st.date_input("Select Appointment Date")

    if date:
        # Fetch appointments for the selected date
        appointments = get_appointments_on_date(date)

        # Prepare options for selecting a child from the fetched appointments
        child_options = [
            {
                "label": f"{app['parent_name']} - {child['name']}",
                "name": child["name"],
                "age": child["age"],
            }
            for app in appointments for child in app["child_details"]
        ]

        if child_options:
            selected_child = st.selectbox(
                "Select Child for Prescription",
                [child["label"] for child in child_options]
            )

            # Fetch selected child details
            child_info = next(child for child in child_options if child["label"] == selected_child)
            st.markdown(f"### Child Name: {child_info['name']} | Age: {child_info['age']} years")
            st.markdown(f"**Appointment Date: {date}**")

            # Prescription Form
            disease = st.text_area("Enter Disease")

            # Initialize or continue the medicine data list in session state
            if "medicine_data" not in st.session_state:
                st.session_state["medicine_data"] = []

            # Medicine Input Fields
            with st.form(key="medicine_form", clear_on_submit=True):
                medicine_name = st.text_input("Medicine Name")
                dosage = st.text_input("Dosage")
                duration = st.text_input("Duration")
                timing = st.selectbox("Timing", ["Before Food", "After Food"])

                submit_button = st.form_submit_button(label="Add Medicine")

                if submit_button:
                    if medicine_name and dosage and duration:
                        st.session_state["medicine_data"].append({
                            "name": medicine_name,
                            "dosage": dosage,
                            "duration": duration,
                            "timing": timing
                        })
                        st.success(f"Added {medicine_name}")
                    else:
                        st.error("Please fill in all the details")

            # Display added medicines
            if st.session_state["medicine_data"]:
                st.write("Added Medicines:")
                for idx, med in enumerate(st.session_state["medicine_data"], 1):
                    st.write(f"{idx}. {med['name']} - {med['dosage']} - {med['duration']} - {med['timing']}")

            # Save prescription
            if st.button("Save Prescription"):
                st.success(f"Prescription Saved for {child_info['name']}")
                # Optionally save the prescription to Firestore or another database here
                st.session_state["medicine_data"] = []  # Clear the medicine data after saving

        else:
            st.warning("No appointments available for this date.")


# Main page routing
if st.session_state.page == "Home":
    home_page()
elif st.session_state.page == "Book Appointment":
    booking_page()
elif st.session_state.page == "Prescription Entry":
    prescription_page()
