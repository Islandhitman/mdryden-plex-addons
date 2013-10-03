

class Config:
	def __init__(self, title, sportKeyword, streamFormat, teams):
		self.Title = title
		self.SportKeyword = sportKeyword
		self.StreamFormat = streamFormat
		self.Teams = teams
		

class Game:
	def __init__(self, id, utcStart, homeCity, awayCity, homeServer, awayServer, homeStreamName, awayStreamName):
		self.ID = id
		self.UtcStart = utcStart
		self.HomeCity = homeCity
		self.AwayCity = awayCity
		self.HomeServer = homeServer
		self.AwayServer = awayServer
		self.HomeStreamName = homeStreamName
		self.AwayStreamName = awayStreamName
				
		
class Stream:
	def __init__(self, title, url, team, available):
		self.Title = title
		self.Url = url
		self.Team = team
		self.Available = available
		

	
