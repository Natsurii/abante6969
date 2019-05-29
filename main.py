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
import re


	
def fbpost():
	logging.debug('Starting Facebook Thread')

	with open("headlines.txt",encoding='utf-8-sig') as f:
		text = f.read()

	text_model = markovify.NewlineText(text)
	content = text_model.make_short_sentence(60,tries=100)


	f = random.choices(content.split(' '),k=1)
	print(f)
	safe=[]
	for i in f:
		safe.append(re.sub('[\W_]', '',str(i)))
	safe
	string = '%20'.join(safe)


	html = urlopen(f'https://www.philstar.com/search/{string}')
	#html = urlopen('https://www.philstar.com/search/maine%20saka')
	print(html)
	soup = BeautifulSoup(html, 'html.parser')
	#imgs = soup.find_all('a',class_='img-holder')
	

	img = []
	for i in soup.find_all('div', attrs={'class':'tiles_image'}):
		print(i.find('img'))
		img.append(i.find('img'))
	img
	print(img)
	urls =[]
	for i in img:

		print(i['src'])
		urls.append(i['src'])
	urls
	imgurls = random.choice(urls)
	urllib.request.urlretrieve(imgurls, "preface.png")

	size = width, height = 712, 483;

	image = Image.new('RGB', size, 'white')
	preface = Image.open("preface.png")

	article = Image.open('article.png')

	rez = preface.resize((712,373),Image.LANCZOS)
	image.paste(rez,(0,0))
	image.paste(article,(0,0),article)
	draw = ImageDraw.Draw(image)

	ar = ImageFont.truetype('arialbd.ttf', 21) ;

	draw.text((21, 405),content, font=ar, fill='#000000')
	image.save('outfile.png','PNG')
	
	del image
	del draw

	graph = facebook.GraphAPI(access_token=fb_token, version="3.1")

	post = graph.put_photo(image=open('outfile.png',"rb"),
                message=content)

	graph.put_object(parent_object=post['post_id'], connection_name='comments',
                  message='Please hit the mf like button.\n Disclaimer: This is computer generated content. Any headlines that con-incide to real events are purely coincidental.')
	logging.debug('=====================SUCCESS POSTING FB, Exiting....=====================')

fbpost()
schedule.every().hour.at(':35').do(fbpost) # run every xx:35:xx / 35 * * * * on cron 
schedule.every().hour.at(':05').do(fbpost)  # run every xx:5:xx / 5 * * * * on cron 

while 1:
    schedule.run_pending()
    time.sleep(1)
