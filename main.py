import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, time

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
        "9:30-10:00 AM": time(9, 30),
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
    st.title("Siri Sampada Child Care Clinic")
    st.image("clinic_logo.png", use_container_width=True)

    st.header("Welcome to Siri Sampada Child Care Clinic")
    st.write("**Address:** 2nd Cross Rd, Ashok Nagar, Mandya, Karnataka 571401")
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
        - Associate Professor in Pediatrics, District Hospital, Mandya  
        """)

        with col2:
            st.markdown(
                """
                <style>
                .rounded-img {
                    border-radius: 15px;
                    width: 100%;
                    max-width: 200px;
                    margin: auto;
                }
                </style>
                """, unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <img src="doctor_photo.jpg" alt="Doctor" class="rounded-img">
                """, unsafe_allow_html=True
            )


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
    st.title("Book an Appointment")
    st.markdown("Fill in the details below to book an appointment.")

    today = datetime.now().strftime("%Y-%m-%d")
    date = st.date_input("Select Date", min_value=datetime.now().date())
    available_slots = get_available_slots(date)

    if available_slots:
        slot = st.selectbox("Select Time Slot", available_slots)
    else:
        st.write("No slots available for the selected date.")
        return

    parent_name = st.text_input("Parent's Name")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")
    num_patients = st.number_input("Number of Patients", min_value=1, max_value=5, step=1)

    patient_details = []
    for i in range(num_patients):
        st.write(f"Patient {i + 1}:")
        name = st.text_input(f"Name of Patient {i + 1}")
        age = st.number_input(f"Age of Patient {i + 1}", min_value=0, max_value=18, step=1)
        patient_details.append({"name": name, "age": age})

    if st.button("Book Appointment"):
        token = len(db.collection(today).get()) + 1
        save_appointment(date.strftime("%Y-%m-%d"), parent_name, phone, address, num_patients, patient_details, slot, token)
        st.success(f"Appointment booked successfully! Your token number is {token}.")

def prescription_page():
    if "prescription_access" not in st.session_state:
        st.session_state.prescription_access = False

    if not st.session_state.prescription_access:
        st.title("Prescription Access")
        password = st.text_input("Enter the Doctor's Password", type="password")
        if st.button("Unlock"):
            if validate_password(password):
                st.session_state.prescription_access = True
                st.success("Access granted! You can now enter prescriptions.")
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

    if st.session_state.prescription_access:
        st.title("Prescription Entry")
        children = get_children_for_today()
        if not children:
            st.write("No appointments for today.")
        else:
            selected_child = st.selectbox("Select a child", [f"{child['name']} ({child['age']})" for child in children])
            selected_child_data = children[next(i for i, child in enumerate(children) if f"{child['name']} ({child['age']})" == selected_child)]

            st.write(f"**Name:** {selected_child_data['name']}")
            st.write(f"**Age:** {selected_child_data['age']}")

            disease = st.text_input("Enter Disease/Condition")
            medicine = st.text_area("Prescribed Medicines (include dosage and frequency)")
            notes = st.text_area("Additional Notes (optional)")

            if st.button("Save Prescription"):
                prescription = {
                    "name": selected_child_data["name"],
                    "age": selected_child_data["age"],
                    "disease": disease,
                    "medicine": medicine,
                    "notes": notes
                }
                st.write("Prescription saved successfully!")
with st.sidebar:
    st.title("Navigation")
    if st.button("Home"):
        st.session_state.page = "home"
        st.experimental_rerun()

    if st.button("Book Appointment"):
        st.session_state.page = "booking"
        st.experimental_rerun()

    if st.button("Prescription"):
        st.session_state.page = "prescription"
        st.experimental_rerun()

# Navigation Logic
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "booking":
    booking_page()
elif st.session_state.page == "prescription":
    prescription_page()