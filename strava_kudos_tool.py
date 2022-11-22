import sys
import urllib
import json
import os
import time
import datetime
from datetime import timedelta
import argparse
import dateutil.parser
from collections import Counter
from collections import OrderedDict
from strava_hack_tools_common.login import Login

# This script can help you to give a lot kudos for your friends.
#
#usage: strava_kudos_tool.py [-h] [-a ID_Number] [-fd UNIX_TIME] -l username password [-fl] [-nebr Number] [-ft FeedType] [-c CLUB_ID] [-v]
#
#Strava Kudos Tool.
#
#options:
#  -h, --help            show this help message and exit
#  -a ID_Number, --athlete ID_Number
#                        Filter by ID of Athlete to analyze, by default all feed is analyzed. (default: None)
#  -fd UNIX_TIME, --feeddeep UNIX_TIME
#                        Force a end of time for get the feed, define a UNIX TIME (default: None)
#  -l username password, --login username password
#                        Login with username and password (default: ('None', 'None'))
#  -fl, --forcelogin     Force a new login instead saved cookies. Warning, this option will destroy old credentials. (default: False)
#  -nebr Number, --numentriesbyrequest Number
#                        Number of entries asked for each request, by default this value is controlled by Strava. If even set a big number, 
#                        strava could rewrite it with the max value from server. (100 entries) (default: 0)
#  -ft FeedType, --feedtype FeedType
#                        Force a filter by feed type, by default this value is controlled by Strava (default: None)
#  -c CLUB_ID, --club CLUB_ID
#                        Use it with -ft option when 'club' feed type is used. (default: None)
#  -v, --verbose         increase output verbosity (default: False)


STRAVA_DASHBOARD_FEED = 'https://www.strava.com/dashboard/feed'
STRAVA_KUDOS_URL 	  = 'https://www.strava.com/feed/activity/#/kudo'

def givekudos(id_activity_for_kudo):

	query = session.post(STRAVA_KUDOS_URL.replace("#",str(id_activity_for_kudo)),headers = {"x-csrf-token": user_login.AUTHENTICITY_TOKEN}).text
	query = json.loads(query)

	if  query['success'] == 'true':
		return True
	else:
		return False

def givekudosall(activities_for_kudos_dict):
	somefailed = False
	for id_activity_for_kudo in activities_for_kudos_dict:	
		if givekudos(id_activity_for_kudo):
			print("kudo for "+str(id_activity_for_kudo)+" OK.")
		else:
			print("kudo for "+str(id_activity_for_kudo)+" FAIL.")
			somefailed = True
	
	if somefailed:
		print("WARNING: Some kudos FAILED. Please Check the list.")

	return not somefailed

	
if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Strava Kudos Tool.',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-a','--athlete' 		, metavar='ID_Number'
												, type=int
												, help='Filter by ID of Athlete to analyze, by default all feed is analyzed.')
	parser.add_argument('-fd','--feeddeep' 		, metavar='UNIX_TIME'
												, type=int
												, help='Force a end of time for get the feed, define a UNIX TIME')
	parser.add_argument('-l','--login'			, required=True
												, nargs=2
												, metavar=('username', 'password')
												, default=('None','None')
												, help='Login with username and password')
	parser.add_argument('-fl','--forcelogin'	, help='Force a new login instead saved cookies. Warning, this option will destroy old credentials.'
												, action='store_true')
	parser.add_argument('-nebr','--numentriesbyrequest'
												, help='Number of entries asked for each request, '
													+ 'by default this value is controlled by Strava. '
													+ 'If even set a big number, strava could rewrite it with the max value from server. (100 entries)'
												, type=int
												, default=0
												, metavar='Number')
	parser.add_argument('-ft','--feedtype'		, metavar='FeedType'
												, choices = ['None','following', 'club']
												, default='None'
												, help='Force a filter by feed type, by default this value is controlled by Strava')
	parser.add_argument('-c','--club' 			, metavar='CLUB_ID'
												, type=int
												, help='Use it with -ft option when \'club\' feed type is used.')

	parser.add_argument('-v','--verbose'		, help='increase output verbosity'
												, action='store_true')
	args = parser.parse_args()

	#Check num entries by request Options
	num_entries_by_request = args.numentriesbyrequest
	if num_entries_by_request < 0 or str(num_entries_by_request) == 'None':
		parser.print_help()
		sys.exit("you must define a Number of entries -nebr as a number bigger than 0")

	#Check feed_type Options
	if args.feedtype == 'club' and str(args.club) == 'None':
		parser.print_help()
		sys.exit("When use feedtype \'club\' you must define CLUB_ID with --club option.")
	
	#Check Club ID Options
	if args.feedtype == 'None' and str(args.club) != 'None':
		parser.print_help()
		sys.exit("When use CLUB_ID you must define feedtype with --ft option.")

	#Check Force Login Options
	login_username=args.login[0]
	login_password=args.login[1]
	login_ok= 0
	user_login = Login(args.verbose)

	if args.forcelogin:
		if args.verbose:
			print('Force a new login...')
		user_login.cookies_remove_from_disk(login_username)

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

    #feed
	limit = 0
	before = 0
	cursor = 0
	lastKudoed = False
	params_list = {}
	activities_for_kudos_dict = {}

	total_raw_entries = 0

	if args.feedtype != 'None':	
		params_list.update({"feed_type": args.feedtype})
		if args.feedtype == 'club':
			params_list.update({"club_id": args.club})
	

	while not lastKudoed:

		if before != 0:
			params_list.update({"before": before})
			params_list.update({"cursor": cursor})
		
		if num_entries_by_request != 0:
			params_list.update({"num_entries": num_entries_by_request})

		params = urllib.parse.urlencode(params_list)

		if args.verbose:
			print('getting feed data:'+str(STRAVA_DASHBOARD_FEED)+'?'+params)

		query = session.get(STRAVA_DASHBOARD_FEED+'?'+params).text
		query = json.loads(query)

		total_raw_entries = total_raw_entries + len(query['entries'])
		print('Total Raw Entries:' + str(total_raw_entries))
		
		if args.verbose:
			c = Counter(player['entity'] for player in query['entries'])
			print(c)

		for entry in query['entries']:
			if entry['entity'] == 'Activity':
				idActivity 	= entry['activity']['id']
				canKudo 	= entry['activity']['kudosAndComments']['canKudo']
				hasKudoed 	= entry['activity']['kudosAndComments']['hasKudoed']
				before 		= entry['cursorData']['updated_at']
				cursor		= entry['cursorData']['rank']

				if args.verbose:
					print('Id activity:'+str(idActivity)+' canKudo:'+ str(canKudo)+ ' hasKudoed:'+str(hasKudoed))

				if hasKudoed:
					lastKudoed = True
				else:
					if canKudo and \
						( str(args.athlete) == entry['activity']['athlete']['athleteId'] or str(args.athlete) =='None' ):

						activities_for_kudos_dict.update({idActivity:{	"athleteId":entry['activity']['athlete']['athleteId'],
																		"athleteName":entry['activity']['athlete']['athleteName'],
																		"updated_at":entry['cursorData']['updated_at']}})
				
				if str(args.feeddeep)!= 'None' and args.feeddeep <= entry['cursorData']['updated_at']:
					lastKudoed = False

			if entry['entity'] == 'GroupActivity':
				for entryOfGroup in entry['rowData']['activities']:
					idActivity 	= entryOfGroup['activity_id']
					canKudo 	= entryOfGroup['can_kudo']
					hasKudoed 	= entryOfGroup['has_kudoed']
					before 		= entry['cursorData']['updated_at']
					cursor		= entry['cursorData']['rank']

					if args.verbose:
						print('Id activity:'+str(idActivity)+' canKudo:'+ str(canKudo)+ ' hasKudoed:'+str(hasKudoed))

					if hasKudoed:
						lastKudoed = True
					else:
						if canKudo and \
							( str(args.athlete) == entryOfGroup['athlete_id'] or str(args.athlete) =='None' ):

							activities_for_kudos_dict.update({idActivity:{	"athleteId":entryOfGroup['athlete_id'],
																			"athleteName":entryOfGroup['athlete_name'],
																			"updated_at":entry['cursorData']['updated_at']}})
					
					if str(args.feeddeep)!= 'None' and args.feeddeep <= entry['cursorData']['updated_at']:
						lastKudoed = False

		if len(query['entries']) == 0:
			lastKudoed = True
			print('Warning: Detect empty entries, no more.')

		limit = limit +1

	if len(activities_for_kudos_dict) == 0:
		sys.exit("No found kudos pending for range especified.")

	print('Total Activities to give kudos:'
		+ str(len(activities_for_kudos_dict))
		+ ' from: '+datetime.datetime.utcfromtimestamp(int(list(activities_for_kudos_dict.values())[0]["updated_at"])).strftime('%Y-%m-%dT%H:%M:%SZ')
		+ ' until: '+datetime.datetime.utcfromtimestamp(int(before)).strftime('%Y-%m-%dT%H:%M:%SZ'))

	#Reverse the Dict for give kudos from OLD to NEW
	activities_for_kudos_dict=OrderedDict(reversed(list(activities_for_kudos_dict.items())))

	data = input("do you want to give that "+str(len(activities_for_kudos_dict))+" kudos ? (y/n)")
	
	if data.lower() in ('y'):
		givekudosall(activities_for_kudos_dict)
		
	else:
		sys.exit("No problem.")
