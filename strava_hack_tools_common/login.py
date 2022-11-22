import requests
from http.cookiejar import LWPCookieJar

import os
from bs4 import BeautifulSoup

STRAVA_URL_LOGIN = 'https://www.strava.com/login'
STRAVA_URL_SESSION = 'https://www.strava.com/session'
STRAVA_ACTIVITIES_SESSION ='https://www.strava.com/activities/'
STRAVA_LOGGED_OUT_FINGERPRINT = 'logged-out'
COOKIE_FILE_DIR='.authdata'


class Login:

    VERBOSE = False
    LOGIN_SESSION = ''
    AUTHENTICITY_TOKEN = ''

    def __init__(self, verbose=False):
        self.VERBOSE = verbose

    def cookies_save_to_disk(self, login_username,session,authenticity_token):
        session.cookies.save(ignore_discard=True)
        file = open(COOKIE_FILE_DIR+'_'+str(login_username)+'_authenticity_token', 'w')
        file.write(authenticity_token)
        file.close()


    def cookies_remove_from_disk(self, login_username):
        if os.path.exists(COOKIE_FILE_DIR+'_'+str(login_username)):
            os.remove(COOKIE_FILE_DIR+'_'+str(login_username))

        if os.path.exists(COOKIE_FILE_DIR+'_'+str(login_username)+'_authenticity_token'):
            os.remove(COOKIE_FILE_DIR+'_'+str(login_username)+'_authenticity_token')

    def cookies_get_from_disk(self, login_username, session):
        if self.VERBOSE:
                print('loading saved cookies')
        session.cookies.load(ignore_discard=True)
        file = open(COOKIE_FILE_DIR+'_'+str(login_username)+'_authenticity_token', 'r')
        authenticity_token = file.read()
        file.close()

        return authenticity_token

    def login(self, login_username, login_password):

        session = requests.session()
        session_from_disk = False

        session.cookies = LWPCookieJar(COOKIE_FILE_DIR+'_'+str(login_username))
        if os.path.exists(COOKIE_FILE_DIR+'_'+str(login_username)):
            # Load saved cookies from the file and use them in a request
            authenticity_token= self.cookies_get_from_disk(login_username, session)		
            session_from_disk = True
        else:
            r = session.get(STRAVA_URL_LOGIN)
            soup = BeautifulSoup(r.content, 'html.parser')

            get_details = soup.find('input', attrs={'name':'authenticity_token'})
            authenticity_token = get_details.attrs.get('value')

            if self.VERBOSE:
                print('LOGIN TOKEN:'+authenticity_token)
            
            # This is the form data that the page sends when logging in
            login_data = {
                'email': login_username,
                'password': login_password,
                'utf8': '%E2%9C%93',
                'authenticity_token':authenticity_token
            }

            # Authenticate
            r = session.post(STRAVA_URL_SESSION, data=login_data)
            self.cookies_save_to_disk(login_username, session, authenticity_token)
        
        # Try accessing a page that requires you to be logged in
        r = session.get('https://www.strava.com/dashboard')

        self.LOGIN_SESSION = session
        self.AUTHENTICITY_TOKEN = authenticity_token

        if int(r.text.find(STRAVA_LOGGED_OUT_FINGERPRINT)) >= 0:
            if session_from_disk:
                if self.VERBOSE:
                    print('Saved cookies Failed, getting new session data...')
                self.cookies_remove_from_disk(login_username)
                return self.login(login_username, login_password)
            else:
                return False
        else:
            return True