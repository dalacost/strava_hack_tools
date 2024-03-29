import sys
import urllib3
import urllib
import json
import os
import shutil
import socket
import time
import datetime
from datetime import timedelta
import argparse
import requests
import traceback
from bs4 import BeautifulSoup
import dateutil.parser
from strava_hack_tools_common.login import Login

# This script can reconstruct a gpx track of a Strava activity from 
# public information. 
#
#usage: strava_traces_downloader.py [-h] -a ID_Number [-o output.gpx]
#
#Download GPS Traces from Strava.
#
#optional arguments:
#  -h, --help            show this help message and exit
#  -a ID_Number, --activity ID_Number
#                        ID of activity to download (default: None)
#  -o output.gpx, --output output.gpx
#                        name of GPX file output. (default: output.gpx)
#                        


STRAVA_PATH_STREAM = 'http://www.strava.com/activities/'
STRAVA_ACTIVITIES_SESSION ='https://www.strava.com/activities/'
DEFAULT_OUTPUT_FILE='output.gpx'

#GPX Format
HEAD_FILE="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\" ?>\n \
<gpx xmlns=\"http://www.topografix.com/GPX/1/1\" creator=\"\" version=\"1.1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd\">\n"   
FOOT_FILE="</gpx>"

def save_as_gpx(activity_id,points,elevation_points, time_points, started_unix_time, output_file):

	final_file = open(output_file, 'w')
	final_file.write(HEAD_FILE)
	final_file.write('<trk>\n')
	final_file.write('<name> Activity '+str(activity_id)+'</name>\n')
	final_file.write('<trkseg>\n')
	points_counter=0

	for point in points:
		#not save 0,0 points, this are points inside of protection area. 
		if not (str(point[0]) == '0.0') and not (str(point[1]) == '0.0'):
			final_file.write('\t<trkpt lat="'+str(point[0])+'"'+' lon="'+str(point[1])+'">\n')
			final_file.write('\t\t<ele>'+str(elevation_points[points_counter])+'</ele>\n')
			if not args.notime:
				try:
					final_file.write('\t\t<time>'+datetime.datetime.utcfromtimestamp(int(started_unix_time)+int(time_points[points_counter])).strftime('%Y-%m-%dT%H:%M:%SZ')+'</time>\n')
				except ValueError:
					print('We can\'t get time for this point. try -nt option.')
					sys.exit(1)
			final_file.write('\t</trkpt>\n')
		points_counter += 1


	final_file.write('</trkseg>\n')
	final_file.write('</trk>\n')
	final_file.write(FOOT_FILE)
	final_file.close()
	print("Info: Activity {0} = {1} points in track. file: {2}".format(str(activity_id),len(points),output_file))


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Download GPS Traces from Strava.',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-a','--activity' , metavar='ID_Number',type=int, help='ID of activity to download')
	parser.add_argument('-ai','--activityinterval' , nargs=2,metavar=('IDstart', 'IDend'),type=int,default=('None','None'), help='A interval of activities. auto outputname, not compatible with output name file option')
	parser.add_argument('-o','--output'   , metavar='output.gpx',default=DEFAULT_OUTPUT_FILE, help='name of GPX file output.')
	parser.add_argument('-l','--login', nargs=2,metavar=('username', 'password'),default=('None','None'), help='login with username and password')
	parser.add_argument('-fl','--forcelogin'	, help='Force a new login instead saved cookies. Warning, this option will destroy old credentials.'
												, action='store_true')
	parser.add_argument('-nt','--notime', help='download track without time parameters', action='store_true')
	parser.add_argument('-v','--verbose', help='increase output verbosity', action='store_true')
	args = parser.parse_args()

	login_username=args.login[0]
	login_password=args.login[1]
	output_file=args.output
	login_ok=0
	user_login = Login(args.verbose)

	if args.forcelogin:
		user_login.forcelogin(login_username)

	if str(args.activity) == 'None' and str(args.activityinterval[0]) == 'None':	
		parser.print_help()
		sys.exit("you must define -a or -ai")

        
	if(str(args.activity) != 'None'):
		activityinterval_start = args.activity
		activityinterval_stop =  args.activity
	else:
		if(str(args.activityinterval[0]) != 'None'):
			print("WARNING: Download a lot of activities is activated. USE this option carefully.")	
			activityinterval_start = args.activityinterval[0]
			activityinterval_stop  = args.activityinterval[1]	

	if login_username != 'None':
		if user_login.login(str(login_username),str(login_password)):
			print("Info: LOGIN OK.")
			login_ok=1
		else:
			print("Warning: LOGIN FAIL!")
			login_ok=0

	else:
		print("Warning: USER NOT LOGIN, without login only we get traces in a very low quality.")
		login_ok=0
        
	#re add session var after login.
	session = user_login.LOGIN_SESSION 

	for activity_id_temp in range (activityinterval_start, activityinterval_stop+1):
		try:
			if(str(args.activityinterval[0]) != 'None'):
				output_file = str(activity_id_temp)+".gpx"

			params = urllib.parse.urlencode([('streams[]', 'latlng'), ('streams[]', 'altitude'), ('streams[]', 'time')])

			started_unix_time = 0

			if login_ok > 0:
				#debug
				if args.verbose:
					print('getting track data:'+str(STRAVA_PATH_STREAM)+str(activity_id_temp)+'/streams?'+params)

				query = session.get(STRAVA_PATH_STREAM +str(activity_id_temp)+'/streams?'+ params).text
				
				#debug
				if args.verbose:
					print('getting starting date:'+str(STRAVA_ACTIVITIES_SESSION)+str(activity_id_temp))

				r = session.get(STRAVA_ACTIVITIES_SESSION +str(activity_id_temp))
				indice_inicio_linea =r.text.find('<time>')
				indice_fin_linea=r.text[indice_inicio_linea:(indice_inicio_linea+100)].find('</time>')
				started_date=r.text[indice_inicio_linea+7:indice_inicio_linea+indice_fin_linea]
				started_date= dateutil.parser.parse(started_date, dayfirst=True).timestamp()

				#debug
				if args.verbose:
					print('startDateLocal:'+str(started_date))

				started_unix_time = started_date
				
				query = json.loads(query)

			else:
				#debug
				if args.verbose:
					print('getting track data:'+str(STRAVA_PATH_STREAM)+str(activity_id_temp))

				http = urllib3.PoolManager()
				query = http.request('GET',STRAVA_PATH_STREAM +str(activity_id_temp))

				if query.status == 429:
					raise Exception("Too many Request from Strava. Try again later.")
					

				query = query.data.decode('utf-8')
					
				public_data = BeautifulSoup(query, 'html.parser')
				public_data_details = public_data.find('div', attrs={'data-react-class':'ActivityPublic'})
				public_data_streams = public_data_details.attrs.get('data-react-props')
				
				query= json.loads(public_data_streams)
				query= query['activity']['streams']

				print("Warning: I can't get started date, so 1970 is setted, please check the file.")
				query['time']=dict.fromkeys(range(len(query['altitude'])),0)
				

			if 'latlng' in query.keys():
				save_as_gpx(activity_id_temp, query['latlng'], query['altitude'], query['time'],started_unix_time, output_file)
			else:
				print("Info: No data for Activity {0}", format(activity_id_temp))

			
		except (KeyboardInterrupt, SystemExit):
			sys.exit()
		except Exception:
			print("Info: Can not get data for "+format(activity_id_temp))
			traceback.print_exc()
