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
import xml.etree.ElementTree as ET

chrome_options = Options()
chrome_options.add_argument("--headless") 

urlHost = "https://tw.manhuagui.com"

#user input
urlPath = "/comic/31279/"

jpgType = ".jpg"

path = ""

headers = {"Referer" : urlHost, "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}

newestFile = "Newest.xml"

def getTitle():
	html = urlopen(urlHost + urlPath)
	bsObj = BeautifulSoup(html.read(), features = "html.parser")
	global path
	path = "./" + bsObj.find("h1").get_text() + "/"
	if not os.path.exists(path):
				os.makedirs(path)

def downloadPicture():
	driver = webdriver.Chrome(executable_path = "./WebDriver/chromedriver.exe", chrome_options = chrome_options)
	driver.get(urlHost + urlPath)
	epNum = len(driver.find_elements_by_class_name("status0"))
	chapterTitles = []
	chapterNums = []

	xmlPath = path + newestFile

	if os.path.exists(xmlPath):
		tree = ET.parse(xmlPath)
		root = tree.getroot()
	else:
		root = ET.Element("Newest")
		title = ET.SubElement(root, "title")
		tree = ET.ElementTree(root)
		tree.write(xmlPath)


	for ep in range(0, epNum):
		chapter = driver.find_elements_by_class_name("status0")[ep]
		chapterNum = chapter.find_element_by_tag_name("i").text
		chapterNum = chapterNum[0 : len(chapterNum) - 1]
		chapterNums.append(chapterNum)
		chapterTitle = chapter.get_attribute("title")
		chapterTitles.append(chapterTitle)

		if root.find("title").text == chapterTitle:
			root.find("title").text = chapterTitles[0]
			tree.write(xmlPath, "UTF-8")
			break
			
		chapter.click()

		for i in range(0, int(chapterNum)):
			driver.switch_to.window(driver.window_handles[-1])
			picUrl = driver.find_element_by_id("mangaFile").get_attribute("src")
			req = urllib.request.Request(url = picUrl, headers = headers)
			data = urllib.request.urlopen(req).read()
			newDirectory = chapterTitle + "/"
			fileName = path + newDirectory + chapterTitle + "_" + str(i + 1)
			print(fileName)
			if not os.path.exists(path + newDirectory):
				os.makedirs(path + newDirectory)

			with open(fileName, "wb") as f:
				f.write(data)
				f.close()

			tmpImg = Image.open(fileName).convert("RGB")
			tmpImg.save(fileName + jpgType,"jpeg")
			os.remove(fileName)
			
			if i != int(chapterNum) - 1:
				driver.find_element_by_link_text("下一頁").click()
			else:
				driver.find_element_by_link_text("目錄列表").click()
				driver.switch_to.window(driver.window_handles[0])

		if ep == epNum - 1:
			root.find("title").text = chapterTitles[0]
			tree.write(xmlPath, "UTF-8")

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


getTitle()

downloadPicture()

updateCategory()

#bug:/comic/27937/