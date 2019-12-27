import facebook
import tweepy
import random
import logging
import schedule
import time
import datetime
import markovify
from PIL import Image, ImageFont, ImageDraw, ImageOps
import urllib.request
from bs4 import BeautifulSoup
import requests
from io import BytesIO
import os
import re
import textwrap
from dhooks import Embed, Webhook


logging.basicConfig(level=logging.INFO)

def headline_factory():
	"""Creates and generates the headline."""
	logging.info('Creating Headline...')
	with open("headlines.txt",encoding='utf-8-sig') as f:
		logging.info('Opening corpus1...')
		text = f.read()

	with open("seagames.txt",encoding='utf-8-sig') as f:
		logging.info('Opening corpus2...')
		text2 = f.read()

	text_model1 = markovify.NewlineText(text, state_size = 3)
#	definitive_model = markovify.Text(string(text_model1))
#	sg = markovify.NewlineText(text2)
#	model = markovify.combine([sg, text_model1], [1.5, 0.2])
#	initword  = ['Pasko','christmas','new year', 'regalo', 'bagong taon', 'paputok', 'fireworks']
#	content = text_model1.make_sentence_with_start(beginning = 'pasko', strict = False, tries=100)
	content = text_model1.make_short_sentence(100)
	logging.info(f'Headline created! \n {content}')
	return content

def query_sanitizer(content):
	"""Sanitize and create keyword queries for searching images."""
	headstring = content.split(' ')
	remove = ['ng', 'nang', 'sa', 'at', 'ang', 'na', 'kay','ni', 'mga', 'nila', 'nina', 'si', 'may','dahil', ' ']
	for i in remove:
		for f in headstring:
			if (i.casefold() == f.casefold()):
				headstring.remove(f)
			else:
				pass
	logging.info('The query has been sanitized.')
	query = random.sample(set(headstring),3)

	safe=[]
	for i in query: #for UTF-8 and Non-alphanumeric
		safe.append(re.sub('[\W_]', '',str(i)))
	logging.info('The keyword has been created.')
	return safe

def miso_soup(ingridient, type):
	"""Beautiful Soup necessary image."""
	souped=[]
	if type == 0: #Abante main page
		for i in ingridient:
			req = urllib.request.Request(f"https://www.abante.com.ph/?s={i}", None, {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'})
			response = urllib.request.urlopen(req).read()
			soup = BeautifulSoup(response, 'html.parser')
			heat = soup.find('div', attrs={'class':'col-sm-8 content-column'})
			for i in heat.find_all('div', attrs={'class':'featured clearfix'}):
				read = i.find('a')
				spooned = read['data-src']
				souped.append(spooned)

	elif type == 1:
		for i in ingridient:
			html = urllib.request.urlopen(f'https://www.philstar.com/search/{i}/age=720').read()
			soup = BeautifulSoup(html, 'html.parser')
			for i in soup.find_all('div', attrs={'class':'tiles_image'}):
				read = i.find('img')
				spooned = read['src']
				souped.append(spooned)

	image_url = random.choice(souped)

	logging.info('Image souped and spooned successfully.')
	return image_url

def image_factory(photo, content, save):
	size = width, height = 712, 483;
	image = Image.new('RGB', size, 'white')

	response = urllib.request.urlopen(photo)
	contents = BytesIO(response.read())
	preface = Image.open(contents)

	logging.info('Image Received, Generating...')

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

	logging.info('Image generated!')
	if save == 1: # 1 to save the image
		image.save('outfile.png', format="PNG")
	elif save == 0:
		with BytesIO() as output:
			image.save(output, format="PNG")
			imgbyte = output.getvalue()
		return imgbyte

def facebook_poster(image,caption):
	fb_token = os.environ['TOKEN_PAINTMIN']
	graph = facebook.GraphAPI(access_token=fb_token, version="3.1")

	post = graph.put_photo(image=image, message=caption)

	comment='''
	Holidays Edition
	Please like our page for more content.
	Disclaimer: This is computer generated content.
	Any headlines that con-incide to real events are purely coincidental.
	For more inquiries, Join us on Discord: https://discord.gg/YG9wEgE
	'''
	graph.put_object(parent_object=post['post_id'], connection_name='comments',message=comment)
	logging.info('Image posted! on facebook')

def tweet_image(filename, message):
	consumer_key = os.environ['TWITTER_CONSUMERKEY']
	consumer_secret = os.environ['TWITTER_CONSUMERSECRET']
	access_token = os.environ['TWITTER_TOKEN']
	access_token_secret = os.environ['TWITTER_TOKENSECRET']
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	api.update_with_media(filename, status=message)
	os.remove(filename)


def main():
	headlines = headline_factory() #strings
	try:
		keywords = query_sanitizer(content=headlines) 
	except ValueError as e:
		pass
		logging.warning(e)
		logging.info('Shit, your headlines sucks. DECLINED')
	finally:
		souped_photo = miso_soup(ingridient=keywords, type=1)
		img = image_factory(photo=souped_photo, content=headlines, save=0)
		facebook_poster(image=img,caption=headlines)

def tweeter():
	headlines = headline_factory() #strings
	try:
		keywords = query_sanitizer(content=headlines) 
	except ValueError as e:
		pass
		logging.warning(e)
		logging.info('Shit, your headlines sucks. DECLINED')
	finally:
		souped_photo = miso_soup(ingridient=keywords, type=1)
		img = image_factory(photo=souped_photo, content=headlines, save=1)
		tweet_image(filename = 'outfile.png', message =headlines)

main()
tweeter()
schedule.every().hour.at(':35').do(main) # run every xx:35:xx / 35 * * * * on cron 
schedule.every().hour.at(':05').do(main)  # run every xx:5:xx / 5 * * * * on cron 
schedule.every().hour.at(':10').do(tweeter)
schedule.every().hour.at(':40').do(tweeter)

while 1:
	schedule.run_pending()
	time.sleep(1)