import re, urlparse

###############################################

VIDEO_MENU = "http://www.tsn.ca/config/videoHubMenu.xml"
VIDEO_URL = "http://esi.ctv.ca/datafeed/urlgenjs.aspx?vid="

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
	def __init__(self, title, id, description, thumbUrl):
		self.Title = title
		self.ID = id
		self.Description = description
		self.ThumbUrl = thumbUrl
	
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
			Log.Debug("no tag for title " + rootPath)
			pass
				
		Log.Debug("Title: " + itemTitle + " URL: " + itemUrl)
		
		if itemUrl == "":
			# no url means it's a top level category
			#Log.Debug("Top level category: " + title)
			subPath = path + "[" + str(index) + "]"
			Log.Debug("Category: " + itemTitle + ", Path: " + subPath)
			itemList.append(CategoryItem(title = itemTitle, path = subPath))
		else:
			Log.Debug("found video list " + itemTitle)
			itemList.append(VideoListItem(title = itemTitle, feedUrl = itemUrl, tag = itemTag))
		
		#dir.Append(Function(DirectoryItem(ChannelMenu, title), urlLatest = url))
		
		index += 1
		
	return itemList
	
def GetVideosInList(feedUrl, tag):

	videoList = []

	items = XML.ElementFromURL(feedUrl)
	videos = items.xpath("//item")
	
	for video in videos:
		
		id = video.xpath("./id/text()")[0]
		type = video.xpath("./type/text()")[0]
		videoTitle = video.xpath("./title/text()")[0]
		description = video.xpath("./description/text()")[0]
		thumb = video.xpath("./imgUrl/text()")[0]
		
		#videoUrl = GetVideoUrl(id)
		
		#Log.Debug("videoUrl: " + videoUrl)
				
		videoList.append(VideoItem(title = videoTitle, id = id, description = description, thumbUrl = thumb))
	
	return videoList

def GetVideoUrl(id, quality):
	tempurl = VIDEO_URL + id
               
	#data = open_url(tempurl)
	
	#Log.Debug("opening " + tempurl)
	
	data = HTML.ElementFromURL(tempurl)#, headers = { "Referer"= "http://cls.ctvdigital.net/" })
	
	#Log.Debug("data: " + HTML.StringFromElement(data))
	
	#get the entire rtmpe:// out of the contents of the esi.ctv.ca
	temprtmpe = re.compile('Video.Load\({url:\'(.+?)\'').findall(HTML.StringFromElement(data))
	
	#Log.Debug("rtmpe: " + temprtmpe[0])

	# there are currently 4 very different rtmpe strings from tsn.  My code isn't smart enough to everything
	# so this is a poor workaround
	o = urlparse.urlparse(temprtmpe[0])
	vidquality = int(quality)

	if o.netloc == 'tsn.fcod.llnwd.net':
		firstpart = 'rtmpe://tsn.fcod.llnwd.net/a5504'
		secondpart = re.compile('a5504/(.+?)\'').findall(data)
		playpath = re.compile('ondemand/(.+?).mp4').findall(temprtmpe[0])
		url = firstpart + ' playpath=mp4:' + secondpart[0]
	elif o.netloc == 'ctvmms.rd.llnwd.net':
		firstpart = 'http://ctvmms.vo.llnwd.net/kip0/_pxn=1+_pxI0=Ripod-h264+_pxL0=undefined+_pxM0=+_pxK=19321+_pxE=mp4/'
		secondpart = re.compile('ctvmms.rd.llnwd.net/(.+?).mp4').findall(temprtmpe[0])
		url = firstpart + secondpart[0] + '.mp4'				
	elif o.netloc == 'tsnpmd.akamaihd.edgesuite.net':
		#vidquality=__settings__.getSetting('vidquality')
		#adding 1 to the video quality because I don't use zero as the lowest quality, I use 1 as the lowest quality.
		#vidquality=int(vidquality)+1
	   
		url = temprtmpe[0]
		#starting in version 0.1.5 (March 19 2013) tsn started using adaptive quality in their http streams
		#the quality now goes up to 720p (adaptive_08)
		url = url.replace('Adaptive_04','Adaptive_0' + str(vidquality+3))
	else:
		#break that down into 3 parts so that we can build the final url and playpath
		firstpart = re.compile('rtmpe(.+?)ondemand/').findall(temprtmpe[0])
		firstpart = 'rtmpe' + firstpart[0] + 'ondemand?'
		secondpart = re.compile('\?(.+?)\'').findall(data)
		thirdpart = re.compile('ondemand/(.+?)\?').findall(temprtmpe[0])
		playpath = ' playpath=mp4:' + thirdpart[0]

		#vidquality=__settings__.getSetting('vidquality')
		#adding 1 to the video quality because I don't use zero as the lowest quality, I use 1 as the lowest quality.
		#vidquality=int(vidquality)+1

		#the tsn site adaptivly figures out what quality it should show you (maybe based on your bandwidth somehow?).  We can set the quality outselves in the settings of this plugin
		playpath = playpath.replace('Adaptive_05','Adaptive_0' + str(vidquality))
		playpath = playpath.replace('Adaptive_04','Adaptive_0' + str(vidquality))
		playpath = playpath.replace('Adaptive_03','Adaptive_0' + str(vidquality))
		playpath = playpath.replace('Adaptive_02','Adaptive_0' + str(vidquality))
		playpath = playpath.replace('Adaptive_01','Adaptive_0' + str(vidquality))
		url = firstpart + secondpart[0] + playpath

	return url