import threading
import tweepy
import facebook
import random
import logging
import schedule
import time
import datetime
import markovify
from PIL import Image, ImageFont, ImageDraw, ImageOps
from urllib.request import urlopen
import urllib.request
from bs4 import BeautifulSoup
import requests
from io import BytesIO
import os
import re
import textwrap
from dhooks import Embed, Webhook


def fbpost():
	logging.debug('Starting Facebook Thread')

	with open("headlines.txt",encoding='utf-8-sig') as f:
		text = f.read()

	text_model = markovify.NewlineText(text)
	content = text_model.make_short_sentence(100,tries=100)

	r = content.split(' ')
	remove = ['ng', 'nang', 'sa', 'at', 'ang', 'na', 'kay','ni', 'mga', 'nila','nina']
	for i in remove:
		for f in r:
			if i == f:
				r.remove(f)
			else:
				pass
		

	f = random.choices(r,k=1)
	print(f)
	safe=[]
	for i in f:
		safe.append(re.sub('[\W_]', '',str(i)))
	safe
	string = '+'.join(safe)

	html = urlopen(f'https://www.philstar.com/search/{string}/age=720')
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

	ar = ImageFont.truetype('arialbd.ttf', 27) ;
	
	lines = textwrap.wrap(content, width=50)
	y_text = 405
	for line in lines:
		width, height = ar.getsize(line)
		draw.text((21, y_text), line, font=ar, fill='#000000')
		y_text += height

	#draw.text((21, 405),content, font=ar, fill='#000000')
	image.save('outfile.png','PNG')

	del image
	del draw
	
	fb_token = os.environ['TOKEN_PAINTMIN']
	graph = facebook.GraphAPI(access_token=fb_token, version="3.1")

	post = graph.put_photo(image=open('outfile.png',"rb"),
				message=content)

	graph.put_object(parent_object=post['post_id'], connection_name='comments',
				  message='Please hit the mf like button.\n Disclaimer: This is computer generated content. Any headlines that con-incide to real events are purely coincidental.')

	webhook_url = os.environ['WEBHOOK']
	client = Webhook(webhook_url)

	FacebookWebhook = Embed()
	FacebookWebhook.color = 0xC0FFEE# colors should be a hexadecimal value
	FacebookWebhook.description = 'The bot has new content!\n Is this another sentient post or not?'
	FacebookWebhook.add_field(name=content,value=str(datetime.datetime.utcnow() + datetime.timedelta(hours=+8)),inline=False)
	FacebookWebhook.set_image(imgurls)
	FacebookWebhook.set_footer(text=f'\u00A9 AbanteBot6969 | Series of 2019 ',)
	client.send('\u200b', embed=FacebookWebhook)
	logging.debug('=====================SUCCESS POSTING FB, Exiting....=====================')

fbpost()
schedule.every().hour.at(':35').do(fbpost) # run every xx:35:xx / 35 * * * * on cron 
schedule.every().hour.at(':05').do(fbpost)  # run every xx:5:xx / 5 * * * * on cron 

while 1:
	schedule.run_pending()
	time.sleep(1)