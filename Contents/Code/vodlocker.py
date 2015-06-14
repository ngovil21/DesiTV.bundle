import re, urlparse, cgi, urllib, urllib2, cookielib, urlparse, string
from BeautifulSoup import BeautifulSoup


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/534.51.22 (KHTML, like Gecko) Version/5.1.1 Safari/534.51.22'
API_URL = "http://%s/api/player.api.php?pass=undefined&file=%s&user=undefined&key=%s&codes=undefined"

def NormalizeURL(url):

	return url

def canPlay(url):
    match = re.search("(vodlocker)", url.lower())
    if match:
        return True
    return False

def MetadataObjectForURL(url):

	#Log('In MetadataObjectForURL for MovShare (' + url + ')')

    html = HTML.ElementFromURL(url)
    string = HTML.StringFromElement(html)

    image = re.compile('image: "([^"]+)"').findall(string)
    if image:
        thumb = Resource.ContentsOfURLWithFallback(url=image[0], fallback=R(ICON))

	return VideoClipObject(
		title = 'VodLocker',
		summary = 'VodLocker',
		thumb = thumb,
	)


def MediaObjectsForURL(url):

	#Log('In MediaObjectsForURL for MovShare (' + url + ')')

	return [
		MediaObject(
			parts = [PartObject(key=Callback(PlayVideo, url=url))],
		)
	]

@route("/Plugins/Sites/Movshare/PlayVideo")
def PlayVideo(url,title=None):

    html = HTML.ElementFromURL(url)
    string = HTML.StringFromElement(html)

    string.replace('|', '/')
    image = re.compile('image: "([^"]+)"').findall(string)
    file = re.compile('file: "([^"]+)"').findall(string)
    if file:
        final_url = file[0]
    if image:
        thumb = Resource.ContentsOfURLWithFallback(url=image[0], fallback=R(ICON))

    video_object = VideoClipObject(
        key=WebVideoURL(final_url),
        rating_key=file_id,
        title=title,
        thumb=thumb
    )