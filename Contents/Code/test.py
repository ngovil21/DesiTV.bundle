import common
import urlparse
import Movshare

PREFIX = common.PREFIX

TEST_URL = "http://www.videoweed.es/file/9f6fdc1064762"

####################################################################################################

@route(PREFIX + '/testmenu')
def TestMenu(url):

  oc = ObjectContainer(title2="Test")

  video = Movshare.PlayVideo(url)

  # oc.add(CreateVideoObject(
  #   url=url,
  #   title="Video Weed",
  #   thumb=None,
  #   originally_available_at=None,
  #   user_agent=USER_AGENT))
  #
  # oc.user_agent = USER_AGENT

  oc.add(video)


  return oc

  #return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")

####################################################################################################