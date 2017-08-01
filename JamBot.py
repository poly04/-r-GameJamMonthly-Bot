from datetime import datetime
from lxml import html
import praw
import Config
import time
import requests
from contextlib import closing
from selenium.webdriver import Edge # pip install selenium
from selenium.webdriver.support.ui import WebDriverWait
import calendar

def login():
	r = praw.Reddit(username = Config.username,
				password = Config.password,
				client_id = Config.client_id,
				client_secret = Config.client_secret,
				user_agent = "Game Jam Bot v0.1")
	return r
				
def getTheme():
	with closing(Edge()) as browser:
		browser.get("https://cjanssen.bitbucket.io/themegen")
		# wait for the page to load
		WebDriverWait(browser, timeout=10).until(
			lambda x: x.find_element_by_id('themefield'))
		# store it to string variable
		page_source = browser.page_source
	tree = html.fromstring(page_source)
	theme = tree.xpath('//div[@id="themefield"]/text()')
	print("Theme: ", theme)
	return theme
				
def remove_prefix(string):
	return string[2:]
				
def remove_lastChar(string):
	return string[:-2]
				
def run_bot(r):
	if datetime.now().day == 1: #day set to current day for testing. Set to 1 in release.
		print ("It's the first, updating Game Jam...")
		
		#pick theme based on the voting thread
		print ("Picking theme...")
		subreddit = r.subreddit('GameJamMonthly')
		for submission in subreddit.hot():
			if submission.stickied:
				if datetime.now().month == 1:
					if submission.title == "December " + (datetime.now().year - 1) + " Voting Thread":
						submission.comment_sort = 'best'
						submission.comments.replace_more(limit=0)
						currentTheme = submission.comments[0].body
				else:
					if submission.title == calendar.month_name[datetime.now().month] + " " + str(datetime.now().year) + " Voting Thread":
						submission.comment_sort = 'best'
						submission.comments.replace_more(limit=0)
						currentTheme = submission.comments[0].body
					else:
						print("Cannot find thread. Sorry!")
		print ("Theme picked!")
		
		#unsticky voting thread and old jam thread
		print ("Unstickying threads...")
		for submission in subreddit.hot():
			if submission.stickied:
				submission.mod.sticky(state=False)
		print ("Threads unstickyed!")
		
		#write post for theme
		print ("Writing theme post")
		postid = subreddit.submit(title=calendar.month_name[datetime.now().month] + " " + str(datetime.now().year) + " " + currentTheme,
								  selftext="Hello everyone.\n\nThis month has a theme!  \nHave fun!")
		post = r.submission(id=postid)
		post.mod.sticky()
		print ("Theme post submitted!")
		
		#generate 5 themes
		print ("Generating Themes...")
		theme1 = getTheme()
		theme2 = getTheme()
		theme3 = getTheme()
		theme4 = getTheme()
		theme5 = getTheme()
		print ("Generation Done!")
		
		#write contest-mode post for theme voting.
		print ("Creating post...")
		if datetime.now().month == 12:
			postid = r.subreddit("GameJamMonthly").submit(title = "January " + str(datetime.now().year + 1) + " Voting Thread", 
								 selftext="Hello everyone, welcome to the voting thread. This thread is for next month's jam. Vote for your favourite!")
		else:
			postid = r.subreddit("GameJamMonthly").submit(title = calendar.month_name[datetime.now().month + 1] + " " + str(datetime.now().year) + " Voting Thread", 
								 selftext="Hello everyone, welcome to the voting thread. This thread is for next month's jam. Vote for your favourite!")
		
		#set contest mode true
		post = r.submission(id=postid)
		post.mod.contest_mode(state = True)
		post.mod.sticky()
		print ("Post submitted!")
		
		#comment all the themes
		print ("Commenting themes...")
		post.reply("Theme: " + remove_lastChar(remove_prefix(str(theme1))))
		post.reply("Theme: " + remove_lastChar(remove_prefix(str(theme2))))
		post.reply("Theme: " + remove_lastChar(remove_prefix(str(theme3))))
		post.reply("Theme: " + remove_lastChar(remove_prefix(str(theme4))))
		post.reply("Theme: " + remove_lastChar(remove_prefix(str(theme5))))
		print ("Themes commented!")
		
		print ("Game jam updated!")
		
	else:
		print ("It's not the first.")
	
				
r = login()

run_bot(r)

