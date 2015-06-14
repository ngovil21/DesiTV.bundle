import common
import urlparse
import Movshare

PREFIX = common.PREFIX

TEST_URL = "http://www.videoweed.es/file/9f6fdc1064762"

####################################################################################################

@route(PREFIX + '/testmenu')
def TestMenu(url):


  html = HTML.ElementFromURL("http://www.hindistop.com/chakravartin-ashoka-samrat-2/", headers={'Referer': "http://bollystop.com/redirector.php?r=http://www.hindistop.com/chakravartin-ashoka-samrat-2/&s=646022"})
  Log(HTML.StringFromElement(html))

  oc = ObjectContainer(title2="Test")
  #
  # video = Movshare.PlayVideo(url)

  # oc.add(CreateVideoObject(
  #   url=url,
  #   title="Video Weed",
  #   thumb=None,
  #   originally_available_at=None,
  #   user_agent=USER_AGENT))
  #
  # oc.user_agent = USER_AGENT

  # oc.add(video)


  return oc

  #return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")

####################################################################################################