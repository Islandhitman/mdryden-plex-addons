import core, string


################################################

GAMES_URL = "http://cedrss.neulion.com/nhlgc/archives/?live=true"

STREAM_FORMAT = "http://nlds{0}.cdnak.neulion.com/nlds/nhl/{1}/as/live/{1}_hd_(q).m3u8"

TEAMS = [
	#CENTRAL
	"Chicago Blackhawks",
	"Columbus Blue Jackets",
	"Detroit Red Wings",
	"Nashville Predators",
	"St. Louis Blues",
	#ATLANTIC
	"New Jersey Devils",
	"New York Islanders",
	"New York Rangers",
	"Philadelphia Flyers",
	"Pittsburgh Penguins",
	#NORTHWEST
	"Calgary Flames",
	"Colorado Avalanche",
	"Edmonton Oilers",
	"Minnesota Wild",
	"Vancouver Canucks"
	#NORTHEAST
	"Boston Bruins",
	"Buffalo Sabres",
	"Montreal Canadiens",
 	"Ottawa Senators",
	"Toronto Maple Leafs",
	#PACIFIC
	"Anaheim Ducks",
	"Dallas Stars",	
	"Los Angeles Kings"
	"Phoenix Coyotes",
	"San Jose Sharks",
	#SOUTHEAST
	"Carolina Hurricanes",
	"Florida Panthers",
	"Tampa Bay Lightning",
	"Washington Capitals",
	"Winnipeg Jets"
	]
	

def GetGames():
	
	feed = XML.ElementFromURL(GAMES_URL)
	
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
	
	
	
	
	
	
	
	
	