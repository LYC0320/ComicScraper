from urllib.request import urlopen
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from PIL import Image
import os
import xml.etree.ElementTree as ET
import sys
import re
import time
from urllib.parse import quote
import json
<<<<<<< HEAD
import random
=======
from fake_useragent import UserAgent

# Fake User Agent Instance
ua = UserAgent()
>>>>>>> 64eba5827e36f1811a6cb8b6ff31ddabae7e75fe

chrome_options = Options()
chrome_options.add_argument("--headless")

# hide log
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--silent")

urlHost = "https://tw.manhuagui.com"
urlSearch = "/tools/word.ashx?"
isWrite = False
urlPath = "/comic/7580/"
fileType = ".jpg"
path = ""
<<<<<<< HEAD
headers = {"Referer" : urlHost, "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/ 81.0.4044.122 Safari/537.36"}
=======
headers = {"Referer" : urlHost, "User-Agent" : ua.random}
>>>>>>> 64eba5827e36f1811a6cb8b6ff31ddabae7e75fe
newestFile = "Newest.xml"
bsObj = ""
comicTitle = ""
isUpdate = 0
outNewestTitle = ""
percentage = 0
interval = 2

# user input
if len(sys.argv) == 2:
	urlPath = sys.argv[1]
elif len(sys.argv) == 3:
	urlPath = sys.argv[1]
	isWrite = sys.argv[2]

def writeFile(string):
	if isWrite == "1":
		f = open(comicTitle + ".txt", "w")
		f.write(string)
		f.close()

def converToUrlPath(comicName):
	keyString = "key=" + quote(comicName)
	html = urlopen(urlHost + urlSearch + keyString)
	bsObj = BeautifulSoup(html.read(), features = "html.parser").text
	data = json.loads(bsObj)
	return data

def getTitle():
	html = urlopen(urlHost + urlPath)

	global bsObj
	bsObj = BeautifulSoup(html.read(), features = "html.parser")

	global comicTitle
	comicTitle = bsObj.find("h1").get_text()

	global path
	path = "./Comics/" + comicTitle + "/"
	if not os.path.exists(path):
				os.makedirs(path)

def downloadPicture():
	driver = webdriver.Chrome(executable_path = "./WebDriver/chromedriver.exe", chrome_options = chrome_options)
	driver.get(urlHost + urlPath)

	# check adult
	if bsObj.find("a", {"id" : "checkAdult"}):
		driver.add_cookie({"name" : "isAdult", "value" : "1"})
		driver.refresh()

	blockList = driver.find_elements_by_css_selector("div[class = 'chapter-list cf mt10']")

	blockNum = len(blockList)

	# create newest xml
	xmlPath = path + newestFile

	if os.path.exists(xmlPath):
		tree = ET.parse(xmlPath)
		root = tree.getroot()
	else:
		root = ET.Element("Newest")
		title = ET.SubElement(root, "title")
		title.text = "0"
		tree = ET.ElementTree(root)
		tree.write(xmlPath)

	newestTitle = driver.find_element_by_css_selector("ul[style = 'display:block']").find_element_by_tag_name("a").get_attribute("title")

	block = 0

	# compute percentage
	epAll = 0
	epCount = 0

	for blockEle in blockList:
		epList = blockEle.find_elements_by_tag_name("li")
		epAll += len(epList)
	# compute percentage

	while block < blockNum:
		
		#prevent ban
		interval = random.randint(2, 5)
		time.sleep(interval)

		epList = blockList[block].find_elements_by_tag_name("li")
		epNum = len(epList)

		# pagination (攤開)
		for page in blockList[block].find_elements_by_tag_name("ul"):
			driver.execute_script("arguments[0].setAttribute('style' , 'display:block')", page)

		lastNewest = root.find("title")

		for ep in range(0, epNum):

			#prevent ban
			interval = random.randint(2, 5)
			time.sleep(interval)

			global percentage
			percentage = round((epCount + ep) / epAll * 100)
			writeFile(str(percentage))
			

			chapter = epList[ep].find_element_by_tag_name("a")
			chapterTitle = chapter.get_attribute("title")
			
			# dir can not contain some chacracter
			chapterTitle = chapterTitle.replace("?", "")

			# 去p
			chapterNum = chapter.find_element_by_tag_name("i").text
			chapterNum = chapterNum[0 : len(chapterNum) - 1]

			# update to the last newest
			if lastNewest.text == chapterTitle:
				# accelerate
				block = blockNum - 1
				break

			chapter.click()

			for i in range(0, int(chapterNum)):
				driver.switch_to.window(driver.window_handles[-1])

				#prevent ban
				interval = random.randint(2, 5)
				time.sleep(interval)

				picUrl = driver.find_element_by_id("mangaFile").get_attribute("src")
				req = urllib.request.Request(url = picUrl, headers = headers)
				data = urllib.request.urlopen(req).read()
				newDirectory = chapterTitle + "/"

				fileName = path + newDirectory + chapterTitle + "_" + str(i + 1)
				print(fileName)
				if not os.path.exists(path + newDirectory):
					os.makedirs(path + newDirectory)
				elif len(os.listdir(path + newDirectory)) >= int(chapterNum):
					driver.close()
					driver.switch_to.window(driver.window_handles[0])
					break

				with open(fileName, "wb") as f:
					f.write(data)
					f.close()

				tmpImg = Image.open(fileName).convert("RGB")
				tmpImg.save(fileName + fileType,"jpeg")
				os.remove(fileName)
				
				if i != int(chapterNum) - 1:
					driver.find_element_by_link_text("下一頁").click()
				else:
					driver.close()
					driver.switch_to.window(driver.window_handles[0])

		epCount += epNum

		block += 1
		
	percentage = 100
	writeFile(str(percentage))

	# update newest
	if lastNewest.text != newestTitle:
			lastNewest.text = newestTitle
			tree.write(xmlPath, "UTF-8")

			global isUpdate
			isUpdate = True

			global outNewestTitle
			outNewestTitle = newestTitle
		
def updateCategory():
	xmlPath = "./Category.xml"

	if os.path.exists(xmlPath):
		tree = ET.parse(xmlPath)
		root = tree.getroot()
		subElements = root.findall("urlPath")
		subElementsNum = len(subElements)

		for i in range(0, subElementsNum):
			if urlPath == subElements[i].text:
				break

			if i == subElementsNum - 1:
				subElement = ET.SubElement(root, "urlPath")
				subElement.text = urlPath
				tree.write(xmlPath)
	else:
		root = ET.Element("Category")
		subElement = ET.SubElement(root, "urlPath")
		subElement.text = urlPath
		tree = ET.ElementTree(root)
		tree.write(xmlPath)

def main2():
	getTitle()
	downloadPicture()
	updateCategory()

def main():
	if __name__ == "__main__":

		getTitle()

		downloadPicture()

		updateCategory()

main()