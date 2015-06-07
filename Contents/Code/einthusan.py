import common
import urlparse
import re
import time

SITETITLE = 'Einthusan'
SITEURL = 'http://http://einthusan.com/'
SITETHUMB = 'icon-apnitv.png'

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON

@route(PREFIX + '/einthusan/languages')
def LanguagesMenu(url):
    oc = ObjectContainer(title2=SITETITLE)

    oc.add(DirectoryObject(key=Callback(MainMenu, url=url + 'index.php?lang=hindi', title='Hindi'), title='Hindi'))
    oc.add(DirectoryObject(key=Callback(MainMenu, url=url + 'index.php?lang=tamil', title='Tamil'), title='Hindi'))
    oc.add(DirectoryObject(key=Callback(MainMenu, url=url + 'index.php?lang=telegu', title='Telegu'), title='Telegu'))
    oc.add(DirectoryObject(key=Callback(MainMenu, url=url + 'index.php?lang=malayalam', title='Malayalam'), title='Malayalam'))

    return oc


@route(PREFIX + '/einthusan/main')
def MainMenu(url,title):

    oc = ObjectContainter(title2=title)

    oc.add(DirectoryObject(key=Callback(ShowcaseMenu, url=url, title='Showcase'), title='Showcase'))

    return oc

@route(PREFIX + '/einthusan/showcase')
def ShowcaseMenu(url,title):

    oc = ObjectContainter(title2=title)
    html = html = HTML.ElementFromURL(url)

    for item in html.xpath("//div[@id='movie-showcase-slides']//a[@class='movie-title']"):
        try:
            link = item.xpath("./@href")[0]
            title = item.xpath("./text()")[0]
        except:
            continue

        oc.add(DirectoryObject(key=Callback(PlayMovie, url=link, title=title), title=title))

    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('ShowWarning'))

    return oc

@route(PREFIX + '/einthusan/movie')
def PlayMovie(url,title):
