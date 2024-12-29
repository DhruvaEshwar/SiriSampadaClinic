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

# Initialize session state
if "language" not in st.session_state:
    st.session_state.language = "en"
if "page" not in st.session_state:
    st.session_state.page = "Home"
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

# Firebase Helpers
def save_appointment(date, parent_name, phone, address, num_children, child_details, slot, token):
    db.collection("appointments").document(token).set({
        "date": date,
        "parent_name": parent_name,
        "phone": phone,
        "address": address,
        "num_children": num_children,
        "child_details": child_details,
        "slot": slot,
        "token": token,
        "created_at": datetime.now()
    })

def get_appointments_on_date(date):
    return [app.to_dict() for app in db.collection("appointments").where("date", "==", date).stream()]

# Function to get available slots (add this definition)
def get_available_slots(date):
    # Example slots
    return ["10:00 AM", "11:00 AM", "12:00 PM", "02:00 PM", "03:00 PM", "04:00 PM"]

# Pages
def home_page():
    render_sidebar()

    # Translate buttons at the top
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

    import streamlit as st
    from datetime import datetime

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
        appointments = get_appointments_on_date(date)  # Fetch appointments for the selected date
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
            st.markdown(f"**Appointment Date: {date} | Time: {datetime.now().strftime('%I:%M %p')}**")

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

def booking_page():
    render_sidebar()

    if st.session_state.language == "en":
        st.title("Book Appointment")
        st.header("Fill in the details below to book an appointment.")
    else:
        st.title("ನೇಮಕಾತಿ ಬುಕ್ ಮಾಡಿ")
        st.header("ನೀವು ನಿಗದಿಗೆ ಇತರೆ ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ.")

    # Appointment Date Selection
    appointment_date = st.date_input("Select Appointment Date" if st.session_state.language == "en" else "ನಿಗದಿ ದಿನಾಂಕ ಆಯ್ಕೆಮಾಡಿ")

    # Get available slots based on the selected date
    available_slots = get_available_slots(appointment_date)

    # If there are no available slots, show a message
    if not available_slots:
        if st.session_state.language == "en":
            st.warning("No slots available for the selected date.")
        else:
            st.warning("ಆಯ್ಕೆಮಾಡಿದ ದಿನಾಂಕಕ್ಕೆ ಯಾವುದೇ ಸಮಯ ಸ್ಲಾಟುಗಳು ಲಭ್ಯವಿಲ್ಲ.")
    else:
        # Select an available slot
        slot = st.selectbox("Select Time Slot" if st.session_state.language == "en" else "ಸಮಯ ಸ್ಲಾಟು ಆಯ್ಕೆಮಾಡಿ", available_slots)

        # Enter personal details
        parent_name = st.text_input("Parent's Name" if st.session_state.language == "en" else "ಹೆತ್ತವರ ಹೆಸರು")
        phone = st.text_input("Phone Number" if st.session_state.language == "en" else "ಫೋನ್ ಸಂಖ್ಯೆ")
        address = st.text_area("Address" if st.session_state.language == "en" else "ವಿಳಾಸ")

        # Child details
        num_children = st.number_input("Number of Children" if st.session_state.language == "en" else "ಮಕ್ಕಳ ಸಂಖ್ಯೆ", min_value=1, max_value=10)
        child_details = []
        for i in range(num_children):
            with st.expander(f"Child {i + 1} Details" if st.session_state.language == "en" else f"ಮಕ್ಕಳು {i + 1} ವಿವರಗಳು"):
                child_name = st.text_input(f"Name of Child {i + 1}" if st.session_state.language == "en" else f"ಮಕ್ಕಳು {i + 1} ಹೆಸರು")
                child_age = st.number_input(f"Age of Child {i + 1}" if st.session_state.language == "en" else f"ಮಕ್ಕಳು {i + 1} ವಯಸ್ಸು", min_value=0, max_value=18)
                child_disease = st.text_area(f"Disease (if any) for Child {i + 1}" if st.session_state.language == "en" else f"ಮಕ್ಕಳು {i + 1} ರೋಗ (ಇಲ್ಲಿ ಇವಿದ್ದರೆ)")
                if child_name:
                    child_details.append({"name": child_name, "age": child_age, "disease": child_disease})

        # Generate unique token for the appointment
        token = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Submit the booking
        if st.button("Book Appointment" if st.session_state.language == "en" else "ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಬುಕ್ ಮಾಡಿ", key="book_appointment_button"):

            if parent_name and phone and address and num_children > 0 and child_details:
                # Save appointment details in Firestore
                save_appointment(appointment_date, parent_name, phone, address, num_children, child_details, slot, token)
                if st.session_state.language == "en":
                    st.success(f"Appointment booked successfully! Token: {token}")
                else:
                    st.success(f"ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಯಶಸ್ವಿಯಾಗಿ ಬುಕ್ ಮಾಡಲಾಗಿದೆ! ಟೋಕನ್: {token}")
            else:
                if st.session_state.language == "en":
                    st.error("Please fill all the details before submitting.")
                else:
                    st.error("ದಯವಿಟ್ಟು ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ಪೂರ್ತಿಗೊಳಿಸಿ.")

# Main page routing
if st.session_state.page == "Home":
    home_page()
elif st.session_state.page == "Book Appointment":
    booking_page()
elif st.session_state.page == "Prescription Entry":
    prescription_page()
