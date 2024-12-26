import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, time

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "sirisampadaclinic",
    "private_key_id": st.secrets['firebase']['private_key_id'],
    "private_key": st.secrets['firebase']['private_key'].replace("\\n", "\n"),  # Fix line breaks
    "client_email": st.secrets['firebase']['client_email'],
    "client_id": st.secrets['firebase']['client_id'],
    "auth_uri": st.secrets['firebase']['auth_uri'],
    "token_uri": st.secrets['firebase']['token_uri'],
    "auth_provider_x509_cert_url": st.secrets['firebase']['auth_provider_x509_cert_url'],
    "client_x509_cert_url": st.secrets['firebase']['client_x509_cert_url'],
    "universe_domain": st.secrets['firebase']['universe_domain']
})

# Initialize Firebase app
try:
    firebase_admin.get_app()  # Check if app is already initialized
except ValueError:
    firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

# Function to save appointment data
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

# Function to fetch available slots
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

# Home page
def home_page():
    st.title("Siri Sampada Child Care Clinic")
    st.image("clinic_logo.png", width=900)

    st.header("Welcome to Siri Sampada Child Care Clinic")
    st.write("**Address:** 2nd Cross Rd, Ashok Nagar, Mandya, Karnataka 571401")

    st.image("clinic_image_1.jpg", caption="Inside of the Clinic", use_container_width=600)
    st.image("clinic_image_2.jpg", caption="Outside of the Clinic", use_container_width=600)

    st.subheader("About the Doctor ~ Dr. Keerti B. J.")
    st.write("""
        Dr. Keerti B. J. is a highly qualified pediatrician with extensive experience in child healthcare. 
        He holds a [MBBS, MD] degree and has been providing expert care for children for several years.
    """)

    st.subheader("Location")
    st.write("Click the button below to open the clinic location in Google Maps:")
    st.markdown("""
        <a href="https://www.google.com/maps?q=Siri+Sampada+Child+Care+Clinic,+2nd+Cross+Rd,+Ashok+Nagar,+Mandya,+Karnataka+571401&hl=en" target="_blank">
            <button style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; cursor:pointer;">
                View on Google Maps
            </button>
        </a>
    """, unsafe_allow_html=True)

    st.write("**Phone no. :** 09742852267")

# Booking page
def booking_page():
    st.title("Book an Appointment")

    # Back Button
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    # Parent details form
    with st.form(key="parent_form"):
        parent_name = st.text_input("Parent's Name")
        phone = st.text_input("Parent's Phone Number")
        address = st.text_area("Address")
        num_patients = st.selectbox("Number of Patients", [1, 2, 3, 4])

        submit_button = st.form_submit_button("Proceed to Child Details")

        if submit_button:
            if not parent_name or not phone or not address:
                st.error("Please fill in all the parent details before proceeding.")
            else:
                st.session_state.parent_data = {
                    "parent_name": parent_name,
                    "phone": phone,
                    "address": address,
                    "num_patients": num_patients
                }
                st.rerun()

    # Child details form
    if "parent_data" in st.session_state:
        parent_data = st.session_state.parent_data
        patient_details = []
        age_options = [f"{i} month" for i in range(1, 13)] + [f"{i} year" for i in range(2, 18)]

        for i in range(parent_data["num_patients"]):
            st.subheader(f"Patient {i + 1}")
            name = st.text_input(f"Child {i + 1} Name", key=f"name_{i + 1}")
            age = st.selectbox(f"Child {i + 1} Age", age_options, key=f"age_{i + 1}")
            service_type = st.selectbox(f"Service Type for Child {i + 1}", ["Consultation", "Vaccination"], key=f"service_{i + 1}")

            patient_details.append({"name": name, "age": age, "service": service_type})

        appointment_date = st.date_input("Select Appointment Date")
        slots = get_available_slots(appointment_date)

        if not slots:
            st.error("No available slots for this date. Please choose another date.")
            return

        selected_slot = st.selectbox("Available Slots", slots)

        if st.button("Submit Appointment"):
            total_cost = sum(250 if details["service"] == "Consultation" else 200 for details in patient_details)
            collection = db.collection(appointment_date.strftime("%Y-%m-%d"))
            token = len([doc for doc in collection.stream()]) + 1

            save_appointment(
                appointment_date.strftime("%Y-%m-%d"),
                parent_data["parent_name"],
                parent_data["phone"],
                parent_data["address"],
                parent_data["num_patients"],
                patient_details,
                selected_slot,
                token
            )

            st.success("Appointment booked successfully!")
            st.write(f"**Parent Name:** {parent_data['parent_name']}")
            st.write(f"**Phone:** {parent_data['phone']}")
            st.write(f"**Number of Patients:** {parent_data['num_patients']}")
            for i, details in enumerate(patient_details):
                st.write(f"**Child {i+1}:** {details['name']} | Age: {details['age']} | Service: {details['service']}")
            st.write(f"**Appointment Date:** {appointment_date}")
            st.write(f"**Slot:** {selected_slot}")
            st.write(f"**Token Number:** {token}")
            st.write(f"**Total Cost:** ₹{total_cost}")

            del st.session_state.parent_data
            st.rerun()

# Main app
def main():
    # Sidebar with navigation
    with st.sidebar:
        if st.button("Book Appointment"):
            st.session_state.page = "booking"
            st.rerun()

    # Page navigation logic
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "home":
        home_page()
    elif st.session_state.page == "booking":
        booking_page()

if __name__ == "__main__":
    main()