import pandas as pd
import streamlit as st
import datetime
import pickle
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
from streamlit_gsheets import GSheetsConnection
import streamlit_authenticator as stauth


st.set_page_config(page_title='uydiaspora', initial_sidebar_state='collapsed')


# Establish connection to spreads
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch current data
dataframe = conn.read(worksheet="Members", usecols=list(range(8)), ttl=45)
dataframe = dataframe.dropna(how="all")
'''

# LOAD DATA
data_path = './UYD_Membership_Data.csv'
dataframe = pd.read_csv(data_path)
dataframe = dataframe.dropna(how="all")
'''
# LOAD HASHED PASSWORD
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_password = pickle.load(file)

# LOAD CONFIG CREDENTIALS
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# CONSTANTS
GENDER = ['Male', 'Female']
WORKSHEET = 'Members'


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


def insert_member(name, gender, date_of_birth, age, phone_number, email, location, worksheet: str = WORKSHEET):
    member_id = len(dataframe['Member ID'].values) + 1
    new_data = pd.DataFrame([{'Member ID': member_id,
                              'Name': name,
                              'Gender': gender,
                              'Date of Birth': date_of_birth,
                              'Age': age,
                              'Phone Number': phone_number,
                              'Email': email,
                              'Location': location}])
    data = pd.concat([dataframe, new_data], ignore_index=True)
    # data.to_csv('./UYD_Membership_Data.csv', index=False)
    conn.update(worksheet=worksheet, data=data)
    st.success(f'Thank you {name} for filling this form.')


def update_member(name, gender, date_of_birth, age, phone_number, email, location, worksheet: str = WORKSHEET):
    dataframe.loc[dataframe['Name'] == name, 'Gender'] = gender
    dataframe.loc[dataframe['Name'] == name, 'Date of Birth'] = date_of_birth
    dataframe.loc[dataframe['Name'] == name, 'Age'] = age
    dataframe.loc[dataframe['Name'] == name, 'Phone Number'] = phone_number
    dataframe.loc[dataframe['Name'] == name, 'Email'] = email
    dataframe.loc[dataframe['Name'] == name, 'Location'] = location

    # dataframe.to_csv('./UYD_Membership_Data.csv', index=False)
    conn.update(worksheet=worksheet, data=dataframe)
    st.success('Information successfully updated')


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
                                        insert_member(name, gender, date_of_birth, age,
                                                      phone_number, email, location)
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


def view_members():
    # d_path = './UYD_Membership_Data.csv'
    # d_frame = pd.read_csv(d_path)
    # dataframe = conn.read(worksheet="Members", usecols=list(range(7)), ttl=45)
    # Fetch current data
    dataframe1 = conn.read(worksheet="Members", usecols=list(range(8)), ttl=45)
    dataframe1 = dataframe1.dropna(how="all")
    dataframe1 = dataframe1.drop(['Date of Birth', 'Phone Number', 'Email'], axis=1)
    st.dataframe(dataframe1)


def enter_details(button_name):
    st.subheader('Membership Data Form')
    if button_name == "Submit":
        with ((st.form(key='member_form', clear_on_submit=True))):
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

    elif button_name == "Update":
        member_to_update = st.selectbox(
            "Select Member",
            options=dataframe['Name'].tolist()
        )
        member_data = dataframe[dataframe['Name'] == member_to_update].iloc[0]
        with ((st.form(key='update', clear_on_submit=True))):
            name = st.text_input(':blue[Full Name]',
                                 placeholder="Enter First Name and Last Name",
                                 value=member_data['Name'])
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
                member_id = len(dataframe['Member ID'].values) + 1
                new_data = pd.DataFrame([{'Member ID': member_id,
                                          'Name': name,
                                          'Gender': gender,
                                          'Date of Birth': date_of_birth,
                                          'Age': age,
                                          'Phone Number': phone_number,
                                          'Email': email,
                                          'Location': location}])
                data = pd.concat([dataframe, new_data], ignore_index=True)
                # data.to_csv('./UYD_Membership_Data.csv', index=False)
                conn.update(worksheet=worksheet, data=data)
                st.success('Information successfully updated')
                # update_member(name, gender, date_of_birth, age, phone_number, email, location)


def call_to_action():
    action = st.selectbox(
        "Choose an action",
        [
            "Enter Member Details",
            "Update Existing Member Details",
            "View All Members",
        ],
        index=None
    )

    if action == "Enter Member Details":
        st.markdown("Enter Details")
        enter_details(button_name="Submit")
    elif action == "Update Existing Member Details":
        st.markdown("Update Details")
        enter_details(button_name="Update")
    elif action == "View All Members":
        view_members()
