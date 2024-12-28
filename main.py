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

# Initialize session state for language and button state
if "language" not in st.session_state:
    st.session_state.language = "english"

if "translate_button_clicked" not in st.session_state:
    st.session_state.translate_button_clicked = False

# Validate doctor password
def validate_password(password):
    return password == "dse@14"

# Get available slots for booking appointments
def get_available_slots(date):
    collection = db.collection(date.strftime("%Y-%m-%d"))
    appointments = collection.stream()

    all_slots = {
        "8:00-8:30 AM": datetime.strptime("08:00", "%H:%M").time(),
        "8:30-9:00 AM": datetime.strptime("08:30", "%H:%M").time(),
        "9:00-9:30 AM": datetime.strptime("09:00", "%H:%M").time(),
        "6:00-6:30 PM": datetime.strptime("18:00", "%H:%M").time(),
        "6:30-7:00 PM": datetime.strptime("18:30", "%H:%M").time(),
        "7:00-7:30 PM": datetime.strptime("19:00", "%H:%M").time(),
        "7:30-8:00 PM": datetime.strptime("19:30", "%H:%M").time()
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

# Save appointment
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

# Get today's children with appointments
def get_children_for_today():
    today = datetime.now().strftime("%Y-%m-%d")
    collection = db.collection(today)
    appointments = collection.stream()
    children = []

    for doc in appointments:
        data = doc.to_dict()
        for patient in data["patient_details"]:
            children.append({"name": patient["name"], "age": patient["age"]})
    return children

# Save prescription
def save_prescription(name, age, disease, medicines, timing, food_timing):
    today = datetime.now().strftime("%Y-%m-%d")
    collection = db.collection(f"prescriptions_{today}")
    collection.add({
        "name": name,
        "age": age,
        "disease": disease,
        "medicines": medicines,
        "timing": timing,
        "food_timing": food_timing,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

# Home Page
def home_page():
    st.title("Siri Sampada Child Care Clinic")
    st.header("Welcome to the Clinic")
    st.write("**Phone no.:** 097428 52267")
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
    st.markdown("""
        <a href="https://www.google.com/maps?q=Siri+Sampada+Child+Care+Clinic,+2nd+Cross+Rd,+Ashok+Nagar,+Mandya,+Karnataka+571401&hl=en" target="_blank">
            <button style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; cursor:pointer;">
                View on Google Maps
            </button>
        </a>
    """, unsafe_allow_html=True)

# Appointment Page
def appointment_page():
    st.title("Book an Appointment")
    today = datetime.now().date()

    available_dates = [today + timedelta(days=i) for i in range(7)]
    available_dates = [date for date in available_dates if date.weekday() != 6]

    date = st.date_input("Select a Date", min_value=available_dates[0], max_value=available_dates[-1])

    if date.weekday() == 6:
        st.warning("Sunday is a holiday. Please select another day.")
        return

    available_slots = get_available_slots(date)
    if not available_slots:
        st.warning("No available slots for the selected date.")
        return

    slot = st.selectbox("Select Time Slot", available_slots)
    parent_name = st.text_input("Parent's Name")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")
    num_patients = st.number_input("Number of Patients", min_value=1, max_value=5)

    if st.button("Book Appointment"):
        if parent_name and phone and address:
            token = f"TOKEN{datetime.now().strftime('%Y%m%d%H%M%S')}"
            patient_details = [{"name": st.text_input("Patient Name"), "age": st.text_input("Age")} for _ in range(num_patients)]
            save_appointment(date.strftime("%Y-%m-%d"), parent_name, phone, address, num_patients, patient_details, slot, token)
            st.success(f"Appointment booked successfully! Your token number is {token}")
        else:
            st.error("Please fill in all details.")

# Prescription Page
def prescription_page():
    st.title("Prescription Entry")
    password = st.text_input("Enter Password", type="password")
    if not validate_password(password):
        st.error("Invalid password. Access denied.")
        return

    st.success("Access granted. Select a child to create a prescription.")

    children = get_children_for_today()
    if not children:
        st.info("No appointments found for today.")
        return

    selected_child = st.selectbox("Select a Child", [f"{child['name']} (Age: {child['age']})" for child in children])
    if selected_child:
        child_data = next(child for child in children if f"{child['name']} (Age: {child['age']})" == selected_child)
        st.subheader(f"Prescription for {child_data['name']} (Age: {child_data['age']})")
        disease = st.text_input("Disease/Infection")
        medicines = st.text_area("Medicines (comma-separated)")
        timing = st.text_area("Medicine Timing (e.g., Morning, Evening)")
        food_timing = st.radio("Before or After Food", ["Before Food", "After Food"])

        if st.button("Save Prescription"):
            if disease and medicines and timing and food_timing:
                save_prescription(child_data["name"], child_data["age"], disease, medicines, timing, food_timing)
                st.success("Prescription saved successfully!")
            else:
                st.error("Please fill in all fields.")

# Main App
def main():
    page = st.sidebar.selectbox("Navigation", ["Home", "Book Appointment", "Prescription Entry"])
    if page == "Home":
        home_page()
    elif page == "Book Appointment":
        appointment_page()
    elif page == "Prescription Entry":
        prescription_page()

if __name__ == "__main__":
    main()









