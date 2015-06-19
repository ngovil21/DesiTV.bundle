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

    for item in html.xpath("//div[contains(@class,'main')]//a[contains(@href,'episode')]"):
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

    items = html.xpath("//div[@id='centerblocks']/table[" + str(index) + "]/tbody/tr/td/a")
    parts=[]
    for item in items:
        link = item.xpath("@href")[0]
        code = HTML.ElementFromURL(link)
        rlink = code.xpath("//div[@id='topsource']/a/@href")[0]
        videosource, poster, host = getURLSource(rlink,link)
        parts.append(videosource)

    # Add the found item to the collection
        if host == 'dailymotion':
            # Log ('Dailymotion Link: ' + link)
            oc.add(VideoClipObject(
                url=videosource,
                title=videotitle,
                thumb=thumb
            ))
        elif host == 'playwire':
            oc.add(CreateVideoObject(
                url=videosource,
                title=videotitle,
                thumb=thumb,
                urls=parts
            ))
        elif host == 'vodlocker':
            oc.add(videosource(
                url=link,
                title=videotitle,
                thumb=thumb,
                urls=parts
            ))
        elif host == 'cloudy':
            oc.add(CreateVideoObject(
                url=videosource,
                title=videotitle,
                thumb=None,
                container='flv',
                urls=parts
            ))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('SourceWarning'))

    return oc


####################################################################################################




def getVideoHost(url):
    return


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
        site = HTTP.Request(url)
        file = re.compile('file:[ ]?"([^"]+)"').findall(site.content)
        host = 'cloudy'
        if file:
            file_id = file[0]
            #Log(file_id)
            key = re.compile('key:[ ]?"([^"]+)"').findall(site.content)[0]
            #Log(key)
            api_call = ('http://www.cloudy.ec/api/player.api.php?user=undefined&codes=1&file=%s&pass=undefined&key=%s') % (file_id, key)
            site = HTTP.Request(api_call)
            content = re.compile('url=([^&]+)&').findall(site.content)
            if content:
                url = String.Unquote(content[0])
                Log(url)
                poster = None
        else:
            return None, None, None

    # return url, thumb
    return url, host, poster


####################################################################################################

def URLCheck(url):
    url = url.rstrip('\r\n/') + '/'
    if url.startswith("http") == False:
        url = url.lstrip('htp:/')
        url = 'http://' + url
    return url


####################################################################################################

@route(PREFIX + '/apnitv/createvideoobject')
def CreateVideoObject(url, title, thumb=None, summary='', container='', originally_available_at=None,
                      include_container=False,
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
