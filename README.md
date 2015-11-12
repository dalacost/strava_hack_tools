Strava hacks script collection
===============================

I will uploading here my collections of scripts to get some hacks from Strava.... 

## Installing on MacOSX
    sudo pip install -r requirements.txt

### strava_traces_downloader.py

with this script you can reconstruct a gpx file from the public strava activity information. without premium account or any else. 

This script **doesn't download the original GPX file**.  is just some a reconstruction, and is not better than the original GPX File.

When you aren't logged, and the activity is public, we can get 100 points only. Is not bad, but when you are logged and the activities is from a friend, we can get thousands of points (resulting a better GPX file). 

    optional arguments:
      -h, --help            show this help message and exit
      -a ID_Number, --activity ID_Number
                            ID of activity to download (default: None)
      -ai IDstart IDend, --activityinterval IDstart IDend
                            A interval of activities. auto outputname, not
                            compatible with output name file option (default:
                            None)
      -o output.gpx, --output output.gpx
                            name of GPX file output. (default: output.gpx)
      -l username password, --login username password
                        login with username and password (default: None)

**EXAMPLES**

Download a simple activity 

    python strava_traces_downloader.py -a activitynumber -l youremail@domain.org yourpassword -o fileoutput.gpx                        


Download multiple activities

    python strava_traces_downloader.py -ai 427796872 427796999 -l youremail@domain.org yourpassword mapa1234

                        
                        

