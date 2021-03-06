import re, urlparse, cgi, urllib, urllib2, cookielib, urlparse, string
from BeautifulSoup import BeautifulSoup


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/534.51.22 (KHTML, like Gecko) Version/5.1.1 Safari/534.51.22'
API_URL = "http://%s/api/player.api.php?pass=undefined&file=%s&user=undefined&key=%s&codes=undefined"

def NormalizeURL(url):

	return url

def canPlay(url):
    match = re.search("(movshare|novamov|nowvideo|divxstage|videoweed)", url.lower())
    if match:
        return True
    return False
		
def MetadataObjectForURL(url):
 
	#Log('In MetadataObjectForURL for MovShare (' + url + ')')
	
	return VideoClipObject(
		title = 'MovShare Redirect Page',
		summary = 'MovShare Redirect Page',
		thumb = None,
	)

def MediaObjectsForURL(url):

	#Log('In MediaObjectsForURL for MovShare (' + url + ')')
	
	return [
		MediaObject(
			parts = [PartObject(key=Callback(PlayVideo, url=url))],
		)
	]

def GetVideoURL(url):
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

	# Request Initial Provider page.
	try:
		# Log('Requesting ' + url)
		request = urllib2.Request(url)
		request.add_header('User-agent', USER_AGENT)
		response = opener.open(request)

		# Read in location and content of MovShare page.
		soup = BeautifulSoup(response.read())

		provider_url = response.geturl()
	# Log(provider_url)

	except Exception as ex:
		return LogProviderError("Error whilst retrieving initial provider page (" + url + ")", ex)



	# See if we have a form to submit before video page...
	form = soup.find('form', {'id': 'watch'})

	if (form is not None):

		# Submit the form to be taken to video page.
		try:
			# Get params to submit form with.
			params = {}
			for elem in form.findAll('input', {'type': 'hidden'}):
				params[elem['name']] = elem['value']

			# Log("Params: " + str(params))
			# Log('Requesting ' + provider_url)

			# Post to form
			request = urllib2.Request(provider_url)
			request.add_header('User-agent', USER_AGENT)
			request.add_data(urllib.urlencode(params))
			response = opener.open(request)

			soup = BeautifulSoup(response.read())

		except Exception as ex:
			return LogProviderError(
				"Error whilst trying to navigate from initial provider page to video page (" + url + ")", ex)


	# Read in API Key info and file ID from video page.
	try:

		contents = str(soup.contents)

		# Decode any WISE encoded script elements.
		contents = wise_process(contents)

		# Decode any PACKED encoded script elements.
		contents = packed_process(contents)

		# Log(contents)

		api_key = re.search("flashvars\.filekey=\"?(.*?)\"?;", contents).group(1)

		# If key is not in right format, look for a matching var...
		api_key_re = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-[a-z0-9]{32}");

		while (api_key and api_key_re.match(api_key) is None):
			api_key = re.search("var.{1,10}" + api_key + "=\"?(.*?)\"?;", contents, re.DOTALL).group(1)

		# Log("API KEY:" + api_key)

		file_id = re.search("flashvars\.file=\"?(.*?)\"?;", contents).group(1)
	# Log("File ID:" + file_id)

	except Exception as ex:
		raise ex
		return LogProviderError("Error whilst retrieving API Key and File ID. Provider may have changed page layout.",
								ex)

	# Get final video location from API.
	try:

		# Build up and retrieve API URL
		api_url = API_URL % (
			urlparse.urlparse(provider_url).netloc,
			file_id,
			urllib.quote_plus(api_key)
		)

		# Log('Requesting ' + api_url)
		request = urllib2.Request(api_url)
		request.add_header('User-agent', USER_AGENT)
		response = opener.open(request)

		content = response.read()
		# Log(content)

		# API should be HTML form encoded query string. Break it down to get elem we're
		# interested in.
		api_info = cgi.parse_qs(content)
		# api_info = urllib.parse.parse_qs(content)
		final_url = api_info['url'][0]

	except Exception as ex:
		return LogProviderError("Error whilst retrieving final url from API page.", ex)

	return final_url, file_id

@route("/Plugins/Sites/Movshare/PlayVideo")
def PlayVideo(url,title=None):

	final_url, file_id = GetVideoURL(url)
	
	video_object = VideoClipObject(
        key=WebVideoURL(final_url),
        rating_key = file_id,
        title = title
	)

	# Might as well set a sensible user agent string.
	#oc.user_agent = USER_AGENT
	
	return video_object


###############################################################################
# Util methods
###############################################################################
def LogProviderError(msg="", ex=None):

	Log("************************** PROVIDER ERROR: " + msg)
	raise Exception(msg)
	return []


###############################################################################
# Decode WISE Methods
# Borrowed from:
# http://pastebin.com/K46TdpiA
# http://www.xbmchub.com/forums/urlresolver/14156-wise-unpacker-python-port.html
###############################################################################
def unwise1(w):

	int1 = 0
	result = ""
	while int1 < len(w):
		result = result + chr(int(w[int1:int1 + 2], 36))
		int1 += 2
	return result
  
def unwise(w, i, s, e):

	int1 = 0
	int2 = 0
	int3 = 0
	int4 = 0
	string1 = ""
	string2 = ""
	while True:
		if w != "":
			if int1 < 5:
				string2 = string2 + w[int1:int1+1]
			elif int1 < len(w):
				string1 = string1 + w[int1:int1+1]
			int1 += 1
		if i != "":
			if int2 < 5:
				string2 = string2 + i[int2:int2+1]
			elif int2 < len(i):
				string1 = string1 + i[int2:int2+1]
			int2 += 1
		if s != "":
			if int3 < 5:
				string2 = string2 + s[int3:int3+1]
			elif int3 < len(s):
				string1 = string1 + s[int3:int3+1]
			int3 = int3 + 1
		if e != "":
			if int4 < 5:
				string2 = string2 + e[int4:int4+1]
			elif int4 < len(e):
				string1 = string1 + e[int4:int4+1]
			int4 = int4 + 1
		if len(w) + len(i) + len(s) + len(e) == len(string1) + len(string2):
			break
	int1 = 0
	int2 = 0
	result = ""
	while int1 < len(string1):
		flag = -1
		if ord(string2[int2:int2+1]) % 2:
			flag = 1
		result = result + chr(int(string1[int1:int1+2], 36) - flag)
		int2 += 1
		if int2 >= len(string2):
			int2 = 0
		int1 += 2
	return result
	
def wise_process(result):

	while True:
		a = re.compile(r'eval\s*\(\s*function\s*\(\s*w\s*,\s*i\s*,\s*s\s*,\s*e\s*\).+?[\"\']\s*\)\s*\)').search(result)
		if not a:
			break
		a = a.group()
		tmp = re.compile(r'\}\s*\(\s*[\"\'](\w*)[\"\']\s*,\s*[\"\'](\w*)[\"\']\s*,\s*[\"\'](\w*)[\"\']\s*,\s*[\"\'](\w*)[\"\']').search(a)
		if not tmp:
			print("UNWISE ERROR --- " + a)
			result = result.replace(a, "")
		else:
			wise = ["", "", "", ""]
			wise = tmp.groups()
			if a.find("while") == -1:
				result = result.replace(a, unwise1(wise[0]))
			else:
				c = 0
				wisetmp = ["", "", "", ""]
				b = re.compile(r'eval\s*\(\s*function\s*\(\s*w\s*,\s*i\s*,\s*s\s*,\s*e\s*\)(.*?)while').search(a).group(1)
				for d in re.compile(r'var\s+\w+\s*=\s*0').findall(b):
					wisetmp[c] = wise[c]
					c += 1
				result = result.replace(a, unwise(wisetmp[0], wisetmp[1], wisetmp[2], wisetmp[3]))
	
	return result
 
###############################################################################
# Decode PACKED Methods
###############################################################################
def unpack(matchObject):

	script = matchObject.group(0)
	
	if script is None:
		return
	
	#Log(script)
	
	# Look for substitution values.
	args_re_res = re.search("return p}\('(.*)',(\d{1,2}),(\d{1,3}),'([^']*)'.split", script)
	
	if (args_re_res is None or args_re_res.group(1) is None):
		return None
	
	val_to_unpack = args_re_res.group(1)
	key_digits_length = int(args_re_res.group(2))
	sub_vals_count = int(args_re_res.group(3))
	sub_vals = args_re_res.group(4).split('|')
	
	#Log(val_to_unpack)
	#Log(key_digits_length)
	#Log(sub_vals_count)
	#Log(sub_vals)
	
	# Create dict to map url sub keys to sub values.
	sub_vals_dict = dict()
	
	# Create list of valid digits for sub keys.
	key_digits = string.digits + string.ascii_lowercase + string.ascii_uppercase[0:key_digits_length]
	
	for index_cnt in range(0, (sub_vals_count / key_digits_length) + 1):
	
		index = index_cnt * key_digits_length
		strindex = str(index_cnt) if index_cnt > 0 else ""
		
		for cnt in range(0, key_digits_length):
			if (cnt + index < len(sub_vals) and sub_vals[cnt + index]):
				sub_vals_dict[strindex + key_digits[cnt]] = sub_vals[cnt + index]
			else:
				sub_vals_dict[strindex + key_digits[cnt]] = strindex + key_digits[cnt]
				
			#Log(strindex + key_digits[cnt] + '=' + str(cnt + index) + '=' + sub_vals_dict[strindex + key_digits[cnt]])
		
	# Sub values into string to unpack
	return (
		re.sub(
			"[0-9a-zA-Z]{1,2}",
			lambda x:  sub_vals_dict[x.group(0)],
			val_to_unpack
		)
	)
	
def packed_process(contents):

	# Look for any script element which contain a packed method.
	regEx = re.compile("eval\(function\(p,a,c,k,e,d\).*?\.split\(\'\|\'\).*?\)\)", flags=re.DOTALL)
	return regEx.sub(unpack, contents)