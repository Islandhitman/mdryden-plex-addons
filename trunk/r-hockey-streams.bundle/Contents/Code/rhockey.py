import re, urlparse, string

###############################################

SEARCH_URL = "http://www.reddit.com/r/hockey/search.rss?q=game+thread+self%3Ayes&sort=new&restrict_sr=on&t=week"

PLAYOFF_TEAMS = [
	"Pittsburgh Penguins",	"New York Islanders",
	"Montreal Canadiens", 	"Ottawa Senators",
	"Washington Capitals", 	"New York Rangers",
	"Boston Bruins",		"Toronto Maple Leafs",
	"Chicago Blackhawks",	"Minnesoda Wild",
	"Anaheim Ducks",		"Detroit Red Wings",
	"Vancouver Canucks",	"San Jose Sharks",
	"St. Louis Blues",		"Los Angeles Kings"
	]

###############################################

class GameThread:
	def __init__(self, title, url, date):
		self.Title = title
		self.Url = url
		self.Date = date
		
class Stream:
	def __init__(self, title, url):
		self.Title = title
		self.Url = url
	
###############################################	

def GetGameList(type):

	Log.Debug("GetGameList()")
	itemList = []

	#try:
	threadList = XML.ElementFromURL(SEARCH_URL)
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
			if (IsGameThread(thread.Title)):
				# clean the title
				thread.Title = CleanGameTitle(thread.Title, thread.Date)
				itemList.append(thread)
				
		else: #always add if we're in full mode
			itemList.append(thread)
	
	return itemList
	
def IsGameThread(title):
	# we'll assume that all game threads will contain 2 teams in the title
	# this should filter most out, since most posters are too lazy to type the full
	# names of each team
	count = 0
	
	for team in PLAYOFF_TEAMS:
		index = string.find(title, team)
		if index > -1:
			count += 1
	
	return (count == 2)
	
def CleanGameTitle(title, pubDate):
	# try and clean up the title so it displays a bit nicer
	# Most (all?) of the threads contain something like "Team 1 vs Team 2" or "Team 1 at Team 2"
	# we'll look for instances of 2 teams and use those as the markers in the header
	
	teams = []
	
	for team in PLAYOFF_TEAMS:
		index = string.find(title, team)
		if index > -1:
			teams.append(dict(name = team, index = index))
	
	# if we didn't find 2 teams, don't mess with the title
	if len(teams) == 2:
		#we did find 2 teams, so create a nice title 
		#first sort by index, so we get them in the order they were in the thread
		teams.sort(key=lambda t: t["index"])
		#trim the date a bit
		date = pubDate[0:16]
		title = str(L("SmartGameTitleFormat")).format(teams[0]["name"], teams[1]["name"], date) 
	
	return title
	
	
def GetOfficialVideosInThread(url):
	videoList = []
	
	# first try looking in the first item of the rss feed
	thread = XML.ElementFromURL(url + ".rss")
	
	selfPost = thread.xpath("//item")[0]
	videoList = GetVideosInComment(selfPost)
	
	return videoList
	
def GetAlternativeVideosInThread(url):
	videoList = []
	urls = [] #tracks the urls we've already added, since any() isn't supported
	
	thread = XML.ElementFromURL(url + ".rss")
	items = thread.xpath("//item")
		
	# we need to loop through all comments and find any which contain a stream.
	for item in items:
		#GetVideosInComment only finds comments in a proper <a> tag, so we need to parse differently
		comment = item.xpath("./description/text()")[0]
		#Log.Debug("Searching comment: " + comment)
		
		lastIndex = 0
		while lastIndex > -1:
			index = string.find(comment, "m3u8", lastIndex + 4) #+4 to account for length of sub
			#Log.Debug("m3u8 found at index" + str(index))
			if index > -1:
				# found a stream
				Log.Debug("Found a stream in comment: " + comment) 
				
				# first, dig it out
				#look for http before the m3u8, and take that index up until m3u8 index + 4
				urlStart = string.rfind(comment, "http", lastIndex, index)
				#Log.Debug("http index " + str(urlStart))
				url = comment[urlStart:index+4]
				url = ReplaceStreamQuality(url)
				
				# make sure it's unique
				Log.Debug("url in urls: " + str(url in urls))
				if (url in urls) == False:
					# video is unique, add it.
					#Log.Debug("Stream: " + url)
					team = GetStreamTeam(url)
					title = str(L("UnofficialLabelFormat")).format(team)
					
					videoList.append(Stream(title = title, url = url))
					#store raw url to avoid duplicates					
					urls.append(url)
					
			#always increment last index or we'll end up with an infinite loop			
			lastIndex = index				
					
	Log.Debug("VideoList: " + str(len(videoList)))
	return videoList
	
def GetStreamTeam(url):
	#guess at the title based on the name of the file
	slashIndex = string.rfind(url, "/")
	lastUnderscore = string.find(url, "_", slashIndex)
	filename = url[slashIndex + 1:lastUnderscore]
	filename = filename.replace(".m3u8", "")
	
	return filename
	
	
def ReplaceStreamQuality(url):
	#remove the quality value from the url
	#http://nlds128.cdnak.neulion.com/nlds/nhl/bruins/as/live/bruins_hd_3000.m3u8
	# it will always be at the end between the underscore and dot
	underscoreIndex = string.rfind(url, "_")
	dotIndex = string.rfind(url, ".")
	qualityValue = url[underscoreIndex+1:dotIndex]
	Log.Debug("Quality: " + qualityValue)
	
	return url.replace(qualityValue, "{q}")
	
	
def GetVideosInComment(comment):
	videoList = []

	description = HTML.ElementFromString(comment.xpath("./description/text()")[0])
	Log.Debug("Found description: " + comment.xpath("./description/text()")[0])
	
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

