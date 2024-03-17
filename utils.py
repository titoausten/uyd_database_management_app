import pandas as pd
import streamlit as st
import datetime
from streamlit_gsheets import GSheetsConnection
import pickle
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth


# CONSTANTS
GENDER = ['Male', 'Female']
WORKSHEET = 'Members'

# Establishing a Google Sheets connection
conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# Fetch current data
dataframe = conn.read(worksheet=WORKSHEET, usecols=list(range(7)), ttl=5)
dataframe = dataframe.dropna(how="all")

# LOAD HASHED PASSWORD
file_path = Path(__file__).parent / "hashed_pw2.pkl"
with file_path.open("rb") as file:
    hashed_password = pickle.load(file)

# LOAD CONFIG CREDENTIALS
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


class FixedAuthenticate(stauth.Authenticate):
    def _implement_logout(self):
        try:
            self.cookie_manager.delete(self.cookie_name)
        except Exception as e:
            print(e)
        self.credentials['usernames'][st.session_state['username']]['logged_in'] = False
        st.session_state['logout'] = True
        st.session_state['name'] = None
        st.session_state['username'] = None
        st.session_state['authentication_status'] = None


def get_member_names():
    names = dataframe['Name'].values
    return names


def check(name, gender, date_of_birth, age, phone_number, email, location):
    # Validate name
    if name != '' and name != name.isdigit() and name != name.replace('.', '', 1).isdigit():
        if name not in get_member_names():
            if gender is not None:
                # Validate DOB
                if date_of_birth is not None and date_of_birth != datetime.datetime.today().date():
                    if date_of_birth < datetime.datetime.today().date():
                        if age >= 18:
                            if phone_number != '':
                                if email != '':
                                    if location != '':
                                        new_data = pd.DataFrame([{'Name': name,
                                                                  'Gender': gender,
                                                                  'Date of Birth': date_of_birth,
                                                                  'Age': age,
                                                                  'Phone Number': phone_number,
                                                                  'Email': email,
                                                                  'Location': location}])
                                        data = pd.concat([dataframe, new_data], ignore_index=True)
                                        # data.to_csv('./UYD_Membership_Data.csv', index=False)
                                        conn.update(worksheet=WORKSHEET, data=data)
                                        st.success(f'Thank you {name} for filling this form.')
                                        st.balloons()
                                    else:
                                        st.warning('Location field is compulsory, Please enter rightly')
                                else:
                                    st.warning('Email field is compulsory, Please enter rightly')
                            else:
                                st.warning('Phone Number field is compulsory, Please enter rightly')
                        else:
                            st.warning('Only persons between age 18-59 are to fill this form')
                    else:
                        st.warning('Date of Birth cannot be in the future')
                else:
                    st.warning('Date of Birth is compulsory, Please enter rightly')
            else:
                st.warning('Choose a gender')
        else:
            st.warning('Member name exists!')
            st.stop()
    else:
        st.warning('Please enter your name rightly')
        st.stop()


def enter_details(button_name: str):
    if button_name == 'Submit':
        with st.form(key='member_form', clear_on_submit=True):
            # with st.form(key="vendor_form"):
            name = st.text_input(':blue[Full Name]', placeholder="Enter First Name and Last Name")
            gender = st.selectbox(':blue[Gender]', ['Male', 'Female'], index=None, placeholder="Choose an option")
            date_of_birth = st.date_input(':blue[Date of Birth]', min_value=datetime.date(day=1, month=1, year=1965))
            phone_number = st.text_input(':blue[Phone Number with Country code]')
            phone_number = str(phone_number)
            email = st.text_input(':blue[Email Address]')
            location = st.text_input(':blue[Location]', placeholder="Enter City, Country")
            currentDate = datetime.datetime.today()
            age = currentDate.year - date_of_birth.year - ((currentDate.month, currentDate.day) <
                                                           (date_of_birth.month, date_of_birth.day))

            submit = st.form_submit_button(button_name)
            if submit:
                check(name, gender, date_of_birth, age, phone_number, email, location)

    elif button_name == 'Update':
        member_to_update = st.selectbox(
            "Select a Member to Update", options=dataframe["Name"].tolist()
        )
        member_data = dataframe[dataframe["CompanyName"] == member_to_update].iloc[
            0
        ]
        with st.form(key="update", clear_on_submit=True):
            name = st.text_input(
                label="Full Name", value=member_data["Name"]
            )
            gender = st.selectbox(':blue[Gender]', options=GENDER,
                                  index=GENDER.index(member_data['Gender']),
                                  placeholder="Choose an option")
            date_of_birth = st.date_input(':blue[Date of Birth]',
                                          value=pd.to_datetime(member_data['Date of Birth']))
            phone_number = st.text_input(':blue[Phone Number with Country code]',
                                         value=member_data['Phone Number'])
            phone_number = str(phone_number)
            email = st.text_input(':blue[Email Address]', value=member_data['Email'])
            location = st.text_input(':blue[Location]', placeholder="Enter City, Country",
                                     value=member_data['Location'])
            currentDate = datetime.datetime.today()
            age = currentDate.year - date_of_birth.year - ((currentDate.month, currentDate.day) <
                                                           (date_of_birth.month, date_of_birth.day))

            submit = st.form_submit_button(button_name)
            if submit:
                # Removing old entry
                dataframe.drop(
                    dataframe[
                        dataframe["Name"] == member_to_update
                        ].index,
                    inplace=True,
                )
                # Creating updated data entry
                new_data = pd.DataFrame([{'Name': name,
                                          'Gender': gender,
                                          'Date of Birth': date_of_birth,
                                          'Age': age,
                                          'Phone Number': phone_number,
                                          'Email': email,
                                          'Location': location}])
                data = pd.concat([dataframe, new_data], ignore_index=True)
                conn.update(worksheet=WORKSHEET, data=data)
                st.success('Information successfully updated')

    elif button_name == 'Delete':
        member_to_delete = st.selectbox(
            "Select a Member to Delete", options=dataframe["Name"].tolist()
        )

        if st.button("Delete"):
            dataframe.drop(
                dataframe[dataframe["Name"] == member_to_delete].index,
                inplace=True,
            )
            conn.update(worksheet=WORKSHEET, data=dataframe)
            st.success("Member successfully deleted!")


def call_to_action():
    action = st.selectbox(
        "Choose an Action",
        [
            "Enter Member Details",
            "Update Existing Member Details",
            "View All Members",
            "Delete Member Details",
        ],
        index=None
    )

    if action == "Enter Member Details":
        st.markdown("Enter details")
        enter_details("Submit")

    elif action == "Update Existing Member Details":
        st.markdown("Select a member and update their details.")
        enter_details("Update")

    # View All Vendors
    elif action == "View All Members":
        st.dataframe(dataframe)

    # Delete Member
    elif action == "Delete Member Details":
        action = st.selectbox(
            "Are you an Executive?",
            [
                "Yes",
                "No",
            ],
            index=None
        )
        if action == "Yes":
            st.markdown("Enter Executives Password")
            password = st.text_input('Enter Password', type="password")
            if password == hashed_password[1]:
                enter_details("Delete")
            else:
                st.error('Wrong Executives password')
        elif action == "No":
            st.warning('You are not allowed to delete member details')
