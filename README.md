Strava hacks script collection
===============================

I will uploading here my collections of scripts to get some hacks from Strava.... for python3

## Installing on MacOSX
    sudo easy_install pip
    sudo pip install -r requirements.txt

## Installing on Ubuntu/Debian
    
    sudo apt install python3
    sudo apt install python3-pip
    sudo pip3 install -r requirements.txt
    
### strava_traces_downloader.py

with this script you can reconstruct a gpx file from the public strava activity information. without premium account or any else. 

This script **doesn't download the original GPX file**.  is just some a reconstruction, and is not better than the original GPX File.

Sometimes, When you aren't logged, and the activity is public, we can get 100 points only. Is not bad, but when you are logged and the activities is from a friend, we can get thousands of points (resulting a better GPX file). 


    usage: strava_traces_downloader.py [-h] [-a ID_Number] [-ai IDstart IDend]
                                       [-o output.gpx] [-l username password]
                                       [-nt] [-v]
    
    Download GPS Traces from Strava.
        
    optional arguments:
      -h, --help            show this help message and exit
      -a ID_Number, --activity ID_Number
                            ID of activity to download (default: None)
      -ai IDstart IDend, --activityinterval IDstart IDend
                            A interval of activities. auto outputname, not
                            compatible with output name file option (default:
                            ('None', 'None'))
      -o output.gpx, --output output.gpx
                            name of GPX file output. (default: output.gpx)
      -l username password, --login username password
                            login with username and password (default: ('None',
                            'None'))
      -nt, --notime         download track without time parameters (default:
                            False)
      -v, --verbose         increase output verbosity (default: False)

**EXAMPLES**

Download a simple activity 

    python strava_traces_downloader.py -a activitynumber -l youremail@domain.org yourpassword -o fileoutput.gpx

Download multiple activities

    python strava_traces_downloader.py -ai 427796872 427796999 -l youremail@domain.org yourpassword                   


### join_gpx_strava_files.py

a fast way to join a lot of GPX files downloaded from strava if you use strava_traces_downloader.py , this is your second step for join  all in just one file. 

    python join_gpx_strava_files.py [gpx_directory] [outputfile.gpx]

### strava_kudos_tool.py

This script can help you to give a lot kudos for your friends.
                        
                        
    usage: strava_kudos_tool.py [-h] [-a ID_Number] [-fd UNIX_TIME] -l username password [-fl] [-nebr Number] [-ft FeedType] [-c CLUB_ID] [-v]

    Strava Kudos Tool.

    options:
    -h, --help            show this help message and exit
    -a ID_Number, --athlete ID_Number
                            Filter by ID of Athlete to analyze, by default all feed is analyzed. (default: None)
    -fd UNIX_TIME, --feeddeep UNIX_TIME
                            Force a end of time for get the feed, define a UNIX TIME (default: None)
    -l username password, --login username password
                            Login with username and password (default: ('None', 'None'))
    -fl, --forcelogin     Force a new login instead saved cookies. Warning, this option will destroy old credentials.
                            (default: False)
    -nebr Number, --numentriesbyrequest Number
                            Number of entries asked for each request, by default this value is controlled by Strava. If
                            even set a big number, strava could rewrite it with the max value from server. (100 entries)
                            (default: 0)
    -ft FeedType, --feedtype FeedType
                            Force a filter by feed type, by default this value is controlled by Strava (default: None)
    -c CLUB_ID, --club CLUB_ID
                            Use it with -ft option when 'club' feed type is used. (default: None)
    -y, --yes             yes to all (default: False)
    -v, --verbose         increase output verbosity (default: False)

**EXAMPLES**

Give kudos for all your following feed.

    python strava_kudos_tool.py -l youremail@domain.org yourpassword

Give kudos for all activities in a specific club.

    python strava_kudos_tool.py -l youremail@domain.org yourpassword -ft club -c 12345678

### strava_photo_downloader.py

Do you want to download all photos of your friends? no problem. 

    usage: strava_photo_downloader.py [-h] -a ID_Number -l username password [-fl] [-y] [-v]
    
    Strava Photo Downloader Tool.
    
    options:
      -h, --help            show this help message and exit
      -a ID_Number, --athlete ID_Number
                            ID of Athlete to analyze (default: None)
      -l username password, --login username password
                            Login with username and password (default: ('None', 'None'))
      -fl, --forcelogin     Force a new login instead saved cookies. Warning, this option will destroy old credentials. (default: False)
      -y, --yes             Yes to all (default: False)
      -v, --verbose         increase output verbosity (default: False)

**EXAMPLES**

Download all photos of a friend from the feed

    python strava_photo_downloader.py -l youremail@domain.org yourpassword -a 12345678
