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

HEAD_FILE="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\" ?>\n \
<gpx xmlns=\"http://www.topografix.com/GPX/1/1\" creator=\"\" version=\"1.1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd\">\n"   
FOOT_FILE="</gpx>"

DEFAULT_OUTPUT_FILE='output.gpx'


def save_as_gpx(activity_id,points, output_file):

	 print("Info: {0} points in track.".format(len(points)))

	 final_file = open(output_file, 'w')
	 final_file.write(HEAD_FILE)
	 final_file.write('<trk>\n')
	 final_file.write('<name> Activity '+str(activity_id)+'</name>\n')
	 final_file.write('<trkseg>\n')

	 for point in points:
		final_file.write('<trkpt lat="'+str(point[0])+'"'+' lon="'+str(point[1])+'">'+'</trkpt>\n')

	 final_file.write('</trkseg>\n')
	 final_file.write('</trk>\n')
	 final_file.write(FOOT_FILE)
  	 final_file.close()

	 print("file "+output_file+" saved.")


if __name__ == '__main__':

 	parser = argparse.ArgumentParser(description='Download GPS Traces from Strava.',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-a','--activity' , metavar='ID_Number',type=int,required=True, help='ID of activity to download')
	parser.add_argument('-o','--output'   , metavar='output.gpx',default=DEFAULT_OUTPUT_FILE, help='name of GPX file output.')
	parser.add_argument('-l','--login', nargs=2,metavar=('username', 'password'), help='login with username and password')
	args = parser.parse_args()

	activity_id=args.activity
	output_file=args.output
	login_username=args.login[0]
	login_password=args.login[1]

	login=0

	if login_username != 'None':
		
		# Start a session so we can have persistant cookies
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
		print r
		
		# Try accessing a page that requires you to be logged in
		r = session.get('https://www.strava.com/dashboard')

		if int(r.text.find(STRAVA_LOGGED_OUT_FINGERPRINT)) >= 0:
			print("Warning: LOGIN FAIL!")
			login=0
		else:
			login=1
		#print(r.text)
		#print(session)
        else:
		print("Warning: USER NOT LOGIN, without login only we get traces in a very low quality.")
    		user_filter = USER_FILTER
		login=0
        

	if login > 0:
		params = urllib.urlencode(zip(['streams[]'],['latlng']))
		query = session.get(STRAVA_PATH_STREAM +str(activity_id)+'?'+ params).text
		query = json.loads(query)
	else:
		params = urllib.urlencode(zip(['streams[]'],['latlng']))
		query = urllib2.urlopen(STRAVA_PATH_STREAM +str(activity_id)+'?'+ params).read()
		query = json.loads(query)
	
	save_as_gpx(activity_id, query['latlng'], output_file)



