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
		"stream_format":"http://nlds{server}.cdnak.neulion.com/nlds/nhl/{streamName}/as/live/{streamName}_hd_{q}.m3u8",
		"team_names": hockey.TEAMS
		}#,
	#"Basketball": {
	#	"sport":"Basketball",
	#	#"formatTitleFunction":basketball.FormatTitle
	#	"stream_format":"http://nlds{server}.cdnak.neulion.com/nlds/nba/{streamName}/as/live/{streamName}_hd_{q}.m3u8"
	#	}
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
	dir = ObjectContainer(title2 = Locale.LocalString("MainMenuTitle"), art=R("art-default.png"))
	
	for item in SPORTS:
		Log.Debug(item)
		sport = SPORTS[item]["sport"]
		dir.add(DirectoryObject(
				key = Callback(SportMenu, sport = sport),
				title = Locale.LocalString(sport + "Title"),
				summary = Locale.LocalString(sport + "Summary"),
				thumb = R(sport+".jpg")
			))

	Log.Debug("Request from platform: " + Client.Platform)
	if Client.Platform in [ClientPlatform.MacOSX, ClientPlatform.Linux, ClientPlatform.Windows]:
		dir.add(PrefsObject(title="Preferences", summary="Change the stream bitrate.", thumb=R("icon-prefs.png")))
	
	return dir
	 
	
def SportMenu(sport):
	
	dir = ObjectContainer(title2 = Locale.LocalString(sport + "Title"), art=R(sport+".jpg")) 
	
	items = core.GetGameList(sport)
	
	HERE = tz.tzlocal()
	UTC = tz.gettz("UTC")

	CLIENT_OS =  Client.Platform
	matchupFormat = L("MatchupFormat" + CLIENT_OS)
	if str(matchupFormat) == "MatchupFormat" + CLIENT_OS:
		# No client specific MatchupFormat, fallback to default
		matchupFormat = L("MatchupFormat")
	summaryFormat = L("SummaryFormat" + CLIENT_OS)
	if str(summaryFormat) == "SummaryFormat" + CLIENT_OS:
		# No client specific SummaryFormat, fallback to default
		summaryFormat = L("SummaryFormat")
	  
	for item in items:
		#todo: format in module
		Log.Debug("utcStart: " + str(item.UtcStart))
		localStart = item.UtcStart.astimezone(HERE).strftime("%H:%M")
		Log.Debug("localStart: " + str(localStart))
		
		# make sure that we are within X minutes of game time so the stream will be active
		#timeDiff = item.UtcStart - datetime.datetime.utcnow()
		#Log.Debug("time diff: " + str(timeDiff))

		away = item.AwayCity
		home = item.HomeCity
		if "team_names" in SPORTS[sport]:
			away = SPORTS[sport]["team_names"][away][0] + " " + SPORTS[sport]["team_names"][away][1]
			home = SPORTS[sport]["team_names"][home][0] + " " + SPORTS[sport]["team_names"][home][1]

		title = str(matchupFormat).replace("{away}", away).replace("{home}", home).replace("{time}", localStart)
		summary = str(summaryFormat).replace("{away}", away).replace("{home}", home).replace("{time}", localStart)
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
	dir = ObjectContainer(title2 = title, art=R(sport+".jpg"))
	
	config = SPORTS[sport]
	
	streams, available = core.GetGameStreams(sport, gameId, config["stream_format"])
	
	quality = Prefs["videoQuality"]
	
	if not available:
		message = str(L("ErrorStreamsNotReady")).replace("{minutes}", str(core.STREAM_AVAILABLE_MINUTES_BEFORE))
		return ObjectContainer(header=L(sport + "Title"), message=message)	

	for stream in streams:
		stream.Url = stream.Url.replace(core.QUALITY_MARKER, quality)
		team = stream.Team
		if "team_names" in SPORTS[sport]:
			team = SPORTS[sport]["team_names"][team][1]
		dir.add(VideoClipObject(
			url = stream.Url,
			title = str(stream.Title).replace("{city}", team),
			thumb = R(sport+"_"+stream.Team+".jpg"),
		))
	
	return dir
	