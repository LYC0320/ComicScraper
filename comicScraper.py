from urllib.request import urlopen
import urllib.request
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from PIL import Image
import os

chrome_options = Options()
chrome_options.add_argument("--headless") 

urlHost = "https://tw.manhuagui.com"

#user input
urlPath = "/comic/13622/"

jpgType = ".jpg"

path = ""

headers = {"Referer" : urlHost, "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}

def getTitle():
	html = urlopen(urlHost + urlPath)
	bsObj = BeautifulSoup(html.read(), features = "html.parser")
	global path
	path = "./" + bsObj.find("h1").get_text() + "/"
	if not os.path.exists(path):
				os.makedirs(path)

def downloadPicture():
	driver = webdriver.Chrome(executable_path = "C:/WebDriver/chromedriver.exe", chrome_options = chrome_options)
	driver.get(urlHost + urlPath)
	chapters = driver.find_elements_by_class_name("status0")
	chapterTitles = []
	chapterNums = []

	for ep in range(0, len(chapters)):
		chapter = driver.find_elements_by_class_name("status0")[ep]

		chapterNum = chapter.find_element_by_tag_name("i").text
		chapterNum = chapterNum[0 : len(chapterNum) - 1]
		chapterNums.append(chapterNum)
		chapterTitles.append(chapter.get_attribute("title"))
		chapter.click()

		for i in range(0, int(chapterNums[len(chapterNums) - 1])):
			driver.switch_to.window(driver.window_handles[-1])
			picUrl = driver.find_element_by_id("mangaFile").get_attribute("src")
			req = urllib.request.Request(url = picUrl, headers = headers)
			data = urllib.request.urlopen(req).read()
			newDirectory = chapterTitles[len(chapterTitles) - 1] + "/"
			fileName = path + newDirectory + chapterTitles[len(chapterTitles) - 1] + "_" + str(i + 1)
			print(fileName)
			if not os.path.exists(path + newDirectory):
				os.makedirs(path + newDirectory)

			with open(fileName, "wb") as f:
				f.write(data)
				f.close()

			tmpImg = Image.open(fileName).convert("RGB")
			tmpImg.save(fileName + jpgType,"jpeg")
			os.remove(fileName)
			
			if i != int(chapterNums[len(chapterNums) - 1]) - 1:
				driver.find_element_by_link_text("下一頁").click()
			else:
				driver.find_element_by_link_text("目錄列表").click()
				driver.switch_to.window(driver.window_handles[0])

getTitle()
downloadPicture()