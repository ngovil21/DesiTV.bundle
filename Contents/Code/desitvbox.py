import common
import urlparse
import re
import time
import datetime

SITETITLE = L('DesiTvBoxTitle')
SITEURL = 'http://www.desitvbox.me/'
SITETHUMB = 'icon-desitvbox.png'

@route(PREFIX + '/desitvbox/channels')
def ChannelsMenu(url):
  oc = ObjectContainer(title2=SITETITLE)

  html = HTML.ElementFromURL(url)

  for item in html.xpath(".//*[@id='left-inside']/div/table/tbody/tr/td/strong"):
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

@route(PREFIX + '/desirulez/showsmenu')
def ShowsMenu(url, title):
  oc = ObjectContainer(title2=title)

  html = HTML.ElementFromURL(url)

  for item in html.xpath("//div[@class='forumbitBody']//div[@class='foruminfo']"):
    try:
      # Show title
      show = item.xpath("./div/div/div/h2/a/text()")[0]

      # Show link
      link = item.xpath("./div/div/div/h2/a/@href")[0]
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

def EpisodesMenu:
    return