import core, hockey, basketball

###############################################

VIDEO_PREFIX = "/video/redditsports"

NAME = "Sports Streams"

ART = 'art-default.png'
ICON = 'icon-default.png'

# address should not start with a slash
# keywords should be url encoded
SUPPORTED_LEAGUES = {
	"NHL": {
		"name":"NHL", 
		"teams":hockey.TEAMS, 
		"getGamesFunction":hockey.GetGames,
		"getStreamsFunction":hockey.GetStreams
		},
	"NBA": {
		"name":"NBA",
		"teams":basketball.TEAMS,
		"getGamesFunction":basketball.GetGames,
		"getStreamsFunction":basketball.GetStreams
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
	
	for item in SUPPORTED_LEAGUES:
		Log.Debug(item)
		name = SUPPORTED_LEAGUES[item]["name"]
		dir.add(DirectoryObject(
				key = Callback(GameList, name = name),
				title = Locale.LocalString(name + "Title"),
				summary = Locale.LocalString(name + "Summary")
			))
	
	return dir
	
def GameList(name):
	dir = ObjectContainer(title2 = L("GameList"))
	
	config = SUPPORTED_LEAGUES[name]
	 
	items = config["getGamesFunction"]() 
	
	for item in items:
		dir.add(DirectoryObject(
			key = Callback(StreamList, name = name, gameId = item.GameId),
			title = item.Title,
		))
		
		
	# display empty message
	if len(dir) == 0:
		Log.Debug("no videos")
		return ObjectContainer(header=title, message=L("ErrorNoThreads")) 
	
	return dir

def StreamList(name, gameId):
	dir = ObjectContainer(title2 = L("StreamList"))

	config = SUPPORTED_LEAGUES[name]
	
	streams = config["getStreamsFunction"](gameId)
	
	for stream in streams:
		Log.Debug("Adding stream: " + stream.Url)
		#media1 = MediaObject(
		#	parts = [
		#		PartObject(key = Callback(PlayStream, url=stream))]
		#	)		
		dir.add(VideoClipObject(
			key = Callback(PlayStream, url = stream.Url),
			rating_key = stream.Url,
			title = stream.TeamName,
			))
		 
		#clip.add(media1)
		#dir.add(clip)
		
	
	# display empty message
	if len(dir) == 0:
		Log.Debug("no videos")
		return ObjectContainer(header=title, message=L("ErrorNoThreads")) 
		
	return dir
	
@indirect
def PlayStream(url):

	quality = Prefs["videoQuality"]
	#quality = "3000"
	
	#set the quality	
	url = url.replace("(q)", quality)
		
	Log.Debug("attempting to play: " + url)
	
	return Redirect(url)
	