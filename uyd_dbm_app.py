from utils import *
import streamlit_authenticator as stauth

# set_background('./nba_rookie1.jpg')

config['credentials']['usernames']['uyd2023']['password'] = hashed_password[0]
config['credentials']['usernames']['uyd2023admin']['password'] = hashed_password[1]


def main():
    authenticator = stauth.Authenticate(config['credentials'],
                                        cookie_name=config['cookie']['name'],
                                        cookie_key=config['cookie']['key'],
                                        cookie_expiry_days=config['cookie']['expiry_days'])

    name, authentication_status, username = authenticator.login("main",
                                                                fields={
                                                                    'Form name': 'Login',
                                                                    'Username': 'Username',
                                                                    'Password': 'Password',
                                                                    'Login': 'Login'})

    if authentication_status:
        authenticator.logout('Logout', 'sidebar')

        if username == 'uyd2023admin':
            st.sidebar.title('Welcome Admin!')
            st.title(':green[UMUEHEA YOUTHS IN DIASPORA]')
            call_to_action("admin")

        elif username == 'uyd2023':
            st.sidebar.title('Welcome!')
            st.title(':green[UMUEHEA YOUTHS IN DIASPORA]')
            call_to_action("member")

    elif authentication_status is False:
        st.error('Username or Password is incorrect')
        
    elif authentication_status is None:
        st.warning('Please enter username and password')


if __name__ == "__main__":
    main()
