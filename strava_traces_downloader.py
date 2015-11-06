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
	parser.add_argument('-o','--output' , metavar='output.gpx',default=DEFAULT_OUTPUT_FILE, help='name of GPX file output.')
	args = parser.parse_args()

	activity_id=args.activity
	output_file=args.output

	params = urllib.urlencode(zip(['streams[]'],['latlng']))
	query = urllib2.urlopen(STRAVA_PATH_STREAM +str(activity_id)+'?'+ params).read()
	query = json.loads(query)
	
	save_as_gpx(activity_id, query['latlng'], output_file)



