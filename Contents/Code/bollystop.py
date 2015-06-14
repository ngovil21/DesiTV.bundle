import common
import urlparse
import re
import time

SITETITLE = "BollyStop"
SITEURL = 'http://bollystop.com/'
SITETHUMB = 'icon-desitvbox.png'

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON

####################################################################################################

@route(PREFIX + '/bollystop/channels')
def ChannelsMenu(url):
    oc = ObjectContainer(title2=SITETITLE)

    url = url + "hindi-serial.html"

    html = HTML.ElementFromURL(url)

    for item in html.xpath("//div[@id='content']/div/div[@class='channel_wrapper']/h3/a"):
        try:
            # Channel title
            channel = item.xpath("./text()")[0]
            link = item.xpath("./@href")[0]
            image = item.xpath("../..//img/@src")
            if image:
                if not image[0].startswith("http:"):
                    image[0] = SITEURL + image[0]
                thumb = Resource.ContentsOfURLWithFallback(url=image[0], fallback=R(ICON))
        except:
            continue

        # try:
        #     image = common.GetThumb(channel.lower())
        # except:
        #     image=None

        # if channel.lower() in common.GetSupportedChannels():
        #     Log(channel)
        oc.add(DirectoryObject(key=Callback(ShowsMenu, url=link, title=channel), title=channel, thumb=thumb))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=SITETITLE, message=L('ChannelWarning'))

    return oc

@route(PREFIX + '/bollystop/showsmenu')
def ShowsMenu(url, title):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)
    shows = html.xpath("//ul[@id='main']/li/p[@class='desc']/a")

    for show in shows:
        name = show.xpath("./text()")[0]
        link = show.xpath("./@href")[0]
        link.replace('/id/','/episodes/')
        image = show.xpath("./../../p//img/@src")
        if image:
            if not image[0].startswith("http:"):
                image[0] = SITEURL + image[0]
            thumb = Resource.ContentsOfURLWithFallback(url=image[0], fallback=R(ICON))


        # Add the found item to the collection
        oc.add(DirectoryObject(key=Callback(EpisodesMenu, url=link, title=name), title=name, thumb=thumb))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('ShowWarning'))

    return oc


####################################################################################################

@route(PREFIX + '/bollystop/episodesmenu')
def EpisodesMenu(url, title):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    for item in html.xpath("//div[@id='left-inside']/div/h2[@class='titles']/a"):
        try:
            # Episode title
            episode = item.xpath("./text()")[0]
            if "written" in episode.lower():
                continue
            # episode link
            link = item.xpath("./@href")[0]
            if not link.startswith("http:"):
                link = SITEURL + link
        except:
            continue

        # Add the found item to the collection
        oc.add(PopupDirectoryObject(key=Callback(PlayerLinksMenu, url=link, title=episode), title=episode))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('EpisodeWarning'))

    return oc