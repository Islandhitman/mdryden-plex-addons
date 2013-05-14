import rhockey

###############################################

VIDEO_PREFIX = "/video/reddithockeystreams"

NAME = "Reddit Hockey"

ART = 'art-default.png'
ICON = 'icon-default.png'

###############################################

# This function is initially called by PMS to inialize the plugin

def Start():

	# Initialize the plugin
	Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("LIST", viewMode = "List", mediaType = "items")
	
	ObjectContainer.title1 = NAME
	
	Log.Debug("Plugin Start")
	
# This main function will setup the displayed items
def MainMenu():
	# load the top level menu items
	# this has a full list, and a smart list
	# smart list attempts to filter threads which don't appear to be game threads
	# full list returns all threads which match the search
	
	dir = ObjectContainer(title2 = Locale.LocalString("MainMenuTitle"))
	
	dir.add(DirectoryObject(
			key = Callback(GameList, type = "smart"),
			title = Locale.LocalString("SmartGameListTitle"),
			summary = Locale.LocalString("SmartGameListSummary")
		))
	
	dir.add(DirectoryObject(
			key = Callback(GameList, type = "full"),
			title = Locale.LocalString("FullGameListTitle"),
			summary = Locale.LocalString("FullGameListSummary")
		))
	
	return dir
		

@route('/video/reddithockeystreams/games')
def GameList(type):

	title = ""
	if type == "smart":
		title = Locale.LocalString("SmartGameListTitle")
	else:
		title = Locale.LocalString("FullGameListTitle")

	dir = ObjectContainer(title2 = title)
	
	Log.Debug("GameList()")
	
	items = rhockey.GetGameList(type)	
	
	for item in items:
		dir.add(DirectoryObject(
			key = Callback(GameThread, title=item.Title, url=item.Url),
			title = item.Title,
			summary = item.Title,
			thumb = ICON
		))
		
		
	# display empty message
	if len(dir) == 0:
		Log.Debug("no videos")
		return ObjectContainer(header=title, message=L("ErrorNoThreads")) 
	
	return dir

@route("/video/reddithockeystreams/thread")
def GameThread(title, url):

	title = title.replace("–", "")
	
	#Log.Debug("Trying to set title to: " + title)	
	
	dir = ObjectContainer(title2 = title)
	
	videos = rhockey.GetVideosInThread(url)
	
	for video in videos:
		media1 = MediaObject(
			parts = [
				PartObject(key = Callback(PlayVideo, videoUrl=video.Url))]
			)		
		clip = VideoClipObject(
			key = Callback(PlayVideo, videoUrl = video.Url),
			rating_key = video.Url,
			title = video.Title,
			)
		
		clip.add(media1)
		dir.add(clip)
	
	# display empty message
	if len(dir) == 0:
		Log.Debug("no videos")
		return ObjectContainer(header=title, message=L("ErrorNoStreams")) 
	
	return dir

def GetMetaData(url):
	dir = ObjectContainer(title2 = "meta")
	
	dir.add(VideoClipObject(
		key = Callback(PlayVideo, videoUrl=url),
		title = "title",
		rating_key = url
		))
			
	return dir
	
@indirect
@route("/video/reddithockeystreams/playvideo")
def PlayVideo(videoUrl):	

	#quality = Prefs["vidquality"]
	quality = "3000"
	
	#set the quality	
	videoUrl = videoUrl.replace("{q}", quality)
		
	Log.Debug("attempting to play: " + videoUrl)
	
	return Redirect(videoUrl)
	