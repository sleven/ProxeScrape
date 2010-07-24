
class Search_Book_Page():

	def __init__(self, url="", visited=False, date="never"):
		self.url = url
		self.visited = visited
		self.date = date

	def __repr__(self):
		return "%s %s %s\n" % (self.url, self.visited, self.date)

	def set_url(self, url):
		self.url = url
		
	def set_visited(self, visited):
		self.visited = visited

	def set_date(self, date):
		self.date = date

	
