import sports_streams_core as core
import datetime
from dateutil import tz

###############################################

VIDEO_PREFIX = "/video/nhl"

NAME = "NHL"

ART = 'art-default.png'
ICON = 'icon-default.png'

SPORT_KEYWORD = "hockey"
STREAM_FORMAT = "http://nlds{server}.cdnak.neulion.com/nlds/nhl/{streamName}/as/live/{streamName}_hd_{q}.m3u8"

TEAMS = {
	"ANA": { "City": "Anaheim", "Name": "Ducks", "Logo": R("Team_ANA.jpg") },
	"BOS": { "City": "Boston", "Name": " Bruins", "Logo": R("Team_BOS.jpg") },
	"BUF": { "City": "Buffalo", "Name": " Sabres", "Logo": R("Team_BUF.jpg") },
	"CAR": { "City": "Carolina", "Name": " Hurricanes", "Logo": R("Team_CAR.jpg") },
	"CBS": { "City": "Columbus", "Name": " Blue Jackets", "Logo": R("Team_CBS.jpg") },
	"CGY": { "City": "Calgary", "Name": " Flames", "Logo": R("Team_CGY.jpg") },
	"CHI": { "City": "Chicago", "Name": " Blackhawks", "Logo": R("Team_CHI.jpg") },
	"COL": { "City": "Colorado", "Name": " Avalanche", "Logo": R("Team_COL.jpg") },
	"DAL": { "City": "Dallas", "Name": " Stars", "Logo": R("Team_DAL.jpg") },
	"DET": { "City": "Detroit", "Name": " Red Wings", "Logo": R("Team_DET.jpg") },
	"EDM": { "City": "Edmonton", "Name": " Oilers", "Logo": R("Team_EDM.jpg") },
	"FLA": { "City": "Florida", "Name": " Panthers", "Logo": R("Team_FLA.jpg") },
	"LOS": { "City": "Los Angeles", "Name": " Kings", "Logo": R("Team_LOS.jpg") },
	"MIN": { "City": "Minnesota", "Name": " Wild", "Logo": R("Team_MIN.jpg") },
	"MON": { "City": "Montreal", "Name": " Canadiens", "Logo": R("Team_MON.jpg") },
	"NJD": { "City": "New Jersey", "Name": " Devils", "Logo": R("Team_NJD.jpg") },
	"NSH": { "City": "Nashville", "Name": " Predators", "Logo": R("Team_NSH.jpg") },
	"NYI": { "City": "NY", "Name": " Islanders", "Logo": R("Team_NYI.jpg") },
	"NYR": { "City": "NY", "Name": " Rangers", "Logo": R("Team_NYR.jpg") },
	"OTT": { "City": "Ottawa", "Name": " Senators", "Logo": R("Team_OTT.jpg") },
	"PHI": { "City": "Philadelphia", "Name": " Flyers", "Logo": R("Team_PHI.jpg") },
	"PHX": { "City": "Phoenix", "Name": " Coyotes", "Logo": R("Team_PHX.jpg") },
	"PIT": { "City": "Pittsburgh", "Name": " Penguins", "Logo": R("Team_PIT.jpg") },
	"SAN": { "City": "San Jose", "Name": " Sharks", "Logo": R("Team_SAN.jpg") },
	"STL": { "City": "St. Louis", "Name": " Blues", "Logo": R("Team_STL.jpg") },
	"TAM": { "City": "Tampa Bay", "Name": " Lightning", "Logo": R("Team_TAM.jpg") },
	"TOR": { "City": "Toronto", "Name": " Maple Leafs", "Logo": R("Team_TOR.jpg") },
	"VAN": { "City": "Vancouver", "Name": " Canucks", "Logo": R("Team_VAN.jpg") },
	"WPG": { "City": "Winnipeg", "Name": " Jets", "Logo": R("Team_WPG.jpg") },
	"WSH": { "City": "Washington", "Name": " Capitals", "Logo": R("Team_WSH.jpg") }
}

###############################################

# This function is initially called by PMS to inialize the plugin

def Start():

	# Initialize the plugin
	Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("LIST", viewMode = "List", mediaType = "items")
	
	ObjectContainer.title1 = NAME
	
	core.Init(NAME, SPORT_KEYWORD, STREAM_FORMAT, TEAMS)
	
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
	
	