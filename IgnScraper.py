import gevent.monkey
gevent.monkey.patch_all()

import json
import urllib3
import os
import bisect
import re
from bs4 import BeautifulSoup

# ********** PlatformSlug Format options *********
# ps4, xbox-one, ps3, pc
# xbox-360, wii, wii-u, 3ds,
# new-nintendo-3ds, nds, nintendo-switch
# vita, psp, iphone, ipad, xbox, gb, gba,
# n64, mac, gcn, dc, ps, ps2, nng
# *************************************************

platforms = ['xbox-one', 'ps3', 'ps4', 'xbox', 'pc',
        'xbox-360', 'wii', 'wii-u', '3ds',
        'new-nintendo-3ds', 'nds', 'nintendo-switch',
        'vita', 'psp', 'iphone', 'ipad', 'gb', 'gba',
        'n64', 'mac', 'gcn', 'dc', 'ps', 'ps2', 'nng' ]

def binarySearch(arr, item):
    low = 0
    high = len(arr)-1

    while low <= high:
        mid = (low + high) // 2
        guess = arr[mid]
        if guess == item:
            return mid
        if guess > item:
            high = mid -1
        else:
            low = mid + 1
    return None

#Game data structure that will be turned into a dictionary (similar to js object)
#and pushed to IgnScrapers games
class GameData(object):
    def __init__(self, name, score, description, content, oneword, platforms, url):
        self.name = name
        self.score = score
        self.description = description
        self.oneword = oneword
        self.content = content
        self.platforms = platforms
        self.url = url

class IgnScraper:
    def __init__(self, platformSlug, games=[]):
        self.root_url = 'http://www.ign.com/reviews/games?platformSlug='+ platformSlug +'&startIndex='
        self.urlList = []
        self.reviewList = []
        self.http = urllib3.PoolManager()

        #sorted array of names that will speed up search of existing gameData
        #the index of a games name will equal the game data's index in the games array
        self.sortedNames = []
        #successfully grabbed data goes here
        self.games = games

        #successfully opened url, but no data was found
        #The data that was collected will still be put in the games list ( successful list)
        self.emptyFields = [] 

        #couldn't open the url at all
        self.failedURLs = []

    def urlopen(self, url):
        return self.http.request(
            'GET',
            url,
            headers={
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': 1,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cookie': 'geoCC=US; _USERCOUNTRY6=US; _ga=GA1.2.2099736787.1528238296; _cb_ls=1; _cb=Bh2oMcD-nwLzDe5EC1; _v__chartbeat3=DKHm1HCoBw51JqSRO;' + 
                          ' __gads=ID=9620a1578b77db33:T=1528238296:S=ALNI_MbXerXr9w1_Epu7hNV6fp3kb2bP4g; optimizelyEndUserId=oeu1528238302000r0.38460126887665;' + 
                          ' optimizelySegments=%7B%221360400627%22%3A%22search%22%2C%221371990448%22%3A%22false%22%2C%221373960443%22%3A%22gc%22%2C%221373960444%22%3A%22none%22%7D; ' +
                           'i10cfd=1; _gid=GA1.2.242024738.1528643017; ign_user_frequency={"lastVisit":"2018-06-10T15:03:40.910Z","oldestVisit":"2018-06-05T22:38:21.175Z",'+
                           '"visits":{"118":{"5":2}}}; zdcse_source=direct; _cb_svref=null; newPrivacyPolicy=closed; OX_plg=pm; _chartbeat5=12,634,%2Freviews%2Fgames,'+
                           'http%3A%2F%2Fwww.ign.com%2Farticles%2F2018%2F06%2F06%2Fthe-elder-scrolls-online-summerset-review%3Fwatch,DH5WJMCYKt41NjukDU5-qPDEiwJO,,c,BT5AgADO6_EgCFnDQjCFoXHXmQuPC,ign.com,;'+
                           ' _gat_UA-71985660-1=1; _chartbeat2=.1528238296292.1528668921163.100001.ZdpPR-XNwdU8hfDYEc3AMNm1J.3; muxData=mux_viewer_id=9cbcf46d-12cd-4408-b927-195806cd6818&msn=0.6236762735498729&sid=3df314cb-05b9-4839-96ea-e51d02ffca0c&sst=1528668920631&sex=1528670422342;'+
                           ' optimizelyBuckets=%7B%2210455061499%22%3A%2210453441056%22%2C%2210841591719%22%3A%2210793845212%22%7D; GED_PLAYLIST_ACTIVITY=W3sidSI6Im5xdkoiLCJ0c2wiOjE1Mjg2Njg5MjMsIm52IjowLCJ1cHQiOjE1Mjg2Njg5MTgsImx0IjoxNTI4NjY4OTE4fV0.; optimizelyPendingLogEvents=%5B%5D'
            }
            ).data


    def tryToGet(self, soup, nodeType, selectType, selectName, childType=None):
        div = soup.find(nodeType, { selectType: selectName })
        if div == None:
            return None
        if childType == None:
            return div.text.strip()
        else:
            return div.findChild(childType).text.strip()
    
    def tryToGetAllChildren(self, soup, nodeType, selectType, selectName, childType):
        parent = soup.find(nodeType, { selectType: selectName })
        if (parent == None):
            return None
        children = parent.find_all(childType)
        if (len(children) < 1):
            return None
        return [child.text for child in children]

    def addToGames(self, game):
        name = game['name']
        idx = binarySearch(self.sortedNames, name)

        if (idx == None):
            #If the game doesn't exist, just add it
            insertIdx = bisect.bisect_left(self.sortedNames, name)
            self.sortedNames.insert(insertIdx, name)
            self.games.insert(insertIdx, game)
        else:
            #Game has already been recorded
            oldGame = self.games[idx]
            self.updateIfBetterData(oldGame, game, 'description')
            self.updateIfBetterData(oldGame, game, 'score')
            self.updateIfBetterData(oldGame, game, 'oneword')
            self.updateIfBetterData(oldGame, game, 'platforms')
    
    def updateIfBetterData(self, oldGame, newGame, attr):
        if (oldGame[attr] == None and newGame[attr] != None):
            oldGame[attr] = newGame[attr]
            if (oldGame['url'] != newGame['url']):
                oldGame['url'] = newGame['url']

    def getBasicInfo(self, url):
        try:
            page = self.urlopen("http://www.ign.com/"+url)
            soup = BeautifulSoup(page, 'html.parser')


            name = self.tryToGet(soup, 'main', 'id', 'main-content', 'h1')
            score=self.tryToGet(soup, 'span', 'class', re.compile("hexagon-content-wrapper$"), 'span')
            content = self.tryToGet(soup, 'section', 'class', 'article-page')
            description=self.tryToGet(soup, 'div', 'class', 'blurb')
            oneword=self.tryToGet(soup, 'div', 'class', 'score-text')
            platforms=self.tryToGet(soup, 'div', 'data-cy', 'platforms-info')[10:]
            url=url.strip()

            game = GameData(name, score, description,content, oneword, platforms, url).__dict__
            self.addToGames(game)

            #This is to create a data structure of data that could be possibly be reviewed
            if (score == None or description == None or oneword == None or platforms == None):
                self.emptyFields.append(game)

            print("Name:", name)
            # print("Score:", score, "-", oneword)
            # print("Desc:", description)
            # #print("Content:", content)
            # print("Url:", url)
            # print("Platforms: ", platforms)
            print("=================================================")
        except:
            print("Cant open url: ", url)
            print("Moving url into failed urls for later use and investigation.")
            self.failedURLs.append(url)

    def getReviewUrls(self,startIdx,step,offset):
        startIdx += offset
        endIdx = startIdx + step - 1 
        print(self.root_url + str(startIdx) + "&endIndex=" + str(endIdx))
        page = self.urlopen(self.root_url + str(startIdx) + "&endIndex=" + str(endIdx) )
        
        soup = BeautifulSoup(page, 'html.parser')
        items = soup.findAll('div', {'class': 'item-details'}, limit = step)
        for child in items:
            #print(child)
            if (child != None):
                nephew = child.findChild('a')
                if nephew == None:
                    nephew = child.find_parent('a')
                self.urlList.append(nephew.get('href'))


    def asyncGetPages(self,n,step,offset):
        gevent.wait([gevent.spawn(self.getReviewUrls,i,step,offset) for i in range(0,n,step)])
        self.reviewList = list(set(self.urlList))


    def run(self,npages,step,offset=0):
        self.asyncGetPages(npages,step,offset)
        for url in self.reviewList:
            self.getBasicInfo(url)

#Fine classe IGNScraper



def scrapertofile(scraper,path):
    '''Writes, for every game in scraper.games, the game to a json file '''
    for game in scraper.games:
        slug = game['url'].split("/").pop()
        with open(f'{path}/{slug}.json','w') as outfile:
            print(f"Writing file {slug}.json..\n")
            json.dump(game,outfile)


def IGNdump(path,platform, ngames, buffer=10, offset=0):
    '''IGN scraping to get ngames reviews from the IGN website for this platform
       offset = starting offset from the review list
       buffer = size of reviews to get each time'''

    if not platform in platforms:
        print(f"\nSyntax Error in the request, {platform} does not exist\n")
        return
    
    scraper = IgnScraper(platform)
    
    try:
        os.mkdir(path)
    except FileExistsError:
        print(f"directory {path} gia' esistente")
    
    scraper.run(ngames,buffer,offset)
    scrapertofile(scraper,path)

def dumpall(platforms,NUM_DOC,STEP,dirpath):
    '''Dumps NUM_DOC reviews for every platforms in platforms, using a step = STEP'''
    for platform in platforms:
        for offset in range(0,NUM_DOC,STEP):
            IGNdump(dirpath,platform,STEP,10,offset)
            
    
