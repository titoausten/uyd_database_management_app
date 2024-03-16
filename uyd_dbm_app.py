from dependencies import *

# set_background('./nba_rookie1.jpg')

config['credentials']['usernames']['uyd2023']['password'] = hashed_password[0]


def main():
    authenticator = FixedAuthenticate(config['credentials'], cookie_name=config['cookie']['name'],
                                      key=config['cookie']['key'],
                                      cookie_expiry_days=config['cookie']['expiry_days'])

    name, authentication_status, username = authenticator.login("main", max_concurrent_users=20,
                                                                fields={'Form name': 'Login',
                                                                        'Username': 'Username',
                                                                        'Password': 'Password',
                                                                        'Login': 'Login'})

    if authentication_status:
        authenticator.logout('Logout', 'sidebar')
        st.sidebar.title('Welcome!')
        st.title(':green[UMUEHEA YOUTHS IN DIASPORA]')
        call_to_action()
    elif authentication_status is False:
        st.error('Username or Password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter username and password')


if __name__ == "__main__":
    main()
