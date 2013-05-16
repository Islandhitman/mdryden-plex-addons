import string, datetime


################################################

GAMES_URL_FORMAT = "http://smb.cdnak.neulion.com/fs/nba/feeds_s2012/schedule/{0}/{1}_{2}.js"

STREAM_FORMAT = "http://nlds{0}.cdnak.neulion.com/nldsdvr/nba/{1}/as/live/{1}_hd_(q).m3u8"

TEAMS = [
	#ATLANTIC
	"Boston Celtics",
	"Brooklyn Nets",
	"New York Knicks",
	"Philadelphia 76ers",
	"Toronto Raptors",
	#SOUTHWEST
	"Dallas Mavericks",
	"Houston Rockets",
	"Memphis Grizzlies",
	"New Orleans Pelicans",
	"San Antonio Spurs",
	#CENTRAL
	"Chicago Bulls",
	"Cleveland Cavaliers",
	"Detroit Pistons",
	"Indiana Pacers",
	"Milwaukee Bucks",
	#NORTHWEST
	"Denver Nuggets",
	"Minnesota Timberwolves",
	"Portland Trail Blazers",
	"Oklahoma City Thunder",
	"Utah Jazz",
	#SOUTHEAST
	"Atlanta Hawks",
	"Charlotte Bobcats",
	"Miami Heat",
	"Orlando Magic",
	"Washington Wizards",
	#PACIFIC
	"Golden State Warriors",
	"Los Angeles Clippers",
	"Los Angeles Lakers",
	"Phoenix Suns",
	"Sacramento Kings"
	]
	

def GetGames():
	
	thedate = datetime.datetime.now()	
	#the schedule date is always a monday and has a week's worth of games
	
	while thedate.weekday() > 0:
		thedate = thedate - datetime.timedelta(days = 1)
		
	year = thedate.strftime("%Y")
	month = thedate.strftime("%m").lstrip("0")
	day = thedate.strftime("%d").lstrip("0")
	
	url = GAMES_URL_FORMAT.format(year, month, day)
	Log.Debug("current schedule url: " + url)
	
	feed = HTML.ElementFromURL(url)
	data = string.replace(HTML.StringFromElement(feed), "<p>var g_schedule=", "")
	data = string.replace(data, "</p>", "")	
	Log.Debug("data: " + data)
	
	json = JSON.ObjectFromString(data)
	
	gameElements = feed.xpath("//item")
	
	games = []
	
	for element in gameElements:
		title = element.xpath("./title/text()")[0]
		gameId = element.xpath("./boxee:property[@name='custom:gid']/text()", namespaces={"boxee":"http://boxee.tv/rss"})[0]
		Log.Debug("Found game: " + title + " with id: " + gameId)
		games.append(core.Game(title, gameId)) 
	
	return games

	
def GetStreams(gameId):
	
	feed = XML.ElementFromURL(GAMES_URL)
	
	# there's probably a better way to find the game than looping, but I such with xpath and the custom attributes make it even tougher
	gameElements = feed.xpath("//item")
	
	gameElement = None
	
	for element in gameElements:
		elementGameId = element.xpath("./boxee:property[@name='custom:gid']/text()", namespaces={"boxee":"http://boxee.tv/rss"})[0]
		if elementGameId == gameId:
			gameElement = element
			break;
	
	if gameElement == None:
		Log.Debug("Failed to find game for some reason...")
	
	awayName = gameElement.xpath("./boxee:property[@name='custom:awayName']/text()", namespaces={"boxee":"http://boxee.tv/rss"})[0]
	homeName = gameElement.xpath("./boxee:property[@name='custom:homeName']/text()", namespaces={"boxee":"http://boxee.tv/rss"})[0]
	Log.Debug("Away Team: " + awayName)
	Log.Debug("Home Team: " + homeName)
	
	awayStream = core.FormatStreamUrl(STREAM_FORMAT, gameId, awayName)
	homeStream = core.FormatStreamUrl(STREAM_FORMAT, gameId, homeName)	
	
	streams = []
	streams.append(core.Stream(teamName = awayName, url = awayStream))
	streams.append(core.Stream(teamName = homeName, url = homeStream))
	
	return streams
	
	
	