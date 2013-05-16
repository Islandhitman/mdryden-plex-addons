import re, urlparse, string

###############################################

SEARCH_URL = "http://www.reddit.com/{0}/search.rss?q={1}+self%3Ayes&sort=new&restrict_sr=on&t=week"

###############################################
		
class Game:
	def __init__(self, title, gameId):
		self.Title = title
		self.GameId = gameId
		
class Stream:
	def __init__(self, teamName, url):
		self.TeamName = teamName
		self.Url = url
	
###############################################	

def FormatStreamUrl(streamFormat, gameId, team):	
	return streamFormat.format(gameId, string.lower(team))


def GetGameList(type, address, keywords, teams):

	Log.Debug("GetGameList()")
	itemList = []

	url = SEARCH_URL.format(address, keywords)
	
	Log.Debug(url)
	
	#try:
	threadList = XML.ElementFromURL(url)
	#except:
		# reddit down likely
	#	return itemList
	
	items = threadList.xpath("//item")
	
	index = 1
	
	for item in items:
		#Log.Debug(XML.StringFromElement(item))
		
		itemTitle = item.xpath("./title/text()")[0]
		itemUrl = item.xpath("./link/text()")[0]
		pubDate = item.xpath("./pubDate/text()")[0]
				
		Log.Debug("Title: " + itemTitle + ", Url: " + itemUrl + ", Date: " + pubDate)
		
		thread = GameThread(title = itemTitle.strip(), url = itemUrl, date = pubDate)
		
		# if using a smart list, only add if it's a game thread
		if type == "smart":
			if (IsGameThread(thread.Title, teams)):
				# clean the title
				thread.Title = CleanGameTitle(thread.Title, thread.Date, teams)
				itemList.append(thread)
				
		else: #always add if we're in full mode
			itemList.append(thread)
	
	return itemList
	
def IsGameThread(title, teams):
	# we'll assume that all game threads will contain 2 teams in the title
	# this should filter most out, since most posters are too lazy to type the full
	# names of each team
	count = 0
	
	for team in teams:
		index = string.find(title, team)
		if index > -1:
			count += 1
	
	return (count == 2)
	
def CleanGameTitle(title, pubDate, teams):
	# try and clean up the title so it displays a bit nicer
	# Most (all?) of the threads contain something like "Team 1 vs Team 2" or "Team 1 at Team 2"
	# we'll look for instances of 2 teams and use those as the markers in the header
	
	foundTeams = []
	
	for team in teams:
		index = string.find(title, team)
		if index > -1:
			foundTeams.append(dict(name = team, index = index))
	
	# if we didn't find 2 teams, don't mess with the title
	if len(foundTeams) == 2:
		#we did find 2 teams, so create a nice title 
		#first sort by index, so we get them in the order they were in the thread
		foundTeams.sort(key=lambda t: t["index"])
		#trim the date a bit
		date = pubDate[0:16]
		title = str(L("SmartGameTitleFormat")).format(foundTeams[0]["name"], foundTeams[1]["name"], date) 
	
	return title
	
	
def GetOfficialVideosInThread(url, findStreamAnchors, replaceStreamQualityFunction, getStreamTeamFunction):
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
		streamUrl = replaceStreamQualityFunction(streamUrl)
		Log.Debug("Found stream: " + streamUrl)
		
		#old way used anchor text, new way is more standardized
		#title = stream.xpath("./text()")[0]
		team = getStreamTeamFunction(streamUrl)
		title = str(L("OfficialLabelFormat")).format(team)
		
		videoList.append(Stream(title = title, url = streamUrl))
		
	return videoList
	
	return videoList
	
def GetAlternativeVideosInThread(url, replaceStreamQualityFunction, getStreamTeamFunction, findStreamsInTextFunction):
	videoList = []
	knownUrls = [] #tracks the urls we've already added, since any() isn't supported
	
	thread = XML.ElementFromURL(url + ".rss")
	items = thread.xpath("//item")
		
	# we need to loop through all comments and find any which contain a stream.
	for item in items:
		#GetVideosInComment only finds comments in a proper <a> tag, so we need to parse differently
		comment = item.xpath("./description/text()")[0]
		streamUrlsInComment = findStreamsInTextFunction(comment)
		
		#loop through the streams we found and clean em up to make sure they aren't duplicates before we add them
		for streamUrl in streamUrlsInComment:		
			url = replaceStreamQualityFunction(streamUrl)
			#make sure it's not a duplicate
			if (url in knownUrls) == False:
				# video is unique, add it.
				#Log.Debug("Stream: " + url)
				team = getStreamTeamFunction(url)
				title = str(L("UnofficialLabelFormat")).format(team)
				
				videoList.append(Stream(title = title, url = url))
				knownUrls.append(url)
					
	Log.Debug("VideoList: " + str(len(videoList)))
	return videoList


def GetExternalVideosInThread(url, replaceStreamQualityFunction, getStreamTeamFunction, isStreamUrlFunction, findStreamsInTextFunction):
	videoList = []
	knownUrls = [] #tracks the urls we've already added, since any() isn't supported
	
	thread = XML.ElementFromURL(url + ".rss")
	items = thread.xpath("//item")	

	# not looping all comments for now, just looking at the self post
	selfPost = thread.xpath("//item")[0]

	description = HTML.ElementFromString(selfPost.xpath("./description/text()")[0])
	Log.Debug("Found description: " + selfPost.xpath("./description/text()")[0])
	
	streamsList = description.xpath("//a[contains(text(), 'vlc') or contains(text(), 'VLC') or contains(text(), 'Vlc')]")
	
	for item in streamsList:
		Log.Debug("Found possible external link:" + HTML.StringFromElement(item))
		url = item.xpath("./@href")[0]
		
		if isStreamUrlFunction(url) == True:
			Log.Debug("Skipping '" + url + "' - appears to be an official stream")
		else:
			Log.Debug("Attempting to open external url: " + url)
			externalPage = HTML.ElementFromURL(url)
			content = HTML.StringFromElement(externalPage)
			# search the page just like a comment
			streamsInPage = findStreamsInTextFunction(content)
			
			for stream in streamsInPage:
				if IsValidStream(stream):
					Log.Debug("Found external stream: " + stream)
					
					url = replaceStreamQualityFunction(stream)
					#make sure it's not a duplicate
					if (url in knownUrls) == False:
						# video is unique, add it.
						#Log.Debug("Stream: " + url)
						team = getStreamTeamFunction(url)
						title = str(L("ExternalLabelFormat")).format(team)
						  
						videoList.append(Stream(title = title, url = url))
						knownUrls.append(url)

	return videoList
	
def IsValidStream(url):
	# checks for some common errors in the url, like spaces (happens from external blog posts, or if someone
	# happened to comment "http" and "m3u8" in the same post, but not as a valid url.
	if string.find(url, " ") > -1: #valid urls do not contain spaces
		return False
	
	if string.find(url, "\r") > -1: # or carriage returns
		return False
		
	if string.find(url, "\n") > -1: # or line feeds
		return False
	
	#seems legit
	return True
	