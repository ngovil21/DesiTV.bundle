import common
import Movshare

PREFIX = common.PREFIX

TEST_URL = "http://www.videoweed.es/file/9f6fdc1064762"

####################################################################################################

@route(PREFIX + '/testmenu')
def TestMenu(url):

  return Movshare.PlayVideo(url)

  #return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")

####################################################################################################


