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

chrome_options = Options()
chrome_options.add_argument("--headless") 

urlHost = "https://tw.manhuagui.com"

# user input
urlPath = "/comic/7580/"
if len(sys.argv) > 1:
	urlPath = sys.argv[1]

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

	for block in range(0, blockNum):
		epList = blockList[block].find_elements_by_tag_name("li")
		epNum = len(epList)

		# pagination
		for page in blockList[block].find_elements_by_tag_name("ul"):
			driver.execute_script("arguments[0].setAttribute('style' , 'display:block')", page)

		lastNewest = root.find("title")

		for ep in range(0, epNum):
			chapter = epList[ep].find_element_by_tag_name("a")
			chapterTitle = chapter.get_attribute("title")

			# 去p
			chapterNum = chapter.find_element_by_tag_name("i").text
			chapterNum = chapterNum[0 : len(chapterNum) - 1]

			# update to the last newest
			if lastNewest.text == chapterTitle:
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
				elif len(os.listdir(path + newDirectory)) == int(chapterNum):
					driver.close()
					driver.switch_to.window(driver.window_handles[0])
					break

				with open(fileName, "wb") as f:
					f.write(data)
					f.close()

				tmpImg = Image.open(fileName).convert("RGB")
				tmpImg.save(fileName + jpgType,"jpeg")
				os.remove(fileName)
				
				if i != int(chapterNum) - 1:
					driver.find_element_by_link_text("下一頁").click()
				else:
					driver.close()
					driver.switch_to.window(driver.window_handles[0])

	# update newest
	lastNewest.text = newestTitle
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

def main():
	if __name__ == "__main__":

		getTitle()

		downloadPicture()

		updateCategory()

main()

# bug:/comic/27937/