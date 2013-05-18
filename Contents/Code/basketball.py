import string, core


################################################

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
		streamUrl = CleanStreamUrl(streamUrl)
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
			url = CleanStreamUrl(streamUrl)
			#make sure it's not a duplicate
			if (url in knownUrls) == False:
				# video is unique, add it.
				Log.Debug("Stream: " + url)
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
					
					url = CleanStreamUrl(stream)
					#make sure it's not a duplicate
					if (url in knownUrls) == False:
						# video is unique, add it.
						#Log.Debug("Stream: " + url)
						team = GetStreamTeam(url)
						title = str(L("ExternalLabelFormat")).format(team)
						  
						videoList.append(Stream(title = title, url = url))
						knownUrls.append(url)

	return videoList
	
def CleanStreamUrl(url):
	#remove the quality value from the url
	#http://boulder.zxq.net/stream.php?server=137&amp;team=gsw&amp;quality=1600
	#the url instability here makes just replacing the available options easier than searching,
	#I'd say.
	url = url.replace("400", core.QUALITY_MARKER)
	url = url.replace("800", core.QUALITY_MARKER)
	url = url.replace("1200", core.QUALITY_MARKER)
	url = url.replace("1600", core.QUALITY_MARKER)
	url = url.replace("3000", core.QUALITY_MARKER)
	url = url.replace("4500", core.QUALITY_MARKER)
	
	url = url.replace("&amp;", "&")
	
	return url
	

def GetStreamTeam(url):
	#guess at the title based on the name of the file
	teamParamIndex = string.rfind(url, "team=") + 5
	filename = url[teamParamIndex:teamParamIndex+3]
	
	return filename
	
def FindStreamsInText(text):
	#this function returns raw urls, no quality removal or dupe checking

	videoList = [] 
	#Log.Debug("Searching text: " + text)
		
	lastIndex = 0
	while lastIndex > -1:
		# Looking for stream rehosts using server.php - they seem common enough.
		index = string.find(text, "stream.php", lastIndex + 10) #+ to account for length of sub
		Log.Debug("stream.php found at index: " + str(index))
		if index > -1:
			# found a stream
			Log.Debug("Found a stream in text: " + text) 
			
			# first, dig it out
			# this is a little harder than /r/hockey, since the keyword we're using isn't at the end
			index2 = index
			while index2 < len(text):
				#look for something that ends the url - line break, space, or end of comment
				char = text[index2]
				if char == "\n" or char == "\r" or char == " ":
					# found the end
					break
				else:
					index2 += 1
					
			urlEnd = index2
			#look for http before the stream.php, and take that index up until m3u8 index + 4
			urlStart = string.rfind(text, "http", lastIndex, index)
			#Log.Debug("http index " + str(urlStart))
			url = text[urlStart:urlEnd]			
			# the guy that posts these often puts in a copy/paste vlc line that has a quote as well
			# I can't avoid it because it's multi-character, so I'll do a blanket replace here
			url = url.replace("&quot;", "")
			Log.Debug("url = " + url)
							
			videoList.append(url)
				
		#always increment last index or we'll end up with an infinite loop			
		lastIndex = index				
	
	return videoList
	
def IsStreamUrl(url):
	return string.find(url, "m3u8") > -1
	