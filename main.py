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
        st.button("➤ Toggle Sidebar", on_click=toggle_sidebar)
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

# Pages
    def home_page():
        render_sidebar()

        # Translate buttons at the top
        if st.session_state.language == "en":
            st.button("Translate to Kannada / ಕನ್ನಡಕ್ಕೆ ಭಾಷಾಂತರಿಸಿ", on_click=lambda: st.session_state.update({"language": "kn"}))
        else:
            st.button("Translate to English / ಇಂಗ್ಲೀಷ್‌ಗೆ ಭಾಷಾಂತರಿಸಿ", on_click=lambda: st.session_state.update({"language": "en"}))

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
                - ಮಾಣ್ಡ್ಯಾ ಜಿಲ್ಲಾ ಆಸ್ಪತ್ರೆಯ ಪೀಡಿಯಾಟ್ರಿಕ್ಸ್ ಅಸೋಸಿಯೇಟ್ ಪ್ರೊಫೆಸರ್  
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
            st.markdown(f"**Appointment Date: {date} | Time: {datetime.datetime.now().strftime('%I:%M %p')}**")

            # Prescription Form
            disease = st.text_area("Enter Disease")

            # Medicine Details
            if "medicine_data" not in st.session_state:
                st.session_state["medicine_data"] = []

            medicine_name = st.text_input("Enter Medicine Name")
            before_after_food = st.selectbox(
                "Before or After Food", ["Before Food", "After Food"]
            )
            timings = st.multiselect(
                "Select Timing", ["Morning", "Afternoon", "Evening"]
            )

            if st.button("Add Medicine"):
                if medicine_name and timings:
                    medicine_entry = {
                        "name": medicine_name,
                        "food": before_after_food,
                        "timings": ", ".join(timings),
                    }
                    st.session_state["medicine_data"].append(medicine_entry)
                    st.success("Medicine added successfully!")

            # Display Added Medicines
            if st.session_state["medicine_data"]:
                st.subheader("Added Medicines")
                for idx, med in enumerate(st.session_state["medicine_data"], start=1):
                    st.write(
                        f"{idx}. **{med['name']}** - {med['food']} - {med['timings']}"
                    )

            # Save Button
            if st.button("Save Prescription"):
                st.success("Prescription saved successfully!")
        else:
            st.warning("No appointments found for the selected date")


def booking_page():
        render_sidebar()

        # Translate buttons at the top
        if st.session_state.language == "en":
            st.button("Translate to Kannada / ಕನ್ನಡಕ್ಕೆ ಭಾಷಾಂತರಿಸಿ", on_click=lambda: st.session_state.update({"language": "kn"}))
        else:
            st.button("Translate to English / ಇಂಗ್ಲೀಷ್‌ಗೆ ಭಾಷಾಂತರಿಸಿ", on_click=lambda: st.session_state.update({"language": "en"}))

        if st.session_state.language == "en":
            st.title("Book Appointment")
            st.markdown("Fill in the details below to book an appointment.")
            today = datetime.now().date()
            available_dates = [today + timedelta(days=i) for i in range(7) if (today + timedelta(days=i)).weekday() != 6]
            date = st.date_input("Select a Date", min_value=available_dates[0], max_value=available_dates[-1])
            if date.weekday() == 6:
                st.warning("Appointments cannot be booked for Sundays.")
                return
            slot = st.selectbox("Select a Time Slot", get_available_slots(date))
            parent_name = st.text_input("Parent's Name")
            phone = st.text_input("Phone Number")
            address = st.text_area("Address")

            # Number of children with plus and minus controls
            num_children = st.number_input("Number of Children", min_value=1, max_value=5)

            children = []
            for i in range(num_children):
                st.subheader(f"Child {i+1}")
                child_name = st.text_input(f"Name of Child {i+1}")
                child_age = st.number_input(f"Age of Child {i+1}", min_value=0, max_value=18)
                children.append({"name": child_name, "age": child_age})

            if st.button("Book Appointment"):
                if parent_name and phone and address and all(child["name"] for child in children):
                    token = f"TOKEN{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    save_appointment(date, parent_name, phone, address, num_children, children, slot, token)
                    st.success(f"Appointment successfully booked! Your token number is {token}.")
                else:
                    st.error("Please fill in all the details.")
        else:
            st.title("ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಬುಕ್ ಮಾಡಿ")
            st.markdown("ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಬುಕ್ ಮಾಡಲು ಕೆಳಗಿನ ವಿವರಗಳನ್ನು ಪೂರ್ತಿಗೊಳಿಸಿ.")
            today = datetime.now().date()
            available_dates = [today + timedelta(days=i) for i in range(7) if (today + timedelta(days=i)).weekday() != 6]
            date = st.date_input("ದಿನಾಂಕವನ್ನು ಆಯ್ಕೆಮಾಡಿ", min_value=available_dates[0], max_value=available_dates[-1])
            if date.weekday() == 6:
                st.warning("ಆದಿತ್ಯವಾರಗಳಲ್ಲಿ ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್‌ಗಳನ್ನು ಬುಕ್ ಮಾಡಲಾಗುವುದಿಲ್ಲ.")
                return
            slot = st.selectbox("ಸಮಯ ಸ್ಲಾಟ್ ಆಯ್ಕೆಮಾಡಿ", get_available_slots(date))
            parent_name = st.text_input("ಪೋಷಕರ ಹೆಸರು")
            phone = st.text_input("ದೂರವಾಣಿ ಸಂಖ್ಯೆ")
            address = st.text_area("ವಿಳಾಸ")

            # Number of children with plus and minus controls
            num_children = st.number_input("ಮಕ್ಕಳ ಸಂಖ್ಯೆ", min_value=1, max_value=5)

            children = []
            for i in range(num_children):
                st.subheader(f"ಮಗು {i+1}")
                child_name = st.text_input(f"ಮಗು {i+1} ಹೆಸರು")
                child_age = st.number_input(f"ಮಗು {i+1} ವಯಸ್ಸು", min_value=0, max_value=18)
                children.append({"name": child_name, "age": child_age})

            if st.button("ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಬುಕ್ ಮಾಡಿ"):
                if parent_name and phone and address and all(child["name"] for child in children):
                    token = f"TOKEN{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    save_appointment(date, parent_name, phone, address, num_children, children, slot, token)
                    st.success(f"ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಯಶಸ್ವಿಯಾಗಿ ಬುಕ್ ಮಾಡಲಾಗಿದೆ! ನಿಮ್ಮ ಟೋಕನ್ ಸಂಖ್ಯೆ {token} ಆಗಿದೆ.")
                else:
                    st.error("ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ಪೂರ್ತಿಗೊಳಿಸಿ.")

# Main Function
def main():
    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Book Appointment":
        booking_page()
    elif st.session_state.page == "Prescription Entry":
        prescription_page()

if __name__ == "__main__":
    main()
