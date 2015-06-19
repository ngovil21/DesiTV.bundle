import common
import urlparse
from Code.Hosts import Movshare

PREFIX = common.PREFIX

TEST_URL = "http://putlockers.us/Zee%20Tv%20Serial/12th-june-2015-watch-online-serial/Jodha%20Akbar.php"

####################################################################################################

@route(PREFIX + '/testmenu')
def TestMenu(url):



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

  # video = putlocker.PlayVideo(url)
  # Log(video)

  return oc

  #return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")

####################################################################################################