import comicScraper
import os
import xml.etree.ElementTree as ET

updateComics = {}

def updateComic():
	xmlPath = "./Category.xml"
	
	if not os.path.exists(xmlPath):
		print("Category.xml doesn't exist.")
	else:
		tree = ET.parse(xmlPath)
		root = tree.getroot()
		urlPaths = root.findall("urlPath")

		f = open("AllNewest.txt", "w+")

		for urlPath in urlPaths:
			comicScraper.urlPath = urlPath.text
			comicScraper.getTitle()
			comicScraper.downloadPicture()

			if comicScraper.isUpdate:
				print(comicScraper.comicTitle + " 更新至 " + comicScraper.outNewestTitle)
				f.write(comicScraper.comicTitle + " 更新至 " + comicScraper.outNewestTitle + "\n")

				global updateComics
				updateComics.update({comicScraper.comicTitle : comicScraper.outNewestTitle})
				comicScraper.isUpdate = False
				
def main():
	if __name__ == "__main__":
		updateComic()

main()