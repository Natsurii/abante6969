
import threading
import tweepy
import facebook
import random
import logging
import schedule
import time
from PIL import Image, ImageFont, ImageDraw, ImageOps
from urllib.request import urlopen
import urllib.request
from bs4 import BeautifulSoup
import requests
from io import BytesIO
hl=[]
text = open('headlines_new.txt','a+',encoding='utf-8-sig')
def get_art(page):
	html = urlopen(f'https://www.abante.com.ph/{page}')
	soup = BeautifulSoup(html, 'html.parser')
	art = soup.find_all('a',class_='post-title post-url')
	headlines =[]

	for i in art:
		val = (str(i.get_text()+'\n'))
		hl.append(val)
get_art(page='/')

for i in range(126,150):
	ref =f'/page/{i}'
	get_art(page=ref)
	print(f'done page{i}')


def Remove(duplicate): 
	final_list = [] 
	for num in duplicate: 
		if num not in final_list: 
			final_list.append(num) 
	return final_list 
# Driver Code 


for i in Remove(hl):
	print(f'writing article: {i} to the file.')
	text.write(i)
text.close()
'''
# Driver Code 
print(hl)
dupe = Remove(hl)
for i in dupe:
	print(f'writing article: {i}')
	text.write(i)

'''