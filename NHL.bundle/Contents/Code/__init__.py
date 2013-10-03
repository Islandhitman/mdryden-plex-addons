import sports_streams_core as core
import teams
import datetime
from dateutil import tz

###############################################

VIDEO_PREFIX = "/video/nhl"

NAME = "NHL"

ART = 'art-default.png'
ICON = 'icon-default.png'

SPORT_KEYWORD = "hockey"
STREAM_FORMAT = "http://nlds{server}.cdnak.neulion.com/nlds/nhl/{streamName}/as/live/{streamName}_hd_{q}.m3u8"


###############################################

# This function is initially called by PMS to inialize the plugin

def Start():

	# Initialize the plugin
	Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("LIST", viewMode = "List", mediaType = "items")
	
	ObjectContainer.title1 = NAME
	
	core.Init(NAME, SPORT_KEYWORD, STREAM_FORMAT, teams.TEAMS)
	
	Log.Debug("Plugin Start")

def MainMenu():
	dir = ObjectContainer(title2 = Locale.LocalString("MainMenuTitle"), art=R("art-default.png"))
	
	core.BuildMainMenu(dir, StreamMenu)
	
	return dir
	 	
		 
def StreamMenu(gameId, title):
	dir = ObjectContainer(title2 = title, art=R(ICON))
	
	try:
		core.BuildStreamMenu(dir, gameId)	
	except core.NotAvailableException as ex:
		message = str(L("ErrorStreamsNotReady")).replace("{minutes}", str(ex.Minutes))
		return ObjectContainer(header=L("MainMenuTitle"), message=message)	
	
	return dir
	
	