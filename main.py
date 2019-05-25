import threading
import tweepy
import facebook
import random
import logging
import schedule
import time
import markovify
from PIL import Image, ImageFont, ImageDraw, ImageOps
from urllib.request import urlopen
import urllib.request
from bs4 import BeautifulSoup
import requests
from io import BytesIO
import os


	
def fbpost():
	logging.debug('Starting Facebook Thread')

	fb_token = os.environ['TOKEN_PAINTMIN']
	with open("headlines.txt",encoding='utf-8-sig') as f:
		text = f.read()

	text_model = markovify.NewlineText(text)
	content = text_model.make_short_sentence(100,tries=100)
	print(content)

	graph = facebook.GraphAPI(access_token=fb_token, version="3.1")

	post = graph.put_photo(image=open('white.png',"rb"),
                message=content)

	graph.put_object(parent_object=post['post_id'], connection_name='comments',
                  message='Please hit the mf like button.\n Disclaimer: This is computer generated content. Any headlines that con-incide to real events are purely coincidental.')
	logging.debug('=====================SUCCESS POSTING FB, Exiting....=====================')

fbpost()
schedule.every(30).minutes.do(fbpost)

while 1:
    schedule.run_pending()
    time.sleep(1)
