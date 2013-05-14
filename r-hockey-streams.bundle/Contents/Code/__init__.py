import rhockey

###############################################

VIDEO_PREFIX = "/video/tsn"

NAME = "Reddit Hockey"

ART = 'art-default.png'
ICON = 'icon-default.png'

###############################################

# This function is initially called by PMS to inialize the plugin

def Start():

	# Initialize the plugin
	Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("LIST", viewMode = "List", mediaType = "items")
	
	# setup artwork
	#MediaContainer.art = R(ART)
	#MediaContainer.title1 = NAME
	#MediaContainer.viewGroup = "List"
	#DirectoryItem.thumb = R(ICON)
	ObjectContainer.title1 = NAME
	
	HTTP.Headers["Referer"] = "http://cls.ctvdigital.net/"
	Log.Debug("TSN Plugin Start")
	
# This main function will setup the displayed items
@handler('/video/tsn', 'TSN')
def MainMenu():
	# load the top level menu items
		
	return CategoryMenu(NAME, "//menu")
		

@route('/video/tsn/categories')
def CategoryMenu(title, rootPath):
	dir = ObjectContainer(title2 = title)
	
	items = tsn.GetItemList(rootPath)	
	
	for item in items:
		if item.IsCategory:
			#Log.Debug("Category: " + item.Title + ", Path: " + item.Path)
			dir.add(DirectoryObject(
				key = Callback(CategoryMenu, title=item.Title, rootPath=item.Path),
				title = item.Title
			))
		
		else:
			Log.Debug("Video: " + item.Title + ", Url: " + item.FeedUrl)
			#dir.add(Function(DirectoryItem(VideoListMenu, item.Title), title = item.Title, feedUrl = item.FeedUrl, tag = item.Tag))
			dir.add(DirectoryObject(
				key = Callback(VideoListMenu, title=item.Title, feedUrl=item.FeedUrl, tag=item.Tag),
				title = item.Title
			))
		
	return dir
	
	
@route('/video/tsn/videos')
def VideoListMenu(title, feedUrl, tag):	
	dir = ObjectContainer(title2 = title)
	
	videoList = tsn.GetVideosInList(feedUrl, tag)
	
	Log.Debug("displaying video list")
	
	
	for video in videoList:
	
		#url = tsn.GetVideoUrl(video.ID)
		
		#if URLService.ServiceIdentifierForURL(url) is not None:
		dir.add(VideoClipObject(
			key = Callback(PlayVideo, title = video.Title, id = video.ID),
			rating_key = id,
			#url = url,
			title = video.Title,
			summary = video.Description,
			thumb = video.ThumbUrl
		))
						
			
	Log.Debug("done displaying video list")
	# display empty message
	if len(dir) == 0:
		Log.Debug("no videos")
		return ObjectContainer(header=title, message=L("ErrorNoTitles")) 
	
	return dir

@indirect
@route("video/tsn/play")
def PlayVideo(id, title):	

	quality = Prefs["vidquality"]
	url = tsn.GetVideoUrl(id, quality)
		
	Log.Debug("attempting to play: " + url)
	
	return Redirect(url)
	