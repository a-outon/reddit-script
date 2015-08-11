#!python3.4 ## Reddit/imgur picture downloader
#This script requires a myconfig.py file on the same directory with variables in order to work

import re, praw, requests, os, glob, sys
from bs4 import BeautifulSoup
from myconfig import * #remember to keep your config file up to date

imgurUrlPattern = re.compile(r'(http://i.imgur.com/(.*))(\?.*)?')
 
def downloadImage(imageUrl, localFileName):
    response = requests.get(imageUrl)
    if response.status_code == 200:
        print('Downloading %s...' % (localFileName))
        with open(localFileName, 'wb') as fo:
            for chunk in response.iter_content(4096):
                fo.write(chunk)

def processReddit(x):
    targetSubreddit = 'streetartporn'
    # Connect to reddit and download the subreddit front page
    r = praw.Reddit(user_agent='Reddit Image Downloader // @halfliquid') # Note: Be sure to change the user-agent to something unique.
    submissions = r.get_subreddit(targetSubreddit).get_top_from_all(limit=55)
     
    # Process all the submissions from the front page
    for submission in submissions:
        # Check for all the cases where we will skip a submission:
        if "imgur.com/" not in submission.url:
            continue # skip non-imgur submissions
        if submission.score < MIN_SCORE:
            continue # skip submissions that haven't even reached the minimum score
        if len(glob.glob('reddit_%s_%s_*' % (targetSubreddit, submission.id))) > 0:
            continue # we've already downloaded files for this reddit submission
     
        if 'http://imgur.com/a/' in submission.url:
            # This is an album submission.
            albumId = submission.url[len('http://imgur.com/a/'):]
            htmlSource = requests.get(submission.url).text
     
            soup = BeautifulSoup(htmlSource, "html.parser")
            matches = soup.select('.album-view-image-link a')
            for match in matches:
                imageUrl = match['href']
                if '?' in imageUrl:
                    imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
                else:
                    imageFile = imageUrl[imageUrl.rfind('/') + 1:]
                localFileName = 'reddit_%s_%s_album_%s_imgur_%s' % (targetSubreddit, submission.id, albumId, imageFile)
                downloadImage('http:' + match['href'], localFileName)
     
        elif 'http://i.imgur.com/' in submission.url:
            # The URL is a direct link to the image.
            mo = imgurUrlPattern.search(submission.url) # using regex here instead of BeautifulSoup because we are pasing a url, not html
     
            imgurFilename = mo.group(2)
            if '?' in imgurFilename:
                # The regex doesn't catch a "?" at the end of the filename, so we remove it here.
                imgurFilename = imgurFilename[:imgurFilename.find('?')]
     
            localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (targetSubreddit, submission.id, imgurFilename)
            downloadImage(submission.url, localFileName)
     
        elif 'http://imgur.com/' in submission.url:
            # This is an Imgur page with a single image.
            htmlSource = requests.get(submission.url).text # download the image's page
            soup = BeautifulSoup(htmlSource, "html.parser")
            imageUrl = soup.select('.image a')[0]['href']
            if imageUrl.startswith('//'):
                # if no schema is supplied in the url, prepend 'http:' to it
                imageUrl = 'http:' + imageUrl
            imageId = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('.')]
     
            if '?' in imageUrl:
                imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
            else:
                imageFile = imageUrl[imageUrl.rfind('/') + 1:]
     
            localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (targetSubreddit, submission.id, imageFile)
            downloadImage(imageUrl, localFileName)

#this loop will run 'processReddit()' with the variables set on "myconfig.py"
def autoMatic():
    for i in range(0,n):
        print ('##' + '\n' + '>> Processing /r/' + subs[i] + '...')
        processReddit(subs[i])
        print ('>> Pictures from /r/' + subs[i] + ' have been downloaded.')
        i+=1

#this loop will let you decide what subreddits to download
def mainMenu():
    z = 'l'
    while z != 'x':
        print ('a = spaceporn' + '\n' + 'b = cityporn' + '\n' + 'c = earthporn' + '\n' + 'd = foodporn' + '\n' + 'e = waterporn' + '\n' + 'f = imaginarylandscapes' + '\n' + 'g = movieposterporn' + '\n' + 'h = artporn' + '\n' + 'i = graffiti' + '\n' + '\n' + '\n' + 'x = exit')
        x = input()
        processReddit(x)

#mainMenu()
#autoMatic()       
processReddit('comicbookporn')
