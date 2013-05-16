import string


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
	

def ReplaceStreamQuality(url):
	#remove the quality value from the url
	#http://nlds128.cdnak.neulion.com/nlds/nhl/bruins/as/live/bruins_hd_3000.m3u8
	# it will always be at the end between the underscore and dot
	underscoreIndex = string.rfind(url, "_")
	dotIndex = string.rfind(url, ".")
	qualityValue = url[underscoreIndex+1:dotIndex]
	Log.Debug("Quality: " + qualityValue)
	
	return url.replace(qualityValue, "{q}")
	

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
	