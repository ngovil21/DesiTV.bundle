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
    html = HTML.ElementFromURL(url, timeout=10)

    #Log(HTML.StringFromElement(html))

    sites = html.xpath("//div[@id='serial_episodes']/h3")
    # Add the item to the collection
    for item in sites:
        type = item.xpath("./text()")[0]
        oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=type), title=type))

    # If there are no channels, warn the user
    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('PlayerWarning'))

    return oc

@route(PREFIX + '/bollystop/episodelinksmenu')
def EpisodeLinksMenu(url, title):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    items = html.xpath(".//*[@id='serial_episodes']/h3[contains(text(),'" + title + "']/following-sibling::div[1]/div//a")

    for item in items:
        try:
            # Video site
            # videosite = item.xpath("./text()")[0]
            # Video link
            link = item.xpath("./@href")[0]
            # Show date
            # date = GetShowDate(videosite)
            # Get video source url and thumb
            link = GetURLSource(link, url)
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


def GetURLSource(url, referer, date=''):
  html = HTML.ElementFromURL(url=url, headers={'Referer': referer})
  string = HTML.StringFromElement(html)

  if string.find('dailymotion') != -1:
    url = html.xpath("//iframe[contains(@src,'dailymotion')]/@src")[0]
  elif string.find('playwire') != -1:
    #Log("pID: " + str(len(html.xpath("//script/@data-publisher-id"))) + " vID: " + str(len(html.xpath("//script/@data-video-id"))))
    if len(html.xpath("//script/@data-publisher-id")) != 0 and len(html.xpath("//script/@data-video-id")) != 0:
      url = 'http://cdn.playwire.com/' + html.xpath("//script/@data-publisher-id")[0] + '/video-' + date + '-' + html.xpath("//script/@data-video-id")[0] + '.mp4'
    else:
      #Log("JSON: " + str(html.xpath("//script/@data-config")))
      json = JSON.ObjectFromURL(html.xpath("//script/@data-config")[0])
      #Log("JSON: " + str(json))
      manifest = json['src']
      #Log("Manifest: " + str(manifest))
      content = HTTP.Request(manifest, headers = {'Accept': 'text/html'}).content
      content = content.replace('\n','').replace('  ','')
      #Log("Content: " + str(content))
      baseurl = re.search(r'>http(.*?)<', content) #<([baseURL]+)\b[^>]*>(.*?)<\/baseURL>
      #Log ('BaseURL: ' + baseurl.group())
      baseurl = re.sub(r'(<|>)', "", baseurl.group())
      #Log ('BaseURL: ' + baseurl)
      mediaurl = re.search(r'url="(.*?)\?', content)
      #Log ('MediaURL: ' + mediaurl.group())
      mediaurl = re.sub(r'(url|=|\?|")', "", mediaurl.group())
      #Log ('MediaURL: ' + mediaurl)
      url = baseurl + "/" + mediaurl
      Log("URL: " + url)

  # thumb = GetThumb(html)

  # return url, thumb
  return url