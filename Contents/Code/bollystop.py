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
        link = link.replace("id/", "episodes/")
        #Log(link)
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

    for item in html.xpath("//div[@id='serial_episodes']/div/div[2]/a"):
        link=""
        # try:
        # Episode link
        link = item.xpath("./@href")[0]
        episode = item.xpath("./../..//div[@class='episode_date']/text()")[0]
        if not link.startswith("http:"):
            link = SITEURL + link
        # except Exception as e:
        #     raise e

        # Add the found item to the collection
        oc.add(PopupDirectoryObject(key=Callback(PlayerLinksMenu, url=link, title=episode), title=episode))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('EpisodeWarning'))

    return oc


@route(PREFIX + '/bollystop/playerlinksmenu')
def PlayerLinksMenu(url, title):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    sites = html.xpath("//div[@id='serial_episodes']/h3")
    # Add the item to the collection
    for item in sites:
        type = item.xpath("./text()")
        oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=type), title=type))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('PlayerWarning'))

def EpisodeLinksMenu(url, title):
    return

