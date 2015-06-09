import common
import urlparse
import Movshare

PREFIX = common.PREFIX

TEST_URL = "http://www.videoweed.es/file/9f6fdc1064762"

####################################################################################################

@route(PREFIX + '/testmenu')
def TestMenu(url):

  oc = ObjectContainer(title2="Test")

  final_url = Movshare.PlayVideo(url)

  oc.add(CreateVideoObject(
    url=final_url,
    title="Video Weed",
    thumb=None,
    originally_available_at=None))

  return oc

  #return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")

####################################################################################################


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
    key = Callback(
      CreateVideoObject,
      url=url,
      title=title,
      thumb=thumb,
      originally_available_at=originally_available_at,
      include_container=True
    ),
    rating_key = url,
    title = title,
    thumb=thumb,
    originally_available_at=originally_available_at,
    items = [
      MediaObject(
        parts = [
          PartObject(key=url)
        ],
        container = container,
        video_codec = video_codec,
        audio_codec = audio_codec,
        audio_channels = audio_channels
      )
    ]
  )

  if include_container:
    return ObjectContainer(objects=[video_object])
  else:
    return video_object