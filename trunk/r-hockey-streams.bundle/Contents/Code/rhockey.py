import re, urlparse, string

###############################################

SEARCH_URL = "http://www.reddit.com/r/hockey/search.rss?q=game+thread+self%3Ayes&restrict_sr=on&sort=relevance&t=week"

###############################################

class GameThread:
	def __init__(self, title, url):
		self.Title = title
		self.Url = url
		
class Stream:
	def __init__(self, title, url):
		self.Title = title
		self.Url = url
	
###############################################	

def GetGameList(type):

	Log.Debug("GetGameList()")
	itemList = []

	threadList = XML.ElementFromURL(SEARCH_URL)
	
	items = threadList.xpath("//item")
	
	index = 1
	
	for item in items:
		#Log.Debug(XML.StringFromElement(item))
		
		itemTitle = item.xpath("./title/text()")[0]
		itemUrl = item.xpath("./link/text()")[0]
		pubDate = item.xpath("/pubDate/text()")[0]
		
		Log.Debug("Title: " + itemTitle + ", Url: " + itemUrl)
		
		itemList.append(GameThread(title = itemTitle.strip(), url = itemUrl))

	return itemList
	
	
def GetVideosInThread(url):
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
		
		#remove the quality value from the url
		#http://nlds128.cdnak.neulion.com/nlds/nhl/bruins/as/live/bruins_hd_3000.m3u8
		# it will always be at the end between the underscore and dot
		underscoreIndex = string.rfind(streamUrl, "_")
		dotIndex = string.rfind(streamUrl, ".")
		qualityValue = streamUrl[underscoreIndex+1:dotIndex]
		Log.Debug("Quality: " + qualityValue)
		
		streamUrl = streamUrl.replace(qualityValue, "{q}")
		Log.Debug("Found stream: " + streamUrl)
		
		title = stream.xpath("./text()")[0]
		
		videoList.append(Stream(title = title, url = streamUrl))
	
	# if we found streams here, just return them.
	# otherwise, we have to dig deeper into the thread.
	if len(videoList) != 0:
		return videoList
		
	return videoList
	