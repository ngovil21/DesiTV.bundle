import common
import urlparse
import re
import time

SITETITLE = 'Einthusan'
SITEURL = 'http://einthusan.com/'
SITETHUMB = 'icon-einthusan.png'

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON


@route(PREFIX + '/einthusan/languages')
def LanguagesMenu(url):
    oc = ObjectContainer(title2=SITETITLE)

    oc.add(DirectoryObject(key=Callback(MainMenu, url=url + 'index.php?lang=hindi', title='Hindi'), title='Hindi'))
    oc.add(DirectoryObject(key=Callback(MainMenu, url=url + 'index.php?lang=tamil', title='Tamil'), title='Tamil'))
    oc.add(DirectoryObject(key=Callback(MainMenu, url=url + 'index.php?lang=telegu', title='Telegu'), title='Telegu'))
    oc.add(DirectoryObject(key=Callback(MainMenu, url=url + 'index.php?lang=malayalam', title='Malayalam'),
                           title='Malayalam'))

    return oc


@route(PREFIX + '/einthusan/main')
def MainMenu(url, title):
    oc = ObjectContainer(title2=title)

    oc.add(DirectoryObject(key=Callback(ShowcaseMenu, url=url, title='Showcase'), title='Showcase'))
    oc.add(DirectoryObject(key=Callback(HDMenu, url=url, title='HD Movies', language=title.lower()), title='HD Movies'))
    oc.add(DirectoryObject(key=Callback(BlurayMenu, url=url, title='Blu-ray Movies', language=title.lower()),
                           title='Blu-ray Movies'))
    oc.add(InputDirectoryObject(key=Callback(SearchResultsMenu, language=title.lower()), title='Search',
                                prompt="Enter the name of the Movie to search:"))
    # oc.add(DirectoryObject(key=Callback(SearchInputMenu, title='Search', language=title), title='Search'))
    return oc


@route(PREFIX + '/einthusan/showcase')
def ShowcaseMenu(url, title):
    oc = ObjectContainer(title2=title)
    html = HTML.ElementFromURL(url)

    for item in html.xpath("//div[@id='movie-showcase-slides']/div"):
        # try:
        link = item.xpath(".//a[@class='movie-title']")[0]
        url = link.xpath("./@href")[0].lstrip(' .')
        if not url.startswith("http://"):
            url = SITEURL + url
        thumb = None
        x_image = item.xpath("//img/@src")
        if x_image:
            image = x_image[0].lstrip(" .")
            if not image.startswith("http:"):
                image = SITEURL + image
            thumb = Resource.ContentsOfURLWithFallback(url=image, fallback=R(ICON))
        title = link.xpath("./text()")[0].rstrip(' -')
        # except:
        #     continue

        oc.add(DirectoryObject(key=Callback(PlayMovie, url=url, title=title), title=title, thumb=thumb))

    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('ShowWarning'))

    return oc


@route(PREFIX + '/einthusan/HdMovies')
def HDMenu(url, title, language):
    oc = ObjectContainer(title2=title)

    url = "http://einthusan.com/movies/index.php?lang=" + language

    oc.add(DirectoryObject(key=Callback(OrganizeMenu, url=url, title="By Year", type="Year"), title="By Year"))
    oc.add(DirectoryObject(key=Callback(OrganizeMenu, url=url, title="By Alphabet", type="Alphabetically"), title="By Alphabet"))
    oc.add(DirectoryObject(key=Callback(OrganizeMenu, url=url, title="By Cast", type="Cast"), title="By Cast"))
    oc.add(DirectoryObject(key=Callback(OrganizeMenu, url=url, title="By Rating", type="Rating"), title="By Rating"))
    oc.add(DirectoryObject(key=Callback(OrganizeMenu, url=url, title="By Director", type="Director"), title="By Director"))

    return oc


@route(PREFIX + '/einthusan/BlurayMovies')
def BlurayMenu(url, title, language):
    oc = ObjectContainer(title2=title)

    url = "http://einthusan.com/bluray/index.php?lang=" + language

    oc.add(DirectoryObject(key=Callback(OrganizeMenu, url=url, title="By Year", type="Year"), title="By Year"))
    oc.add(DirectoryObject(key=Callback(OrganizeMenu, url=url, title="By Alphabet", type="Alphabetical"), title="By Alphabet"))
    oc.add(DirectoryObject(key=Callback(OrganizeMenu, url=url, title="By Cast", type="Cast"), title="By Cast"))
    oc.add(DirectoryObject(key=Callback(OrganizeMenu, url=url, title="By Rating", type="Rating"), title="By Rating"))
    oc.add(DirectoryObject(key=Callback(OrganizeMenu, url=url, title="By Director", type="Director"), title="By Director"))

    return oc


@route(PREFIX + '/einthusan/Organize')
def OrganizeMenu(url, title, type="Year"):
    oc = ObjectContainer(title2=title)
    yurl = url + "&organize=" + type

    html = HTML.ElementFromURL(yurl)

    for item in html.xpath("//div[@id='video-organizer-wrapper']/div[@class='video-organizer-element-wrapper']/a"):
        try:
            year = item.xpath("./text()")[0]
            link = item.xpath("./@href")[0].lstrip(" .")
            if not link.startswith("http://"):
                link = url + link
        except:
            continue
        oc.add(DirectoryObject(key=Callback(MovieListMenu, url=link, title=year), title=year, thumb=None))

    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('ShowWarning'))

    return oc


@route(PREFIX + '/einthusan/MovieList')
def MovieListMenu(url, title):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    for item in html.xpath("//div[@class='video-object-wrapper']"):
        x_image = item.xpath("./a//img")
        thumb = None
        if x_image:
            image = x_image[0].xpath("./@src")[0].lstrip(". ")
            if not image.startswith("http:"):
                image = SITEURL + image
            thumb = Resource.ContentsOfURLWithFallback(url=image, fallback=R(ICON))
        x_link = item.xpath(".//div[@class='movie-title-wrapper']//a")[0]
        link = x_link.xpath("./@href")[0].lstrip(" .")
        if not link.startswith("http://"):
            link = SITEURL + link
        name = x_link.xpath("./text()")[0]
        oc.add(DirectoryObject(key=Callback(PlayMovie, url=link, title=name), title=name, thumb=thumb))

    pages = html.xpath(".//div[@id='content']/div[@class='numerical-nav']/a")
    if len(pages) > 1:
        prevPage = ""
        nextPage = ""
        if "movies" in url:
            baseURL = "http://einthusan.com/movies/index.php"
        elif "bluray" in url:
            baseURL  = "http://einthusan.com/bluray/index.php"
        else:
            baseURL = SITEURL + "index.php"
        for i in range(0,len(pages)):
            p = pages[i]
            if p.xpath("./@class='numerical-nav-selected'"):
                if i > 0:
                    prevPage = pages[i-1].xpath("./@href")[0]
                    if not prevPage.startswith("http:"):
                        prevPage = baseURL + prevPage
                    oc.add(DirectoryObject(key=Callback(MovieListMenu, url=prevPage, title=title), title="Previous Page"))
                if i < (len(pages)-1):
                    nextPage = pages[i+1].xpath("./@href")[0]
                    if not nextPage.startswith("http:"):
                        nextPage = baseURL + nextPage
                    oc.add(DirectoryObject(key=Callback(MovieListMenu, url=nextPage, title=title), title="Next Page"))
                break

    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('ShowWarning'))

    return oc


@route(PREFIX + '/einthusan/searchinput')
def SearchInputMenu(title, language):
    oc = ObjectContainer(title2=title)

    oc.add(InputDirectoryObject(key=Callback(SearchResultsMenu, language=language), title=title,
                                prompt="Enter the name of the Movie to search:"))
    return oc


@route(PREFIX + '/einthusan/searchresults')
def SearchResultsMenu(language, query):
    oc = ObjectContainer(title2="Search")

    query = String.Quote(query, usePlus=True)
    url = SITEURL + "search/?search_query=" + query + "&lang=" + language.lower()
    Log(url)
    html = HTML.ElementFromURL(url)

    for item in html.xpath("//div[@id='non-realtime-search']/div[@class='search-category-wrapper-left']/div//li/a"):
        try:
            title = item.xpath("./text()")[0]
            link = item.xpath("./@href")[0].lstrip(" .")
            if not link.startswith("http:"):
                link = SITEURL + link
        except:
            continue
        oc.add(DirectoryObject(key=Callback(PlayMovie, url=link, title=title), title=title))

    if len(oc) == 0:
        return ObjectContainer(header=title, message=L('ShowWarning'))

    return oc


@route(PREFIX + '/einthusan/movie')
def PlayMovie(url, title):
    oc = ObjectContainer(title2=title)
    html = HTML.ElementFromURL(url)

    source = HTML.StringFromElement(html)

    thumb = html.xpath("//div[@class='video-object-wrapper']/a//img/@src")[0].lstrip(" .")
    if not thumb.startswith("http:"):
        thumb = SITEURL + thumb

    posted = html.xpath("//div[@class='movie-description-wrapper']/p/text()")[0]
    words = posted.split()
    date = words[1] + " " + words[2] + " " words[3]

    match = re.compile("'file': '(.+?)'").findall(source)

    if len(match) == 0:
        return ObjectContainer(header=title, message=L('ShowWarning'))

    oc.add(CreateVideoObject(match[0], title, thumb, date, False))

    return oc


@route(PREFIX + '/einthusan/createvideoobject')
def CreateVideoObject(url, title, thumb, originally_available_at=None, summary=None, include_container=False):
    try:
        originally_available_at = Datetime.ParseDate(originally_available_at).date()
    except:
        originally_available_at = None

    container = Container.MP4
    video_codec = VideoCodec.H264
    audio_codec = AudioCodec.AAC
    audio_channels = 2

    video_object = VideoClipObject(
        key=Callback(
            CreateVideoObject,
            url=url,
            title=title,
            thumb=thumb,
            originally_available_at=originally_available_at,
            include_container=True
        ),
        rating_key=url,
        title=title,
        thumb=thumb,
        originally_available_at=originally_available_at,
        items=[
            MediaObject(
                parts=[
                    PartObject(key=url)
                ],
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
