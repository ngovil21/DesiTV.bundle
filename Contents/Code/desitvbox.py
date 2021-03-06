import common
import urlparse
import re
import time

SITETITLE = "Desi TV Box"
SITEURL = 'http://www.desitvbox.me/'
SITETHUMB = 'icon-desitvbox.png'

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON

####################################################################################################

@route(PREFIX + '/desitvbox/channels')
def ChannelsMenu(url):
    oc = ObjectContainer(title2=SITETITLE)

    html = HTML.ElementFromURL(url)

    for item in html.xpath("//div[@id='left-inside']/div/table/tbody/tr/td/strong"):
        try:
            # Channel title
            channel = item.xpath("./text()")[0]
        except:
            continue

        try:
            image = common.GetThumb(channel.lower())
        except:
            continue

        if channel.lower() in common.GetSupportedChannels():
            oc.add(DirectoryObject(key=Callback(ShowsMenu, url=url, title=channel), title=channel, thumb=image))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=SITETITLE, message=L('ChannelWarning'))

    return oc


####################################################################################################

@route(PREFIX + '/desitvbox/showsmenu')
def ShowsMenu(url, title):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)
    channel = html.xpath("//div[@id='left-inside']/div/table/tbody/tr/td/strong[contains(text(),'" + title + "')]/..")[
        0]

    for show in channel.xpath(".//li/a"):
        name = show.xpath("./text()")[0]
        link = show.xpath("./@href")[0]

        # Add the found item to the collection
        oc.add(DirectoryObject(key=Callback(EpisodesMenu, url=link, title=name), title=name))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('ShowWarning'))

    return oc


####################################################################################################

@route(PREFIX + '/desitvbox/episodesmenu')
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


####################################################################################################

@route(PREFIX + '/desitvbox/playerlinksmenu')
def PlayerLinksMenu(url, title):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    sites = html.xpath(".//*[@id='left-inside']/div/center/p/strong")
    # Add the item to the collection
    count = 1
    for item in sites:
        type = item.xpath("./text()")[0]
        oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=type, index=count), title=type))
        count += 1

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('PlayerWarning'))

    return oc


####################################################################################################

@route(PREFIX + '/desitvbox/episodelinksmenu')
def EpisodeLinksMenu(url, title, index):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    items = html.xpath(".//*[@id='centercol']/table[" + str(index) + "]/tbody/tr/td/a")

    for item in items:
        try:
            # Video site
            # videosite = item.xpath("./text()")[0]
            # Video link
            link = item.xpath("./@href")[0]
            link = getVideoHost(link)
            # Show date
            date = GetShowDate(videosite)
            # Get video source url and thumb
            link = GetURLSource(link, url, date)
        except:
            continue

        # Add the found item to the collection
        if link.find('dailymotion') != -1:
            # Log ('Dailymotion Link: ' + link)
            oc.add(VideoClipObject(
                url=link,
                title=videosite,
                thumb=Resource.ContentsOfURLWithFallback(R(ICON), fallback=R(ICON)),
                originally_available_at=Datetime.ParseDate(date).date()))
        elif link.find('playwire') != -1:
            oc.add(CreateVideoObject(
                url=link,
                title=videosite,
                thumb=Resource.ContentsOfURLWithFallback(R(ICON), fallback=R(ICON)),
                originally_available_at=Datetime.ParseDate(date).date()))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('SourceWarning'))

    return oc


####################################################################################################


def getVideoHost(url):
    html = HTML.ElementFromURL(url)
    link = html.xpath(".//*[@id='topsource']/a/@href")

    string = HTML.StringFromElement(link)

    match = re.search("http:\/\/[\w]+\.com\/\?host=(?P<host>\w+?)&video=(?P<link>\w+)", string)
    videohost = match.group("host")
    link = match.group("link")


def GetURLSource(url, referer, date=''):
    html = HTML.ElementFromURL(url=url, headers={'Referer': referer})
    string = HTML.StringFromElement(html)

    if string.find('dailymotion') != -1:
        url = html.xpath("//div[@id='topsource']/a/@href")[0]
    elif string.find('fastplay') != -1:
        url = html.xpath("//div[@id='topsource']/a/@href")[0]

        html = HTML.ElementFromURL(url=url, headers={'Referer': url})
        string = HTML.StringFromElement(html)

        if string.find('playwire') != -1:
            url = 'http://cdn.playwire.com/' + html.xpath("//script/@data-publisher-id")[0] + '/video-' + date + '-' + \
                  html.xpath("//script/@data-video-id")[0] + '.mp4'
        elif string.find('dailymotion') != -1:
            url = html.xpath("//iframe[contains(@src,'dailymotion')]/@src")[0]
            if url.startswith("http") == False:
                url = url.lstrip('htp:/')
                url = 'http://' + url

    return url


####################################################################################################

def GetDailymotion(html):
    items = html.xpath(
        "//table[@class='list']/tr[@class='heading' and contains(td/text(),'Dailymotion')]/following-sibling::tr/td/a")
    return items


####################################################################################################

def GetFlashPlayer(html):
    items = html.xpath(
        "//table[@class='list']/tr[@class='heading' and contains(td/text(),'Fastplay')]/following-sibling::tr/td/a")
    return items


####################################################################################################

def GetShowDate(title):
    # find the date in the show title
    match = re.search(r'\w+\s\d{1,2}[thsrdn]+\s\d{4}', title)
    # Log ('match: ' + match.group())
    # remove the prefix from date
    match = re.sub(r'(st|nd|rd|th)', "", match.group())
    if match.find('Augu') != -1:
        match = match.replace("Augu", "August", 1)
    # strip date to struct
    date = time.strptime(match, '%B %d %Y')
    # convert date
    date = time.strftime('%Y%m%d', date)
    # Log ('Date: ' + date)
    return date


####################################################################################################

def URLCheck(url):
    url = url.rstrip('\r\n/') + '/'
    if url.startswith("http") == False:
        url = url.lstrip('htp:/')
        url = 'http://' + url
    return url


####################################################################################################

@route(PREFIX + '/desitvbox/createvideoobject')
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
