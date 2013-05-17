import re, urlparse, time
from datetime import datetime

###############################################

VIDEO_MENU = "http://www.tsn.ca/config/videoHubMenu.xml"
VIDEO_URL = "http://esi.ctv.ca/datafeed/urlgenjs.aspx?vid="
CACHE_TIME = 3600
TSN_DATE_FORMAT = "%A, %B %d, %Y %I:%M:%S %p" #Monday, May 13, 2013 7:24:42 PM

# This file contains code licensed under the GNU GPL v2 from the project
# teefer-xmbc-repo/plugin.video.tsn, located at:
# https://code.google.com/p/teefer-xbmc-repo/

###############################################

class VideoListItem:
	def __init__(self, title, feedUrl, tag):
		self.Title = title
		self.FeedUrl = feedUrl
		self.Tag = tag
	
	IsCategory = False
	
class CategoryItem:
	def __init__(self, title, path):
		self.Title = title
		self.Path = path
	
	IsCategory = True
	
class VideoItem:
	def __init__(self, title, id, description, thumbUrl, durationMilliseconds):
		self.Title = title
		self.ID = id
		self.Description = description
		self.ThumbUrl = thumbUrl
		self.DurationMilliseconds = durationMilliseconds
	
###############################################	

def GetItemList(rootPath):

	itemList = []

	menuXml = XML.ElementFromURL(VIDEO_MENU)
	
	path = rootPath + "/item"
	items = menuXml.xpath(path)
	
	index = 1
	
	for item in items:
		#Log.Debug(XML.StringFromElement(item))
		itemTitle = item.xpath("./text/text()")[0]
		#Log.Debug(title)
		#some items have no url (categories with sub categories)
		itemUrl = ""
		try: itemUrl = item.xpath("./urlLatest/text()")[0]
		except: pass
		
		itemTag = ""
		try: itemTag = item.xpath("./tag/text()")[0]
		except:
			#Log.Debug("no tag for title " + rootPath)
			pass
				
		#Log.Debug("Title: " + itemTitle + " URL: " + itemUrl)
		
		if itemUrl == "":
			# no url means it's a top level category
			#Log.Debug("Top level category: " + title)
			subPath = path + "[" + str(index) + "]"
			#Log.Debug("Category: " + itemTitle + ", Path: " + subPath)
			itemList.append(CategoryItem(title = itemTitle, path = subPath))
		else:
			#Log.Debug("found video list " + itemTitle)
			itemList.append(VideoListItem(title = itemTitle, feedUrl = itemUrl, tag = itemTag))
		
		#dir.Append(Function(DirectoryItem(ChannelMenu, title), urlLatest = url))
		
		index += 1
		
	return itemList
	
def GetVideosInList(feedUrl):

	videoList = []
	
	Log.Debug("opening feed: " + feedUrl)

	items = XML.ElementFromURL(feedUrl, cacheTime = CACHE_TIME)
	videos = items.xpath("//item")
	
	for video in videos:
		
		id = video.xpath("./id/text()")[0]
		type = video.xpath("./type/text()")[0]
		videoTitle = video.xpath("./title/text()")[0]
		description = video.xpath("./description/text()")[0]
		thumb = video.xpath("./imgUrl/text()")[0]
		durationSeconds = video.xpath("./duration/text()")[0]
		durationMilliseconds = int(durationSeconds) * 1000		
		
		#videoUrl = GetVideoUrl(id)
		
		#Log.Debug("video in list title: " + videoTitle)
				
		videoList.append(VideoItem(
			title = videoTitle,
			id = id,
			description = description,
			thumbUrl = thumb,
			durationMilliseconds = durationMilliseconds
		))
	
	return videoList

def GetVideoUrl(id, quality):
	tempurl = VIDEO_URL + id
	
	#Log.Debug("opening " + tempurl)
	 
	data = HTML.ElementFromURL(tempurl)
	
	#Log.Debug("data: " + HTML.StringFromElement(data))
	
	#get the entire rtmpe:// out of the contents of the esi.ctv.ca
	temprtmpe = re.compile('Video.Load\({url:\'(.+?)\'').findall(HTML.StringFromElement(data))
	
	#Log.Debug("rtmpe: " + temprtmpe[0])

	o = urlparse.urlparse(temprtmpe[0])
	vidquality = int(quality)

	# raise an error if we encounter an URL we don't know how to parse
	if o.netloc == 'tsnpmd.akamaihd.edgesuite.net':	 
		url = temprtmpe[0]
		#starting in version 0.1.5 (March 19 2013) tsn started using adaptive quality in their http streams
		#the quality now goes up to 720p (adaptive_08)
		url = url.replace('Adaptive_04','Adaptive_0' + str(vidquality+3))
		
	elif o.netloc == "tsnhd-i.akamaihd.net":
		# TSN started throwing in some m3u8 playlists from this site, return them directly
		url = temprtmpe[0]
	
	else:	
		Log.Debug("o = " + temprtmpe[0])
		Log.Debug("netloc = " + o.netloc)
		raise Exception("Unknown video location")	

	return url