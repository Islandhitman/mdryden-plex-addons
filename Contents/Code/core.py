import re, urlparse, string

###############################################

SEARCH_URL = "http://www.reddit.com/{0}/search.rss?q={1}+self%3Ayes&sort=new&restrict_sr=on&t=week"

QUALITY_MARKER = "(q)"  

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
				
		#Log.Debug("Title: " + itemTitle + ", Url: " + itemUrl + ", Date: " + pubDate)
		
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
	
	Log.Debug("is '" + title + "' a game thread?")
	
	for team in teams:
		index = string.find(title, team)
		#Log.Debug("index of: " + team + " = " + str(index)) 
		if index > -1:
			count += 1
			
	if count == 2:
		Log.Debug("Yes")
	else:
		Log.Debug("No")
	
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
	