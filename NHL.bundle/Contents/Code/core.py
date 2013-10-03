import re, urlparse, string, datetime
from dateutil import parser
from dateutil import tz

###############################################

SEARCH_URL = "http://www.reddit.com/r/Sports_Streams/search.rss?q={sport}&sort=new&t=week&restrict_sr=on"

QUALITY_MARKER = "{q}" 

STREAM_AVAILABLE_MINUTES_BEFORE = 2000 
STREAM_HIDDEN_AFTER = 360 # 6 hours oughta be plenty...

###############################################

class Game:
	def __init__(self, id, utcStart, homeCity, awayCity, homeServer, awayServer, homeStreamName, awayStreamName):
		self.ID = id
		self.UtcStart = utcStart
		self.HomeCity = homeCity
		self.AwayCity = awayCity
		self.HomeServer = homeServer
		self.AwayServer = awayServer
		self.HomeStreamName = homeStreamName
		self.AwayStreamName = awayStreamName
		
# class Game:
	# def __init__(self, id, homeCity, awayCity):
		# self.ID = id
		# self.HomeCity = homeCity
		# self.AwayCity = awayCity
		
		
class Stream:
	def __init__(self, title, url, team, available):
		self.Title = title
		self.Url = url
		self.Team = team
		self.Available = available
	
###############################################	

def GetGameList(sport):

	#Log.Debug("GetGameList()")
	
	# thedate = datetime.datetime.now()
	# year = thedate.strftime("%Y")
	# month = thedate.strftime("%m")
	# day = thedate.strftime("%d")
	#stupid osx doesn't have .format available....	
	url = SEARCH_URL.replace("{sport}", sport)#, year, month, day)
	
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
	Data.Save(sport, XML.StringFromElement(gamesXml))
	
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
			list.append(Game(gameId, utcStart, homeCity, awayCity, homeServer, awayServer, homeStreamName, awayStreamName))
	
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
	
		
def GetGameStreams(sport, gameId, stream_format):
 
	xml = XML.ElementFromString(Data.Load(sport))
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
			streams.append(Stream(title, url, game.HomeCity, available))
			
		if game.AwayServer != "":
			title = str(L("AwayStreamLabelFormat"))
			url = stream_format.replace("{server}", game.AwayServer).replace("{streamName}",game.AwayStreamName)
			Log.Debug("url: " + url)
			streams.append(Stream(title, url, game.AwayCity, available))
		
	return streams, available
	
