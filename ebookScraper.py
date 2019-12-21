#! /usr/bin/python3
# ebookScraper.py - A web scraper which downloads ebook files from www.standardebooks.org

import os
import sys
import requests
import bs4
import json

## Functions
# Return list (of dictionaries) of all ebooks
def gatherBooks(url):
    bookList = []
    # Download first page and collect nav page URLs
    navResponse = requests.get(url)
    navResponse.raise_for_status()
    soup = bs4.BeautifulSoup(navResponse.text, 'html.parser')
    navSelect = soup.select('.ebooks nav li a')[1:]
    navPages = [url]
    for i in range(len(navSelect)):
        navPages.append(baseURL + navSelect[i].get('href'))
    
    # Collect data for loading bar
    navTotal = len(navPages)
    navCurrent = 0

    # Loop through nav pages
    for navPage in navPages:
        navCurrent += 1
        navNextResponse = requests.get(navPage)
        navNextResponse.raise_for_status()
        navNextSoup = bs4.BeautifulSoup(navNextResponse.text, 'html.parser')
        # Overwrite the same line displaying download percentage
        print('Gathering ebook details: ', end='', flush=True)
        print('[{:>7.2%}]\r'.format(navCurrent/navTotal), end='', flush=True)

        # Retrieve book/page details and populate book list
        bookPages = navNextSoup.find('ol')
        for li in bookPages.find_all('li'):
            bookTitle = li.find('p').find('a').text
            bookAuthor = li.find(class_ = 'author').find('a').text
            bookURL = baseURL + li.find('a').get('href')
            bookList.append({'title': bookTitle, 'author': bookAuthor, 'url': bookURL})
    return bookList

# Download specified files of a given ebook
def downloadBook(bookURL, siteURL, kindle = False):
    # Download ebook page
    bookResponse = requests.get(bookURL)
    bookResponse.raise_for_status()
    bookSoup = bs4.BeautifulSoup(bookResponse.text, 'html.parser')

    # Collect URLs of ebook files
    azw3Elem = bookSoup.select('.amazon')
    kepubElem = bookSoup.select('.kobo')
    epubElem = bookSoup.select('.epub')

    azw3URL = siteURL + azw3Elem[0].get('href')
    kepubURL = siteURL + kepubElem[0].get('href')
    epubURL = siteURL + epubElem[0].get('href')
    epub3URL = siteURL + epubElem[1].get('href')

    coverElem = bookSoup.find('a', string='Kindle cover thumbnail')
    coverURL = siteURL + coverElem.get('href')

    # If Kindle directories not detected, create book sub-directories
    # otherwise, download azw3 and thumbnail files to target dir for distribution
    if kindle == False:
        eBookFiles = [azw3URL, kepubURL, epubURL, epub3URL, coverURL]
        bookDir = os.path.splitext(os.path.basename(azw3URL))[0].title()
        os.makedirs(bookDir, exist_ok=True)
    elif kindle == True:
        eBookFiles = [azw3URL, coverURL]
        bookDir = targetDir


    bookDetails = bookSoup.find('meta', property='og:title').get('content')

    # Download ebook files
    print('Downloading:  %s...' % bookDetails)
    for eBookFile in eBookFiles:
        fileName = os.path.join(bookDir, os.path.basename(eBookFile))
        if not os.path.exists(fileName):
            dlResponse = requests.get(eBookFile)
            dlResponse.raise_for_status()
            ebFile = open(fileName, 'wb')
            for chunk in dlResponse.iter_content(100000):
                ebFile.write(chunk)
            ebFile.close()
        print('.', end = '')
    print('Complete!')

# Loop through list of ebooks for download
def downloadList(bookList, downloadDir):
    # Verify and move to target directory
    try:
        os.makedirs(downloadDir, exist_ok=True)
        os.chdir(downloadDir)
        print('Downloading eBooks...')
    except OSError:
        print(f'Cannot download to: {downloadDir}. Please provide a valid path.')
        #TODO: print usage message
        sys.exit()
    
    for book in bookList:
        downloadBook(book['url'], baseURL)

#TODO: Implement selection feature
def presentList(bookList):
    selectedBooks = []
    #TODO: Present bookList to user, allow user selection, pass selectedBooks to downloadList
    #downloadList(selectedBooks, targetDir)
    for index, book in enumerate(bookList):
        title = book['title']
        author = book['author']
        print(f'[ {index} ] {title} - {author}')

    userInput = ''
    while userInput != 'x':
        userInput = input('Enter book number to add it to download list: ')
        #selection = bookList[int(userInput)]
        if userInput != 'x':
            selectedBooks.append(bookList[int(userInput)])
        else:
            continue

    if not selectedBooks:
        downloadList(selectedBooks, targetDir)



## Variables
dirName = 'standardEbooks'
currentDir = os.path.join(os.getcwd(), dirName)
baseURL = 'https://standardebooks.org'
newURL = 'https://standardebooks.org/ebooks/'
alphaURL = 'https://standardebooks.org/ebooks/?sort=author-alpha'
targetDir = ''
#TODO: Usage message


## Initialise
# Determine mode; determine path
if len(sys.argv) == 2:
    targetDir = currentDir
    if sys.argv[1] == '-a':
        downloadList(gatherBooks(alphaURL), targetDir)
    elif sys.argv[1] == '-s':
        presentList(gatherBooks(alphaURL))
    else:
        #TODO: display error and usage message
        sys.exit()
elif len(sys.argv) == 3:
    targetDir = os.path.join(sys.argv[2], dirName)
    if sys.argv[1] == '-a':
        downloadList(gatherBooks(alphaURL), targetDir)
    elif sys.argv[1] == '-s':
        presentList(gatherBooks(alphaURL))
    else:
        #TODO: display error and usage message
        sys.exit()
else:
    #TODO: display error and print usage message
    sys.exit() 


