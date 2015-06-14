import common
import urlparse
import re
import time

SITETITLE = L('ApniTvTitle')
SITEURL = 'http://apni.tv/'
SITETHUMB = 'icon-apnitv.png'

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON

####################################################################################################

@route(PREFIX + '/apnitv/channels')
def ChannelsMenu(url):
    oc = ObjectContainer(title2=SITETITLE)

    html = HTML.ElementFromURL(url)

    for item in html.xpath("//div[@id='navi']/a"):
        try:
            # Channel title
            channel = item.xpath("./text()")[0]
            channel = channel.replace(" Serials", "", 1)

            # Channel link
            link = item.xpath("./@href")[0]
            if link.startswith("http") == False:
                link = SITEURL + link
        except:
            continue

        try:
            image = common.GetThumb(channel.lower())
        except:
            continue

        if channel.lower() in common.GetSupportedChannels():
            oc.add(DirectoryObject(key=Callback(ShowsMenu, url=link, title=channel), title=channel, thumb=image))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=SITETITLE, message=L('ChannelWarning'))

    return oc


####################################################################################################

@route(PREFIX + '/apnitv/showsmenu')
def ShowsMenu(url, title):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    for item in html.xpath("//div[@id='centerblocks']/div[@class='serial']/strong/a"):
        try:
            # Show title
            show = item.xpath("./text()")[0]

            # Show link
            link = item.xpath("./@href")[0]
            if link.startswith("http") == False:
                link = SITEURL + link
        except:
            continue

        # Add the found item to the collection
        oc.add(DirectoryObject(key=Callback(EpisodesMenu, url=link, title=show), title=show))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('ShowWarning'))

    return oc


####################################################################################################

@route(PREFIX + '/apnitv/episodesmenu')
def EpisodesMenu(url, title):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    for item in html.xpath(".//div[contains(@class,'main')]/div/p/a[contains(text(),'Episode')]"):
        try:
            # Episode title
            episode = item.xpath("./text()")[0]
            if "written" in episode.lower():
                continue
            # episode link
            link = item.xpath("./@href")[0]
            if link.startswith("http") == False:
                link = SITEURL + link
        except:
            continue

        # Add the found item to the collection
        oc.add(PopupDirectoryObject(key=Callback(PlayerLinksMenu, url=link, title=episode), title=episode))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('EpisodeWarning'))

    return oc


####################################################################################################

@route(PREFIX + '/apnitv/playerlinksmenu')
def PlayerLinksMenu(url, title):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    sites = html.xpath("//div[@id='centerblocks']/table[@class='list']")
    # Add the item to the collection
    Log(str(len(sites)))
    i = 1
    for item in sites:
        type = "Link " + str(i)
        Log(type)
        oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=type, index=i), title=type))
        i += 1

    # oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type=L('Fastplay')), title=L('Fastplay'), thumb=R('icon-flashplayer.png')))
    # oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type=L('Dailymotion')), title=L('Dailymotion'), thumb=R('icon-dailymotion.png')))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('PlayerWarning'))

    return oc


####################################################################################################

@route(PREFIX + '/apnitv/episodelinksmenu')
def EpisodeLinksMenu(url, title, index):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    items = html.xpath(".//div[@id='centerblocks']/table[" + str(index) + "]/tbody/tr/td/a")
    for item in items:
        link = item.xpath("@href")[0]
        code = HTML.ElementFromURL(link)
        rlink = code.xpath("//div[@id='topsource']/a/@href")[0]
        videosource = getURLSource(rlink)

    # Add the found item to the collection
        if link.find('dailymotion') != -1:
            # Log ('Dailymotion Link: ' + link)
            oc.add(VideoClipObject(
                url=videosource,
                title=videosite,
                thumb=Resource.ContentsOfURLWithFallback(R(ICON), fallback=R(ICON)),
                thumb=Resource.ContentsOfURLWithFallback(R(ICON), fallback=R(ICON)),
                originally_available_at=Datetime.ParseDate(date).date()))
        elif link.find('playwire') != -1:
            oc.add(CreateVideoObject(
                url=videosource,
                title=videosite,
                thumb=Resource.ContentsOfURLWithFallback(R(ICON), fallback=R(ICON)),
                originally_available_at=Datetime.ParseDate(date).date()))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('SourceWarning'))

    return oc


####################################################################################################




def getVideoHost(url):
    return


def GetURLSource(url, referer=None, date=''):
    html = HTML.ElementFromURL(url=url, headers={'Referer': referer})
    string = HTML.StringFromElement(html)

    videocontainer = html.xpath("//div[@class='video_container']")[0]
    return videocontainer.xpath("./iframe/@src")


####################################################################################################

def URLCheck(url):
    url = url.rstrip('\r\n/') + '/'
    if url.startswith("http") == False:
        url = url.lstrip('htp:/')
        url = 'http://' + url
    return url


####################################################################################################

@route(PREFIX + '/apnitv/createvideoobject')
def CreateVideoObject(url, title, thumb, originally_available_at, include_container=False):
    try:
        originally_available_at = Datetime.ParseDate(originally_available_at).date()
    except:
        originally_available_at = None

    container = Container.MP4
    video_codec = VideoCodec.H264
    audio_codec = AudioCodec.AAC
    audio_channels = 2

    video_object = VideoClipObject(
        key=Callback(
            CreateVideoObject,
            url=url,
            title=title,
            thumb=thumb,
            originally_available_at=originally_available_at,
            include_container=True
        ),
        rating_key=url,
        title=title,
        thumb=thumb,
        originally_available_at=originally_available_at,
        items=[
            MediaObject(
                parts=[
                    PartObject(key=url)
                ],
                container=container,
                video_codec=video_codec,
                audio_codec=audio_codec,
                audio_channels=audio_channels
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[video_object])
    else:
        return video_object

        ####################################################################################################
