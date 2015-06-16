import common
import urlparse
import re
import time

SITETITLE = "BollyStop"
SITEURL = 'http://bollystop.com/'
SITETHUMB = 'icon-bollystop.png'

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
        # Log(link)
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
        type = item.xpath("./text()")[0]
        index = int(item.xpath("count(./preceding-sibling::h3)") + 1)
        #Log(str(index))
        oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=type, index=index), title=type))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('PlayerWarning'))

    return oc


@route(PREFIX + '/bollystop/episodelinksmenu')
def EpisodeLinksMenu(url, title, index):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    items = html.xpath("//div[@id='serial_episodes']/h3[" + str(index) + "]/following-sibling::div[1]/div//a")
    # Log(HTML.StringFromElement(items[0]))
    parts = []
    for item in items:
        # try:
        # Video site
        videotitle = item.xpath("./text()")[0]
        #Log(videotitle)
        # Video link
        link = item.xpath("./@href")[0]
        if not link.startswith("http:"):
            link = SITEURL + link
        #Log(link)
        match = re.compile('redirector.php\?r=(.+?)&s=(.+?)').search(link)
        redirect = match.group(1)
        # Log(redirect)
        # Show date
        # date = GetShowDate(videosite)
        # Get video source url and thumb
        link, host, thumb = GetURLSource(redirect, link)
        parts.append(link)
        # except:
        #     continue

        # Add the found item to the collection
        if host == 'dailymotion':
            # Log ('Dailymotion Link: ' + link)
            oc.add(VideoClipObject(
                url=link,
                title=videotitle,
                thumb=thumb
            ))
        elif host == 'playwire':
            oc.add(CreateVideoObject(
                url=link,
                title=videotitle,
                thumb=thumb,
                urls=parts
            ))
        elif host == 'vodlocker':
            oc.add(CreateVideoObject(
                url=link,
                title=videotitle,
                thumb=thumb,
                urls=parts
            ))
        elif host == 'cloudy':
            oc.add(CreateVideoObject(
                url=link,
                title=videotitle,
                thumb=None,
                container='flv'
            ))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('SourceWarning'))

    return oc


def GetURLSource(url, referer, date=''):
    html = HTML.ElementFromURL(url=url, headers={'Referer': referer})
    string = HTML.StringFromElement(html)
    host = ''
    poster = ''
    # Log(string)
    if html.xpath("//iframe[contains(@src,'dailymotion')]"):
        url = html.xpath("//iframe[contains(@src,'dailymotion')]/@src")[0]
        host = 'dailymotion'
        thumb = None
    elif string.find('playwire') != -1:
        # Log("pID: " + str(len(html.xpath("//script/@data-publisher-id"))) + " vID: " + str(len(html.xpath("//script/@data-video-id"))))
        if len(html.xpath("//script/@data-publisher-id")) != 0 and len(html.xpath("//script/@data-video-id")) != 0:
            url = 'http://cdn.playwire.com/' + html.xpath("//script/@data-publisher-id")[0] + '/video-' + date + '-' + \
                  html.xpath("//script/@data-video-id")[0] + '.mp4'
            host = 'playwire'
        else:
            # Log("JSON: " + str(html.xpath("//script/@data-config")))
            json_obj = JSON.ObjectFromURL(html.xpath("//script/@data-config")[0])
            # Log("JSON: " + str(json_obj))
            # import json
            # Log(json.dumps(json_obj,indent=4))
            manifest = json_obj['content']['media']['f4m']
            poster = json_obj['content']['poster']
            # Log("Manifest: " + str(manifest))
            content = HTTP.Request(manifest, headers={'Accept': 'text/html'}).content
            content = content.replace('\n', '').replace('  ', '')
            # Log("Content: " + str(content))
            baseurl = re.search(r'>http(.*?)<', content)  # <([baseURL]+)\b[^>]*>(.*?)<\/baseURL>
            # Log ('BaseURL: ' + baseurl.group())
            baseurl = re.sub(r'(<|>)', "", baseurl.group())
            # Log ('BaseURL: ' + baseurl)
            mediaurl = re.search(r'url="(.*?)\?', content)
            # Log ('MediaURL: ' + mediaurl.group())
            mediaurl = re.sub(r'(url|=|\?|")', "", mediaurl.group())
            # Log ('MediaURL: ' + mediaurl)
            url = baseurl + "/" + mediaurl
            host = 'playwire'
            Log("URL: " + url)
            thumb = poster
    elif html.xpath("//iframe[contains(@src,'vodlocker')]"):
        url = html.xpath("//iframe[contains(@src,'vodlocker')]/@src")[0]
        site = HTML.ElementFromURL(url)
        source = HTML.StringFromElement(site)
        source = source.replace('|', '/')
        file = re.compile('file: "([^"]+)"').findall(source)
        image = re.compile('image: "([^"]+)"').findall(source)
        if file:
            url = file[0]
            Log(url)
            poster = image[0]
        else:
            return None,None,None
        host = 'vodlocker'
        thumb = None
    elif html.xpath("//iframe[contains(@src,'cloudy')]"):
        url = html.xpath("//iframe[contains(@src,'cloudy')]/@src")[0]
        site = HTML.ElementFromURL(url)
        source = HTML.StringFromElement(site)
        file = re.compile('file:[ ]?"([^"]+)"').findall(source)
        host = 'cloudy'
        if file:
            file_id = file[0]
            Log(file_id)
            key = re.compile('file:[ ]?"([^"]+)"').findall(source)[0]
            Log(key)
            api_call = ('http://www.cloudy.ec/api/player.api.php?user=undefined&codes=1&file=%s&pass=undefined&key=%s') % (file_id, key)
            site = HTTP.Request(api_call)
            source = site.read()
            content = re.compile('url=(.+').findall(source)
            if content:
                url = String.Unquote(content)
                Log(url)
                poster = None
        else:
            return None, None, None

    # return url, thumb
    return url, host, poster


@route(PREFIX + '/bollystop/createvideoobject')
def CreateVideoObject(url, title, thumb=None, summary='', container='', originally_available_at=None, include_container=False,
                      urls=None):
    try:
        originally_available_at = Datetime.ParseDate(originally_available_at).date()
    except:
        originally_available_at = None

    if not container:
        container = Container.MP4
    video_codec = VideoCodec.H264
    audio_codec = AudioCodec.AAC
    audio_channels = 2

    if urls:
        parts = []
        for part in urls:
            parts.append(PartObject(key=part))
    else:
        parts = [
            PartObject(key=url)
        ]

    video_object = VideoClipObject(
        key=Callback(
            CreateVideoObject,
            url=url,
            title=title,
            summary=summary,
            thumb=thumb,
            originally_available_at=originally_available_at,
            include_container=True
        ),
        rating_key=url,
        title=title,
        summary=summary,
        thumb=thumb,
        originally_available_at=originally_available_at,
        items=[
            MediaObject(
                parts=parts,
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
