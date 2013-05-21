import core, hockey, basketball, datetime
from dateutil import tz

###############################################

VIDEO_PREFIX = "/video/redditsports"

NAME = "Reddit Sports"

ART = 'art-default.png'
ICON = 'icon-default.png'


# address should not start with a slash
# keywords should be url encoded
SPORTS = { 
	"Hockey": {
		"sport":"Hockey",
		#"formatTitleFunction":hockey.FormatTitle
		},
	"Basketball": {
		"sport":"Basketball"
		#"formatTitleFunction":basketball.FormatTitle
		}
	}

###############################################

# This function is initially called by PMS to inialize the plugin

def Start():

	# Initialize the plugin
	Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("LIST", viewMode = "List", mediaType = "items")
	
	ObjectContainer.title1 = NAME
	
	Log.Debug("Plugin Start")
	

def MainMenu():
	dir = ObjectContainer(title2 = Locale.LocalString("MainMenuTitle"))
	
	for item in SPORTS:
		Log.Debug(item)
		sport = SPORTS[item]["sport"]
		dir.add(DirectoryObject(
				key = Callback(SportMenu, sport = sport),
				title = Locale.LocalString(sport + "Title"),
				summary = Locale.LocalString(sport + "Summary")
			))
	
	return dir
	 
	
def SportMenu(sport):
	
	dir = ObjectContainer(title2 = Locale.LocalString(sport + "Title")) 
	
	items = core.GetGameList(sport)
	
	HERE = tz.tzlocal()
	UTC = tz.gettz("UTC")
	  
	for item in items:
		#todo: format in module
		Log.Debug("utcStart: " + str(item.UtcStart))
		localStart = item.UtcStart.astimezone(HERE).strftime("%H:%M")
		Log.Debug("localStart: " + str(localStart))
		
		# make sure that we are within X minutes of game time so the stream will be active
		#timeDiff = item.UtcStart - datetime.datetime.utcnow()
		#Log.Debug("time diff: " + str(timeDiff))
		
		title = str(L("MatchupFormat")).replace("{away}", item.AwayCity).replace("{home}", item.HomeCity).replace("{time}", localStart)
		summary = "summary goes here"
		dir.add(DirectoryObject(
			key = Callback(StreamMenu, sport = sport, gameId = item.ID, title = title),
			title = title,
			summary = summary
		))
		
		 
	# display empty message
	if len(dir) == 0: 
		Log.Debug("no games")
		return ObjectContainer(header=L(sport + "Title"), message=L("ErrorNoGames")) 
		
	return dir
	
		 
def StreamMenu(sport, gameId, title):
	dir = ObjectContainer(title2 = title)
	
	streams, available = core.GetGameStreams(sport, gameId)
	
	quality = Prefs["videoQuality"]
	
	if not available:
		message = str(L("ErrorStreamsNotReady")).replace("{minutes}", str(core.STREAM_AVAILABLE_MINUTES_BEFORE))
		return ObjectContainer(header=L(sport + "Title"), message=message)	
	
	for stream in streams:
	
		stream.Url = stream.Url.replace(core.QUALITY_MARKER, quality)
		dir.add(VideoClipObject(
			url = stream.Url,
			title = stream.Title,
		))
	
	return dir
	