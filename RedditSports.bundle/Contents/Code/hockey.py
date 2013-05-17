import string, core


################################################

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
	"Vancouver Canucks",
	#NORTHEAST
	"Boston Bruins",
	"Buffalo Sabres",
	"Montreal Canadiens",
 	"Ottawa Senators",
	"Toronto Maple Leafs",
	#PACIFIC
	"Anaheim Ducks",
	"Dallas Stars",	
	"Los Angeles Kings",
	"Phoenix Coyotes",
	"San Jose Sharks",
	#SOUTHEAST
	"Carolina Hurricanes",
	"Florida Panthers",
	"Tampa Bay Lightning",
	"Washington Capitals",
	"Winnipeg Jets"
	]
	

def GetOfficialVideosInThread(url):
	videoList = []
	
	# first try looking in the first item of the rss feed
	thread = XML.ElementFromURL(url + ".rss")
	
	selfPost = thread.xpath("//item")[0]	

	description = HTML.ElementFromString(selfPost.xpath("./description/text()")[0])
	Log.Debug("Found description: " + selfPost.xpath("./description/text()")[0])
	
	#//td[contains(label, 'Choice 1')]/input
	streamsList = description.xpath("//a[contains(@href, 'm3u8')]")
	
	for stream in streamsList:
		#Log.Debug("Found stream: " + XML.StringFromElement(stream))
		streamUrl = stream.xpath("./@href")[0]
		Log.Debug("Found stream: " + streamUrl)
		streamUrl = ReplaceStreamQuality(streamUrl)
		Log.Debug("Found stream: " + streamUrl)
		
		#old way used anchor text, new way is more standardized
		#title = stream.xpath("./text()")[0]
		team = GetStreamTeam(streamUrl)
		title = str(L("OfficialLabelFormat")).format(team)
		
		videoList.append(Stream(title = title, url = streamUrl))
		
	return videoList
	
	return videoList
	
def GetAlternativeVideosInThread(url):
	videoList = []
	
	thread = XML.ElementFromURL(url + ".rss")
	items = thread.xpath("//item")
	
	videoList = FindVideosInComments(items)
	
	if len(videoList) > 0:
		return videoList
	
	# try searching the newer comments (last ditch, in case someone like me posts one...)	
	thread = XML.ElementFromURL(url + ".rss?sort=new")
	items = thread.xpath("//item")
	
	return FindVideosInComments(items)

def FindVideosInComments(items):
	
	videoList = []
	knownUrls = [] # tracks the urls we've already added, since any() isn't supported
	
	# we need to loop through all comments and find any which contain a stream.
	for item in items:
		#GetVideosInComment only finds comments in a proper <a> tag, so we need to parse differently
		comment = item.xpath("./description/text()")[0]
		streamUrlsInComment = FindStreamsInText(comment)
		
		#loop through the streams we found and clean em up to make sure they aren't duplicates before we add them
		for streamUrl in streamUrlsInComment:		
			url = ReplaceStreamQuality(streamUrl)
			#make sure it's not a duplicate
			if (url in knownUrls) == False:
				# video is unique, add it.
				#Log.Debug("Stream: " + url)
				team = GetStreamTeam(url)
				title = str(L("UnofficialLabelFormat")).format(team)
				
				videoList.append(core.Stream(title = title, url = url))
				knownUrls.append(url)
					
	Log.Debug("VideoList: " + str(len(videoList)))
	return videoList
	
def GetExternalVideosInThread(url):
	videoList = []
	knownUrls = [] #tracks the urls we've already added, since any() isn't supported
	
	thread = XML.ElementFromURL(url + ".rss")
	items = thread.xpath("//item")	

	# not looping all comments for now, just looking at the self post
	selfPost = thread.xpath("//item")[0]

	description = HTML.ElementFromString(selfPost.xpath("./description/text()")[0])
	Log.Debug("Found description: " + selfPost.xpath("./description/text()")[0])
	
	streamsList = description.xpath("//a[contains(text(), 'vlc') or contains(text(), 'VLC') or contains(text(), 'Vlc')]")
	#sometimes they trip things up by putting formatting tags inside the link...
	if len(streamsList) == 0:
		streamsList = description.xpath("//a/*[contains(text(), 'vlc') or contains(text(), 'VLC') or contains(text(), 'Vlc')]")
	
	for item in streamsList:
		Log.Debug("Found possible external link:" + HTML.StringFromElement(item))		
		url = ""
		href = item.xpath("./@href")
		if len(href) == 0:
			# probably inside a formatting tag, href is probably in parent.  hopefully.	
			url = item.xpath("../@href")[0]
		else:
			url = href[0] #use the href
		
		if IsStreamUrl(url) == True:
			Log.Debug("Skipping '" + url + "' - appears to be an official stream")
		else:
			Log.Debug("Attempting to open external url: " + url)
			externalPage = HTML.ElementFromURL(url)
			content = HTML.StringFromElement(externalPage)
			# search the page just like a comment
			streamsInPage = FindStreamsInText(content)
			
			for stream in streamsInPage:
				if IsValidStream(stream):
					Log.Debug("Found external stream: " + stream)
					
					url = ReplaceStreamQuality(stream)
					#make sure it's not a duplicate
					if (url in knownUrls) == False:
						# video is unique, add it.
						#Log.Debug("Stream: " + url)
						team = GetStreamTeam(url)
						title = str(L("ExternalLabelFormat")).format(team)
						  
						videoList.append(Stream(title = title, url = url))
						knownUrls.append(url)

	return videoList
	
def ReplaceStreamQuality(url):
	#remove the quality value from the url
	#http://nlds128.cdnak.neulion.com/nlds/nhl/bruins/as/live/bruins_hd_3000.m3u8
	# it will always be at the end between the underscore and dot
	underscoreIndex = string.rfind(url, "_")
	dotIndex = string.rfind(url, ".")
	qualityValue = url[underscoreIndex+1:dotIndex]
	Log.Debug("Quality: " + qualityValue)
	
	return url.replace(qualityValue, core.QUALITY_MARKER)
	

def GetStreamTeam(url):
	#guess at the title based on the name of the file
	slashIndex = string.rfind(url, "/")
	lastUnderscore = string.find(url, "_", slashIndex)
	filename = url[slashIndex + 1:lastUnderscore]
	filename = filename.replace(".m3u8", "")
	
	return filename
	
def FindStreamsInText(text):
	#this function returns raw urls, no quality removal or dupe checking

	videoList = [] 
	#Log.Debug("Searching text: " + text)
		
	lastIndex = 0
	while lastIndex > -1:
		index = string.find(text, "m3u8", lastIndex + 4) #+4 to account for length of sub
		Log.Debug("m3u8 found at index: " + str(index))
		if index > -1:
			# found a stream
			#Log.Debug("Found a stream in text: " + text) 
			
			# first, dig it out
			#look for http before the m3u8, and take that index up until m3u8 index + 4
			urlStart = string.rfind(text, "http", lastIndex, index)
			#Log.Debug("http index " + str(urlStart))
			url = text[urlStart:index+4]
							
			videoList.append(url)
				
		#always increment last index or we'll end up with an infinite loop			
		lastIndex = index				
	
	return videoList
	
def IsStreamUrl(url):
	return string.find(url, "m3u8") > -1
	