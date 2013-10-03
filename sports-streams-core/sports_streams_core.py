import re, urlparse, string, datetime
import sports_streams_objects as core
from dateutil import parser
from dateutil import tz

###############################################

# NOTHING SPORT SPECIFIC SHOULD GO IN HERE.  
# THE CODE SHOULD BE REUSABLE REGARDLESS OF THE SPORT.

SEARCH_URL = "http://www.reddit.com/r/Sports_Streams/search.rss?q={sport}&sort=new&t=week&restrict_sr=on"
QUALITY_MARKER = "{q}" 

STREAM_AVAILABLE_MINUTES_BEFORE = 20
STREAM_HIDDEN_AFTER = 360 # 6 hours oughta be plenty...

CONFIG = None

###############################################

# This method should be called first by sport plugins.
def Init(title, sportKeyword, streamFormat, teamNames):
	Log.Debug("Core.Init()")
	global CONFIG
	CONFIG = core.Config(title, sportKeyword, streamFormat, teamNames)
	

class NotAvailableException(Exception):
	pass
	
	Minutes = STREAM_AVAILABLE_MINUTES_BEFORE
	
	
###############################################	

def BuildMainMenu(container, streamCallBack):
	
	items = GetGameList()
	
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
		
		away = CONFIG.Teams[item.AwayCity]["City"] + " " + CONFIG.Teams[item.AwayCity]["Name"]
		home = CONFIG.Teams[item.HomeCity]["City"] + " " + CONFIG.Teams[item.HomeCity]["Name"]

		title = str(matchupFormat).replace("{away}", away).replace("{home}", home).replace("{time}", localStart)
		summary = str(summaryFormat).replace("{away}", away).replace("{home}", home).replace("{time}", localStart)
		container.add(DirectoryObject(
			key = Callback(streamCallBack, gameId = item.ID, title = title),
			title = title,
			summary = summary
		))
		
		 
	# display empty message
	if len(container) == 0: 
		Log.Debug("no games")
		return ObjectContainer(header=L("MainMenuTitle"), message=L("ErrorNoGames")) 

	Log.Debug("Request from platform: " + Client.Platform)
	if NeedsPreferencesItem():
		Log.Debug("Adding preferences menu item")
		container.add(PrefsObject(title="Preferences", summary="Change the stream bitrate.", thumb=R("icon-prefs.png")))

	
def BuildStreamMenu(container, gameId):
		
	streams, available = GetGameStreams(gameId, CONFIG.StreamFormat)
	
	quality = Prefs["videoQuality"]
	
	if not available:
		raise NotAvailableException

	for stream in streams:
		stream.Url = stream.Url.replace(QUALITY_MARKER, quality)
		team = CONFIG.Teams[stream.Team]["Name"]
		container.add(VideoClipObject(
			url = stream.Url,
			title = str(stream.Title).replace("{city}", team),
			thumb = CONFIG.Teams[stream.Team]["Logo"]
		))
	
	
	
def NeedsPreferencesItem():
	# Rather than only show it for some items, we'll show for all and hide for some.
	# The list of those that don't need it is probably shorter and doesn't include hard to predict ones like browers
	if Client.Platform in [ClientPlatform.iOS, ClientPlatform.Android]:
		return False
	else:
		return True

def GetGameList():

	#Log.Debug("GetGameList()")
	
	# thedate = datetime.datetime.now()
	# year = thedate.strftime("%Y")
	# month = thedate.strftime("%m")
	# day = thedate.strftime("%d")
	#stupid osx doesn't have .format available....	
	Log.Debug("Searching for: " + CONFIG.SportKeyword)
	url = SEARCH_URL.replace("{sport}", CONFIG.SportKeyword)
	
	#Log.Debug(url)
	
	#try:
	threadList = XML.ElementFromURL(url, cacheTime=None)
	#except:
		# reddit down likely
	#	return itemList
	
	items = threadList.xpath("//item")
	
	if len(items) == 0:
		# no threads in past week
		return []
		
	# we're only concerned with the most recent game
	item = items[0]
	threadUrl = item.xpath("./link/text()")[0]
	
	#Log.Debug("Opening thread: " + threadUrl)
	
	thread = XML.ElementFromURL(threadUrl + ".rss")
	selfPost = thread.xpath("//item")[0]
	Log.Debug("selfPost: " + selfPost.xpath("./description/text()")[0])
	description = HTML.ElementFromString(selfPost.xpath("./description/text()")[0])
	
	gamesXml = XML.ElementFromString(description.xpath("//p/text()")[0])
	#cache xml
	#This gets cached so we don't need to reload the XML when we open the game menu
	#We reload it each time we open the main menu, to avoid an out of date game list
	#Should probably read from the cache for a certain time period as well, since the games only change once per day.
	Data.Save("games", XML.StringFromElement(gamesXml))
	
	return GamesXmlToList(gamesXml)
	
def GamesXmlToList(xml):	
	list = []
		  
	#I should cache this data for the next calls...
	for game in xml.xpath("//game"): 
		gameId = GetSingleXmlValue(game, "./@id") 
		utcStartString = GetSingleXmlValue(game, "./utcStart/text()") #2013-05-18 17:00:00+0000
		#Log.Debug("utc string: " + utcStartString)
		#utcStart = datetime.datetime.strptime(utcStartString, "%Y-%m-%d %H:%M:%S%z")
		utcStart = parser.parse(utcStartString)
		# set timezone
		#utcStart = utcStart.replace(tzinfo=UTC)
		#utcStart.tzinfo = UTC 
		#Log.Debug("utc date: " + str(utcStart))
		homeCity = GetSingleXmlValue(game, "./homeTeam/@city")
		homeStreamName = GetSingleXmlValue(game, "./homeTeam/@streamName")
		awayCity = GetSingleXmlValue(game, "./awayTeam/@city")
		awayStreamName = GetSingleXmlValue(game, "./awayTeam/@streamName")
		homeServer = GetSingleXmlValue(game, "./homeTeam/@server")
		awayServer = GetSingleXmlValue(game, "./awayTeam/@server")  
		#Log.Debug("gameID: " + gameId)
		
		# only add if the start time is within a reasonable window
		minutesToStart = GetMinutesToStart(utcStart)
		if minutesToStart > STREAM_HIDDEN_AFTER * -1: # -1 in the past			
			list.append(core.Game(gameId, utcStart, homeCity, awayCity, homeServer, awayServer, homeStreamName, awayStreamName))
	
	return list
	
	
def GetSingleXmlValue(element, xpath):
	match = element.xpath(xpath)
	
	if len(match) > 0:
		return match[0]
	elif len(match) > 1:
		raise Exception("found " + str(len(match)) + " elements where 1 was expected")
	else:
		return ""
		

def GetMinutesToStart(utcStart):
	#Python's date handling is horrifically bad.
	gameStart = utcStart.replace(tzinfo = None) - datetime.datetime.utcnow()
	# to get a logical representation of how long in the future or past the game was, I have to do all this ridiculous math...
	minutesToStart = ((gameStart.microseconds + (gameStart.seconds + gameStart.days * 24 * 3600) * 10**6) / 10.0**6) / 60
	
	return minutesToStart
	
		
def GetGameStreams(gameId, stream_format):
 
	xml = XML.ElementFromString(Data.Load("games"))
	games = GamesXmlToList(xml)
	 
	streams = []
	UTC = tz.gettz("UTC")
	
	for game in filter(lambda g: g.ID == gameId, games):
		minutesToStart = GetMinutesToStart(game.UtcStart)
		Log.Debug("game starts in: " + str(minutesToStart))
		
		available = minutesToStart <= STREAM_AVAILABLE_MINUTES_BEFORE
				  
		if game.HomeServer != "":
			title = str(L("HomeStreamLabelFormat"))
			url = stream_format.replace("{server}", game.HomeServer).replace("{streamName}", game.HomeStreamName)
			Log.Debug("url: " + url)
			streams.append(core.Stream(title, url, game.HomeCity, available))
			
		if game.AwayServer != "":
			title = str(L("AwayStreamLabelFormat"))
			url = stream_format.replace("{server}", game.AwayServer).replace("{streamName}",game.AwayStreamName)
			Log.Debug("url: " + url)
			streams.append(core.Stream(title, url, game.AwayCity, available))
		
	return streams, available
	
