import sys
import argparse
import json
import os
from bs4 import BeautifulSoup
from strava_hack_tools_common.login import Login

#Do you want to download all photos of your friends? no problem. 
#
#    usage: strava_photo_downloader.py [-h] -a ID_Number -l username password [-fl] [-y] [-v]
#    
#    Strava Photo Downloader Tool.
#    
#    options:
#      -h, --help            show this help message and exit
#      -a ID_Number, --athlete ID_Number
#                            ID of Athlete to analyze (default: None)
#      -l username password, --login username password
#                            Login with username and password (default: ('None', 'None'))
#      -fl, --forcelogin     Force a new login instead saved cookies. Warning, this option will destroy old credentials. (default: False)
#      -y, --yes             Yes to all (default: False)
#      -v, --verbose         increase output verbosity (default: False)
#

STRAVA_ATHLETE_HOME            = 'https://www.strava.com/athletes'

def downloadallphotos(dict_of_files):
    if not os.path.isdir(str(args.athlete)):
        os.makedirs(str(args.athlete))

    for onephoto in dict_of_files:
        print("downloading -> "+str(args.athlete)+"/"+dict_of_files[onephoto]['photo_id']+".jpg")
        query = session.get(dict_of_files[onephoto]['large'])
        open(str(args.athlete)+"/"+dict_of_files[onephoto]['photo_id']+".jpg", "wb").write(query.content)

    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Strava Photo Downloader Tool.',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a','--athlete' 		, metavar='ID_Number'
                                                , type=int
                                                , required=True
												, help='ID of Athlete to analyze')
    parser.add_argument('-l','--login'			, required=True
												, nargs=2
												, metavar=('username', 'password')
												, default=('None','None')
												, help='Login with username and password')
    parser.add_argument('-fl','--forcelogin'	, help='Force a new login instead saved cookies. Warning, this option will destroy old credentials.'
												, action='store_true')
    parser.add_argument('-y','--yes'			, help='Yes to all'
												, action='store_true')
    parser.add_argument('-v','--verbose'		, help='increase output verbosity'
												, action='store_true')
    args = parser.parse_args()

	#Check Force Login Options
    login_username=args.login[0]
    login_password=args.login[1]
    login_ok= 0
    user_login = Login(args.verbose)

    if args.forcelogin:
        user_login.forcelogin(login_username)

	#Check Login Option
    if login_username != 'None':
        if user_login.login(str(login_username),str(login_password)):
            print("Info: LOGIN OK.")
            login_ok=1
        else:
            print("Warning: LOGIN FAIL!")
            login_ok=0

    else:
        parser.print_help()
        sys.exit("you must define -l for LOGIN Credentials")
        
	#re add session var after login.
    session = user_login.LOGIN_SESSION
    if login_ok == 0: 
        sys.exit("To continue, you must be logged.")

    #debug
    if args.verbose:
        print('getting data:'+str(STRAVA_ATHLETE_HOME)+'/'+str(args.athlete))

    query = session.get(STRAVA_ATHLETE_HOME + '/'+ str(args.athlete)).text

    public_data = BeautifulSoup(query, 'html.parser')
    public_data_details = public_data.find('div', attrs={'data-react-class':'MediaThumbnailList'})
    public_data_streams = public_data_details.attrs.get('data-react-props')
    
    query= json.loads(public_data_streams)

    photos_dict = {}

    for entry in query['items']:
        if entry['media_type'] == 1:
            photos_dict.update({entry['photo_id']:{
                                    "photo_id":entry['photo_id'],
								    "large":entry['large'],
                                    "start_date":entry['activity']['start_date']}})
    
    print('Total Photos:'
		+ str(len(photos_dict))
		+ ' from: '+list(photos_dict.values())[0]["start_date"]
        + ' until: '+list(photos_dict.values())[-1]["start_date"])
    
    if not args.yes:
        data = input("do you want to give that "+str(len(photos_dict))+" kudos ? (y/n)")
    else:
        data = 'y'
	
    if data.lower() in ('y') or args.yes:
        downloadallphotos(photos_dict)
		
    else:
        sys.exit("No problem.")
    
