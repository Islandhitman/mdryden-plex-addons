import core, hockey, basketball

###############################################

VIDEO_PREFIX = "/video/redditsports"

NAME = "Reddit Sports"

ART = 'art-default.png'
ICON = 'icon-default.png'

# address should not start with a slash
# keywords should be url encoded
SUPPORTED_SUBREDDITS = { 
	"Hockey": {
		"name":"Hockey", 
		"address":"r/hockey", 
		"keywords":"game+thread", 
		"teams":hockey.TEAMS, 
		"getOfficialVideosFunction":hockey.GetOfficialVideosInThread,
		"getAlternativeVideosFunction":hockey.GetAlternativeVideosInThread,
		"getExternalVideosFunction":hockey.GetExternalVideosInThread
		},
	# "Basketball": {
		# "name":"Basketball",
		# "address":"r/nba",
		# "keywords":"game+thread",
		# "teams":basketball.TEAMS,
		# "getOfficialVideosFunction":basketball.GetOfficialVideosInThread,
		# "getAlternativeVideosFunction":basketball.GetAlternativeVideosInThread,
		# "getExternalVideosFunction":basketball.GetExternalVideosInThread
		# }
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
	
	for item in SUPPORTED_SUBREDDITS:
		Log.Debug(item)
		name = SUPPORTED_SUBREDDITS[item]["name"]
		dir.add(DirectoryObject(
				key = Callback(SubredditMenu, name = name),
				title = Locale.LocalString(name + "Title"),
				summary = Locale.LocalString(name + "Summary")
			))
	
	return dir
	
def SubredditMenu(name):
	# load the top level menu items
	# this has a full list, and a smart list
	# smart list attempts to filter threads which don't appear to be game threads
	# full list returns all threads which match the search
	
	dir = ObjectContainer(title2 = Locale.LocalString(name + "Title"))
	
	dir.add(DirectoryObject(
			key = Callback(GameList, type = "smart", name = name),
			title = Locale.LocalString("SmartGameListTitle"),
			summary = Locale.LocalString("SmartGameListSummary")
		))
	
	dir.add(DirectoryObject(
			key = Callback(GameList, type = "full", name = name),
			title = Locale.LocalString("FullGameListTitle"),
			summary = Locale.LocalString("FullGameListSummary")
		))
	
	return dir
		

def GameList(name, type):

	title = ""
	if type == "smart":
		title = Locale.LocalString("SmartGameListTitle")
	else:
		title = Locale.LocalString("FullGameListTitle")

	dir = ObjectContainer(title2 = title)
	
	config = SUPPORTED_SUBREDDITS[name]
	 
	items = core.GetGameList(type, config["address"], config["keywords"], config["teams"])	
	
	for item in items:
		dir.add(DirectoryObject(
			key = Callback(GameThread, url=item.Url, name=name),
			title = item.Title,
			summary = item.Title,
			thumb = ICON
		))
		
		
	# display empty message
	if len(dir) == 0:
		Log.Debug("no videos")
		return ObjectContainer(header=title, message=L("ErrorNoThreads")) 
	
	return dir

def GameThread(url, name):
	dir = ObjectContainer(title2 = L("OfficialTitle"))
	
	config = SUPPORTED_SUBREDDITS[name]
	
	videos = config["getOfficialVideosFunction"](url)
		
	AddStreamObjects(dir, videos)
	
	#add link to unofficial streams
	dir.add(DirectoryObject(
			key = Callback(GameThreadUnofficial, url=url, name=name),
			title = L("UnofficialTitle"),
		))
		
	#add link to external streams
	dir.add(DirectoryObject(
			key = Callback(GameThreadExternal, url=url, name=name),
			title = L("ExternalTitle"),
		))
	
	return dir
	
def GameThreadUnofficial(url, name):
	dir = ObjectContainer(title2 = L("UnofficialTitle"))
	
	config = SUPPORTED_SUBREDDITS[name]
	
	videos = config["getAlternativeVideosFunction"](url) 
	 
	AddStreamObjects(dir, videos)
	
	# display empty message
	if len(dir) == 0:
		return ObjectContainer(header=L("UnofficialTitle"), message=L("ErrorNoStreams"))
	
	return dir
	
def GameThreadExternal(url, name):
	dir = ObjectContainer(title2 = L("ExternalTitle"))
	
	
	config = SUPPORTED_SUBREDDITS[name]
	
	videos = config["getExternalVideosFunction"](url)
	
	AddStreamObjects(dir, videos)
	
	# display empty message
	if len(dir) == 0:
		return ObjectContainer(header=L("ExternalTitle"), message=L("ErrorNoStreams"))
	
	return dir

def AddStreamObjects(container, videos):

	quality = Prefs["videoQuality"]
	
	for video in videos:
		#media1 = MediaObject(
		#	parts = [
		#		PartObject(key = HTTPLiveStreamURL(Callback(PlayVideo, videoUrl=video.Url)))]
		#	)
		# add quality to url
		video.Url = video.Url.replace(core.QUALITY_MARKER, quality)
		clip = VideoClipObject(
			#key = HTTPLiveStreamURL(Callback(PlayVideo, videoUrl = video.Url)),
			url = video.Url,
			#rating_key = video.Url,
			title = video.Title,
			)
		
		#clip.add(media1)
		container.add(clip)


#@indirect
#def PlayVideo(videoUrl):
#
#	quality = Prefs["videoQuality"]
#	#quality = "3000"
#	
#	#set the quality	
#	videoUrl = videoUrl.replace("{q}", quality)
#		
#	Log.Debug("attempting to play: " + videoUrl)
	
#	return Redirect(videoUrl)
	