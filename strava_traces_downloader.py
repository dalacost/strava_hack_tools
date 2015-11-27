import sys
import urllib2, urllib
import json
import os
import shutil
import socket
import time
import datetime
from datetime import timedelta
import argparse
import requests

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


STRAVA_PATH_STREAM = 'http://www.strava.com/stream/'
STRAVA_URL_LOGIN = 'https://www.strava.com/login'
STRAVA_URL_SESSION = 'https://www.strava.com/session'
STRAVA_LOGGED_OUT_FINGERPRINT = 'logged-out'
DEFAULT_OUTPUT_FILE='output.gpx'

#GPX Format
HEAD_FILE="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\" ?>\n \
<gpx xmlns=\"http://www.topografix.com/GPX/1/1\" creator=\"\" version=\"1.1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd\">\n"   
FOOT_FILE="</gpx>"


#global session var
LOGIN_SESSION = ''

def save_as_gpx(activity_id,points,elevation_points, time_points, output_file):

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
#			final_file.write('\t\t<time>'+str(time_points[points_counter])+'</time>\n')
			final_file.write('\t</trkpt>\n')
		points_counter += 1


	 final_file.write('</trkseg>\n')
	 final_file.write('</trk>\n')
	 final_file.write(FOOT_FILE)
  	 final_file.close()
 	 print("Info: Activity {0} = {1} points in track. file: {2}".format(str(activity_id),len(points),output_file))

def login(login_username, login_password):
	# Start a session so we can have persistant cookies
	global LOGIN_SESSION
	session = requests.session()
	r = session.get(STRAVA_URL_LOGIN)
	indice_final_linea =r.text.find('name=\"csrf-token\"')
	indice_inicio_linea=r.text[1:indice_final_linea].rfind('<meta')
	index1=r.text[indice_inicio_linea:indice_final_linea].find('\"')
	authenticity_token = r.text[index1+indice_inicio_linea:indice_final_linea].strip().strip('\"')

	# This is the form data that the page sends when logging in
	login_data = {
		'email': login_username,
		'password': login_password,
		'utf8': '%E2%9C%93',
		'authenticity_token':authenticity_token
	}

	# Authenticate
	r = session.post(STRAVA_URL_SESSION, data=login_data)
	#print r
	
	# Try accessing a page that requires you to be logged in
	r = session.get('https://www.strava.com/dashboard')

	LOGIN_SESSION = session

	if int(r.text.find(STRAVA_LOGGED_OUT_FINGERPRINT)) >= 0:
		return False
	else:
		return True
	#print(r.text)
	#print(session)

	
if __name__ == '__main__':

 	parser = argparse.ArgumentParser(description='Download GPS Traces from Strava.',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-a','--activity' , metavar='ID_Number',type=int, help='ID of activity to download')
	parser.add_argument('-ai','--activityinterval' , nargs=2,metavar=('IDstart', 'IDend'),type=int,default=('None','None'), help='A interval of activities. auto outputname, not compatible with output name file option')
	parser.add_argument('-o','--output'   , metavar='output.gpx',default=DEFAULT_OUTPUT_FILE, help='name of GPX file output.')
	parser.add_argument('-l','--login', nargs=2,metavar=('username', 'password'),default=('None','None'), help='login with username and password')
	parser.add_argument('-v','--verbose', help='increase output verbosity', action='store_true')
	args = parser.parse_args()

        login_username=args.login[0]
	login_password=args.login[1]
	output_file=args.output
	login_ok=0


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
		if login(str(login_username),str(login_password)):
			print("Info: LOGIN OK.")
			login_ok=1
		else:
			print("Warning: LOGIN FAIL!")
			login_ok=0

        else:
		print("Warning: USER NOT LOGIN, without login only we get traces in a very low quality.")
#    		user_filter = USER_FILTER
		login_ok=0
        
	#re add session var after login.
	session = LOGIN_SESSION 

	for activity_id_temp in range (activityinterval_start, activityinterval_stop+1):
	    try:
		if(str(args.activityinterval[0]) != 'None'):
			output_file = str(activity_id_temp)+".gpx"

#		params = urllib.urlencode([('streams[]', 'latlng'), ('streams[]', 'altitude'), ('streams[]', 'distance'), ('streams[]', 'time')])
		params = urllib.urlencode([('streams[]', 'latlng'), ('streams[]', 'altitude'), ('streams[]', 'time')])

		if login_ok > 0:			
			query = session.get(STRAVA_PATH_STREAM +str(activity_id_temp)+'?'+ params).text
			#debug 
			if args.verbose:
			   print "url:"+STRAVA_PATH_STREAM +str(activity_id_temp)+'?'+ params
		else:
			query = urllib2.urlopen(STRAVA_PATH_STREAM +str(activity_id_temp)+'?'+ params).read()
			#debug 
			if args.verbose:
			   print "url:"+STRAVA_PATH_STREAM +str(activity_id_temp)+'?'+ params

		query = json.loads(query)
		if 'latlng' in query.keys():
			save_as_gpx(activity_id_temp, query['latlng'], query['altitude'], query['time'], output_file)
		else:
			 print("Info: No data for Activity {0}", format(activity_id_temp))
	    except (KeyboardInterrupt, SystemExit):
                sys.exit()
            except:
                print "Info: Can not get data for "+format(activity_id_temp)
