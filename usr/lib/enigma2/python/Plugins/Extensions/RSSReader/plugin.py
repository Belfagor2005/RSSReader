# -*- coding: utf-8 -*-

# based on the work from Rico Schulte
# (c) 2006 Rico Schulte
# This Software is Free, use it where you want, when you want for whatever you want and modify it
# if you want but don't remove my copyright!
# adapted for py3 and added fhd screens by mrvica
# up @lululla 20240521
from Components.ActionMap import ActionMap
from Components.config import config
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText  # , MultiContentEntryPixmapAlphaTest
from Components.ScrollLabel import ScrollLabel
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, getDesktop, eTimer
from six.moves.urllib.request import urlopen, Request
from xml.dom.minidom import parse
import ssl
import os
import sys

global HALIGN
myname = 'RSS Reader'
version = '1.12'
descplugx = 'RSS Reader by Rico Schulte v.%s\n\nModd.by @lululla 20240521\n\n' % version
HALIGN = RT_HALIGN_LEFT
ssl._create_default_https_context = ssl._create_unverified_context

try:
    lng = config.osd.language.value
    lng = lng[:-3]
    if lng == 'ar':
        HALIGN = RT_HALIGN_RIGHT
except:
    lng = 'en'
    pass


def main(session, **kwargs):
    session.open(RSSFeedScreenList)


def autostart(reason, **kwargs):
    pass


def Plugins(**kwargs):
    return [PluginDescriptor(name=myname, description='RSS Simple Reader v.%s' % version, icon='rss.png', where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main), PluginDescriptor(name='RSS Reader', where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]


class RSSFeedScreenList(Screen):
    if (getDesktop(0).size().width() >= 1920):

        skin = '<screen position="0,0" size="1920,1080" title="RSS Reader">\
                    <widget name="info" position="970,45" zPosition="4" size="870,40" font="Regular;35" transparent="1" valign="center" />\
                    <ePixmap position="188,92" size="500,8" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/slider_fhd.png" alphatest="blend" />\
                    <ePixmap position="0,0" size="1920,1080" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/RSS_FEED+1.png" transparent="1" alphatest="blend" />\
                    <widget name="mylist" itemHeight="55" position="970,120" size="870,875" scrollbarMode="showOnDemand" zPosition="2" transparent="1" />\
                    <widget name="opisi" font="Regular; 34" position="61,742" size="773,281" zPosition="2" transparent="1" />\
                    <widget font="Regular; 40" halign="center" position="69,30" render="Label" size="749,70" source="global.CurrentTime" transparent="1">\
                        <convert type="ClockToText">Format:%a %d.%m. %Y | %H:%M</convert>\
                    </widget>\
                    <widget source="session.VideoPicture" render="Pig" position="77,152" zPosition="20" size="739,421" backgroundColor="transparent" transparent="0" />\
                    <eLabel name="" position="346,652" size="190,52" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" font="Regular; 17" zPosition="3" text="0 FOR LANGUAGE" />\
                </screen>'
        
    else:
        skin = '<screen position="center,center" size="920,600" title="RSS Reader">\
                    <widget name="info" position="15,10" zPosition="4" size="895,55" font="Regular;23" foregroundColor="#ffc000" valign="center" />\
                    <ePixmap position="15,65" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/slider.png" alphatest="blend" />\
                    <widget name="opisi" font="Regular; 34" position="61,742" size="773,281" zPosition="2" transparent="1" />\
                    <widget name="mylist" itemHeight="38" position="12,79" size="890,452" scrollbarMode="showOnDemand" zPosition="2" />\
                    <eLabel name="" position="710,556" size="190,35" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" font="Regular; 17" zPosition="3" text="0 FOR LANGUAGE" />\
                </screen>'

    def __init__(self, session, args=0):
        self.skin = RSSFeedScreenList.skin
        self.session = session
        Screen.__init__(self, session)
        self.menu = args
        self.config = FeedreaderConfig()
        self['mylist'] = MenuList([], True, eListboxPythonMultiContent)
        if (getDesktop(0).size().width() >= 1920):
            self['mylist'].l.setItemHeight(57)
            self['mylist'].l.setFont(0, gFont('Regular', 30))
        else:
            self['mylist'].l.setItemHeight(38)
            self['mylist'].l.setFont(0, gFont('Regular', 23))
        self['info'] = Label('RSS Feeds')
        self['opisi'] = Label(descplugx)
        self['actions'] = ActionMap(['WizardActions', 'InputActions',  'DirectionActions'], {'ok': self.go, '0': self.arabic, 'back': self.close}, -1)
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.getFeedList)
        else:
            self.timer.callback.append(self.getFeedList)
        self.timer.start(200, True)
        self.onClose.append(self.cleanup)

    def arabic(self):
        global HALIGN
        if HALIGN == RT_HALIGN_LEFT:
            HALIGN = RT_HALIGN_RIGHT
        elif HALIGN == RT_HALIGN_RIGHT:
            HALIGN = RT_HALIGN_LEFT
        self.getFeedList()

    def cleanup(self):
        if self.config:
            self.config.cleanup()

    def go(self):
        try:
            i = 1
            i = self['mylist'].getSelectedIndex()
            feed = self.feedlist[i][1]
            if feed:
                self.showFeed(feed)
            else:
                print(('[' + myname + '] section in config not found'))
        except:
            self['info'].setText('sorry, no feeds available, try later')

    def showFeed(self, feed):
        try:
            self.session.open(RSSFeedScreenContent, feed)
        except IOError as e:
            print(e)
            self['info'].setText('loading feeddata failed!')
        except:
            print('no feed data')
            self['info'].setText('sorry feeds not available')

    def getFeedList(self):
        list = []
        feedlist = []
        try:
            for feed in self.config.getFeeds():
                res = []
                feedname = feed.getName()
                fedname = 'default'
                try:
                    a = []
                    a = feedname.split('-')
                    fedname = a[0]
                    fedname = fedname.strip()
                    fedname = fedname.lower()
                except:
                    fedname = 'default'

                if (getDesktop(0).size().width() >= 1920):
                    res.append(MultiContentEntryText(pos=(0, 8), size=(8, 15), font=0, flags=HALIGN, text='', color=0x98fb98, color_sel=0x98fb98))
                    res.append(MultiContentEntryText(pos=(15, 8), size=(822, 90), font=0, flags=HALIGN, text=feedname, color=0xffffff, color_sel=0x00fffc00))
                else:
                    res.append(MultiContentEntryText(pos=(0, 5), size=(5, 10), font=0, flags=HALIGN, text='', color=0x98fb98, color_sel=0x98fb98))
                    res.append(MultiContentEntryText(pos=(10, 5), size=(850, 60), font=0, flags=HALIGN, text=feedname, color=0xffffff, color_sel=0x00fffc00))

                feedlist.append((feed.getName(), feed))
                list.append(res)
                res = []

            self.feedlist = feedlist
            self['mylist'].l.setList(list)
            self['mylist'].show()
        except:
            self['info'].setText('error in parsing feed xml')


class FeedreaderConfig:
    configfile = '/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/feeds.xml'

    def __init__(self):
        self.node = None
        self.feeds = []
        self.readConfig()
        return

    def cleanup(self):
        if self.node:
            self.node.unlink()
            del self.node
            self.node = None
            self.feeds = []
        return

    def readConfig(self):
        self.cleanup()
        try:
            self.node = parse(self.configfile)
        except:
            print('Illegal xml file')
            print((self.configfile))
            return
        self.node = self.node.documentElement
        self.getFeeds()

    def getFeeds(self):
        if self.feeds:
            return self.feeds
        for node in self.node.getElementsByTagName('feed'):
            name = ''
            description = ''
            url = ''
            nodes = node.getElementsByTagName('name')
            if nodes and nodes[0].childNodes:
                name = str(nodes[0].childNodes[0].data)
            nodes = node.getElementsByTagName('description')
            if nodes and nodes[0].childNodes:
                description = str(nodes[0].childNodes[0].data)
            nodes = node.getElementsByTagName('url')
            if nodes and nodes[0].childNodes:
                url = str(nodes[0].childNodes[0].data)
            self.feeds.append(Feed(name, description, url, True))
        return self.feeds

    def isFeed(self, feedname):
        for feed in self.feeds:
            if feed.getName() == feedname:
                return True
        return False

    def getFeedByName(self, feedname):
        for feed in self.feeds:
            if feed.getName() == feedname:
                return feed
        return None


class Feed:
    isfavorite = False

    def __init__(self, name, description, url, isfavorite=False):
        self.name = name
        self.description = description
        self.url = url
        self.isfavorite = isfavorite

    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def getURL(self):
        self.url = self.url.replace('zz', '&')
        return self.url

    def setName(self, name):
        self.name = name

    def setDescription(self, description):
        self.description = description

    def setURL(self, url):
        self.url = url

    def setFavorite(self):
        self.isfavorite = True

    def isFavorite(self):
        return self.isfavorite


class RSSFeedScreenContent(Screen):
    if (getDesktop(0).size().width() >= 1920):
        skin = '<screen position="0,0" size="1920,1080" title="RSS Reader">\
                    <widget name="info" position="970,45" zPosition="4" size="870,40" font="Regular;35" transparent="1" valign="center" />\
                    <ePixmap position="188,92" size="500,8" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/slider_fhd.png" alphatest="blend" />\
                    <ePixmap position="0,0" size="1920,1080" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/RSS_FEED+1.png" transparent="1" alphatest="blend" />\
                    <widget name="mylist" itemHeight="55" position="970,120" size="870,875" scrollbarMode="showOnDemand" zPosition="2" transparent="1" />\
                    <!-- <widget name="opisi" font="Regular; 34" position="61,742" size="773,281" zPosition="2" transparent="1" /> -->\
                    <widget font="Regular; 40" halign="center" position="69,30" render="Label" size="749,70" source="global.CurrentTime" transparent="1">\
                        <convert type="ClockToText">Format:%a %d.%m. %Y | %H:%M</convert>\
                    </widget>\
                    <widget source="session.VideoPicture" render="Pig" position="77,152" zPosition="20" size="739,421" backgroundColor="transparent" transparent="0" />\
                    <eLabel name="" position="346,652" size="190,52" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" font="Regular; 17" zPosition="3" text="0 FOR LANGUAGE" />\
                </screen>'

    else:
        skin = '<screen position="center,center" size="920,600" title="RSS Reader">\
                    <widget name="info" position="18,20" zPosition="4" size="557,30" font="Regular;23" foregroundColor="#ffc000" valign="center" />\
                    <ePixmap position="15,65" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/slider.png" alphatest="blend" />\
                    <widget name="mylist" itemHeight="39" position="20,84" size="880,464" scrollbarMode="showOnDemand" zPosition="2" />\
                    <!-- <widget name="opisi" font="Regular; 34" position="61,742" size="773,281" zPosition="2" transparent="1" /> -->\
                    <widget font="Regular; 24" halign="center" position="646,11" render="Label" size="254,38" source="global.CurrentTime" transparent="1">\
                        <convert type="ClockToText">Format:%a %d.%m. %Y | %H:%M</convert>\
                    </widget>\
                    <eLabel name="" position="351,561" size="190,30" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" font="Regular; 17" zPosition="3" text="0 FOR LANGUAGE" />\
                </screen>'

    def __init__(self, session, args=0):
        self.feed = args
        self.skin = RSSFeedScreenContent.skin
        self.session = session
        Screen.__init__(self, session)
        self.feedname = self.feed.getName()
        self['info'] = Label()
        self['mylist'] = MenuList([], True, eListboxPythonMultiContent)
        if (getDesktop(0).size().width() >= 1920):
            self['mylist'].l.setItemHeight(57)
            self['mylist'].l.setFont(0, gFont('Regular', 30))
        else:
            self['mylist'].l.setItemHeight(38)
            self['mylist'].l.setFont(0, gFont('Regular', 23))
        self.menu = args
        self['actions'] = ActionMap(['WizardActions', 'InputActions', 'DirectionActions'], {'ok': self.go, '0': self.arabic, 'back': self.close}, -1)
        self['info'].setText('Loading feed titles')
        # self['opisi'].setText(descplugx)
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.filllist)
        else:
            self.timer.callback.append(self.filllist)
        self.timer.start(200, True)

    def arabic(self):
        global HALIGN
        if HALIGN == RT_HALIGN_LEFT:
            HALIGN = RT_HALIGN_RIGHT
        elif HALIGN == RT_HALIGN_RIGHT:
            HALIGN = RT_HALIGN_LEFT
        self.filllist()

    def filllist(self):
        list = []
        self.itemlist = []
        newlist = []
        itemnr = 0
        for item in self.getFeedContent(self.feed):
            list.append((item['title'], itemnr))
            self.itemlist.append(item)
            itemnr += 1
            res = []
            if (getDesktop(0).size().width() >= 1920):
                res.append(MultiContentEntryText(pos=(0, 8), size=(8, 45), font=0, flags=HALIGN, text='', color=0xffffff, color_sel=0xffffff))
                res.append(MultiContentEntryText(pos=(8, 8), size=(822, 45), font=0, flags=HALIGN, text=item['title'], color=0xffffff, color_sel=0x00fffc00))
            else:
                res.append(MultiContentEntryText(pos=(0, 5), size=(5, 30), font=0, flags=HALIGN, text='', color=0xffffff, color_sel=0xffffff))
                res.append(MultiContentEntryText(pos=(5, 5), size=(850, 30), font=0, flags=HALIGN, text=item['title'], color=0xffffff, color_sel=0x00fffc00))
            newlist.append(res)
            res = []

        self['info'].setText(self.feedname)
        if len(self.itemlist) == 0:
            self['info'].setText('sorry no feeds available')
        else:
            self['mylist'].l.setList(newlist)
            self['mylist'].show()

    def getFeedContent(self, feed):
        print(('[' + myname + "] reading feedurl '%s' ..." % feed.getURL()))
        try:
            self.rss = RSS()
            self.feedc = self.rss.getList(feed.getURL())
            print(('[' + myname + '] have got %i items in newsfeed ' % len(self.feedc)))
            return self.feedc
        except IOError:
            print(('[' + myname + '] IOError by loading the feed! feed adress correct?'))
            self['info'].setText('IOError by loading the feed! feed adress correct')
            return []
        except:
            self['info'].setText('loading feeddata failed!')
            return []

    def go(self):
        i = self['mylist'].getSelectedIndex()
        self.currentindex = i
        selection = self['mylist'].l.getCurrentSelection()
        if selection is not None:
            item = self.itemlist[i]
            if item['type'].startswith('folder') is True:
                newitem = Feed(item['title'], item['desc'], item['link'])
                self.session.open(RSSFeedScreenContent, newitem)
            elif item['type'].startswith('pubfeed') is True:
                newitem = Feed(item['title'], item['desc'], item['link'])
                self.session.open(RSSFeedScreenContent, newitem)
            else:
                try:
                    self.session.open(RSSFeedScreenItemviewer, [self.feed, item, self.currentindex, self.itemlist])
                except AssertionError:
                    self.session.open(MessageBox, 'Error processing feeds', MessageBox.TYPE_ERROR)
        return


class RSSFeedScreenItemviewer(Screen):
    skin = ''

    def __init__(self, session, args=0):
        self.feed = args[0]
        self.item = args[1]
        self.currentindex = args[2]
        self.itemlist = args[3]

        if (getDesktop(0).size().width() >= 1920):
            self.skin = '<screen name="RSSFeedScreenItemviewer" position="center,68" size="1380,930" title="%s" flags="wfNoBorder">\
                            <widget name="titel" position="28,24" zPosition="1" size="1318,126" font="Regular;35" foregroundColor="#ffc000" />\
                            <widget name="leagueNumberWidget" position="27,817" size="1335,53" halign="center" font="Regular;30" transparent="1" zPosition="4" />\
                            <ePixmap position="23,162" size="1335,8" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/slider_fhd.png" alphatest="blend" />\
                            <widget name="text" position="30,180" size="1319,627" halign="block" font="Regular;34" />\
                            <ePixmap position="23,810" size="1335,8" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/slider_fhd.png" alphatest="blend" />\
                            <widget name="feedtitel" position="27,867" zPosition="1" size="1335,45" halign="center" font="Regular;34" foregroundColor="#ffc000" />\
                        </screen>' % self.feed.getName()

        else:
            self.skin = '<screen name="RSSFeedScreenItemviewer" position="center,45" size="920,620" title="%s" flags="wfNoBorder">\
                            <widget name="titel" position="20,16" zPosition="1" size="810,84" font="Regular;23" foregroundColor="#ffc000" />\
                            <widget name="leagueNumberWidget" position="308,542" size="300,35" halign="center" font="Regular;20" />\
                            <ePixmap position="15,108" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/slider.png" alphatest="blend" />\
                            <widget name="text" position="20,120" size="880,418" halign="block" font="Regular;23" />\
                            <ePixmap position="15,540" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/slider.png" alphatest="blend" />\
                            <widget name="feedtitel" position="14,577" zPosition="1" size="890,30" halign="center" font="Regular;23" foregroundColor="#ffc000" />\
                        </screen>' % self.feed.getName()

        Screen.__init__(self, session)
        self.itemscount = len(self.itemlist)
        self['leagueNumberWidget'] = Label(str(self.currentindex + 1) + '/' + str(self.itemscount))
        self['titel'] = Label(str(self.item['title']))
        self['feedtitel'] = Label(self.feed.getName())
        self['text'] = ScrollLabel(str(self.item['desc']) + '\n\n' + str(self.item['date']))
        self['actions'] = ActionMap(['DirectionActions', 'WizardActions'],
                                    {
                                    'left': self.previousitem,
                                    'right': self.nextitem,
                                    'up': self['text'].pageUp,
                                    'down': self['text'].pageDown,
                                    'ok': self.close,
                                    'back': self.close
                                    }, -1)

    def gofill(self):
        i = self.currentindex
        selection = self.itemlist
        if selection is not None:
            item = self.itemlist[i]
            self.item = item
            self.filllist()
        return

    def filllist(self):
        self.itemscount = len(self.itemlist)
        self['leagueNumberWidget'].setText(str(self.currentindex + 1) + '/' + str(self.itemscount))
        self['titel'].setText(str(self.item['title']))
        self['text'].setText(str(self.item['desc']) + '\n\n' + str(self.item['date']))

    def nextitem(self):
        currentindex = int(self.currentindex) + 1
        if currentindex == self.itemscount:
            currentindex = 0
        self.currentindex = currentindex
        self.gofill()

    def previousitem(self):
        currentindex = int(self.currentindex) - 1
        if currentindex < 0:
            currentindex = self.itemscount - 1
        self.currentindex = currentindex
        self.gofill()


class RSS:
    DEFAULT_NAMESPACES = (None, 'http://purl.org/rss/1.0/', 'http://my.netscape.com/rdf/simple/0.9/')
    DUBLIN_CORE = ('http://purl.org/dc/elements/1.1/',)

    def getElementsByTagName(self, node, tagName, possibleNamespaces=DEFAULT_NAMESPACES):
        for namespace in possibleNamespaces:
            children = node.getElementsByTagNameNS(namespace, tagName)
            if len(children):
                return children
        return []

    def node_data(self, node, tagName, possibleNamespaces=DEFAULT_NAMESPACES):
        children = self.getElementsByTagName(node, tagName, possibleNamespaces)
        node = len(children) and children[0] or None
        return node and "".join([child.data for child in node.childNodes]) or None

    def get_txt(self, node, tagName, default_txt=''):
        """
        Liefert den Inhalt >tagName< des >node< zurueck, ist dieser nicht vorhanden, wird >default_txt< zurueck gegeben.
        """
        return self.node_data(node, tagName) or self.node_data(node, tagName, self.DUBLIN_CORE) or default_txt

    def getList(self, url):
        header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36", 'referer': 'https://www.google.com/'}
        req = Request(url, headers=header)
        rssDocument = parse(urlopen(req))
        channelname = self.get_txt(rssDocument, 'title', 'no channelname')
        data = []
        for node in self.getElementsByTagName(rssDocument, 'item'):
            nodex = {}
            nodex['channel'] = channelname
            nodex['type'] = self.get_txt(node, 'type', 'feed')
            nodex['link'] = self.get_txt(node, 'link', '')
            nodex['title'] = self.clearTags(self.get_txt(node, 'title', '<no title>'))
            nodex['date'] = self.get_txt(node, 'pubDate', self.get_txt(node, 'date', ''))
            nodex['desc'] = self.clearTags(self.get_txt(node, 'description', ''))
            data.append(nodex)
        return data

    def clearTags(self, text):
        charlist = []
        charlist.append(('&#224;', '\xc3\xa0'))
        charlist.append(('&agrave;', '\xc3\xa0'))
        charlist.append(('&#225;', '\xc3\xa1'))
        charlist.append(('&aacute;', '\xc3\xa1'))
        charlist.append(('&#226;', '\xc3\xa2'))
        charlist.append(('&acirc;', '\xc3\xa2'))
        charlist.append(('&#228;', '\xc3\xa4'))
        charlist.append(('&auml;', '\xc3\xa4'))
        charlist.append(('&#249;', '\xc3\xb9'))
        charlist.append(('&ugrave;', '\xc3\xb9'))
        charlist.append(('&#250;', '\xc3\xba'))
        charlist.append(('&uacute;', '\xc3\xba'))
        charlist.append(('&#251;', '\xc3\xbb'))
        charlist.append(('&ucirc;', '\xc3\xbb'))
        charlist.append(('&#252;', '\xc3\xbc'))
        charlist.append(('&uuml;', '\xc3\xbc'))
        charlist.append(('&#242;', '\xc3\xb2'))
        charlist.append(('&ograve;', '\xc3\xb2'))
        charlist.append(('&#243;', '\xc3\xb3'))
        charlist.append(('&oacute;', '\xc3\xb3'))
        charlist.append(('&#244;', '\xc3\xb4'))
        charlist.append(('&ocirc;', '\xc3\xb4'))
        charlist.append(('&#246;', '\xc3\xb6'))
        charlist.append(('&ouml;', '\xc3\xb6'))
        charlist.append(('&#236;', '\xc3\xac'))
        charlist.append(('&igrave;', '\xc3\xac'))
        charlist.append(('&#237;', '\xc3\xad'))
        charlist.append(('&iacute;', '\xc3\xad'))
        charlist.append(('&#238;', '\xc3\xae'))
        charlist.append(('&icirc;', '\xc3\xae'))
        charlist.append(('&#239;', '\xc3\xaf'))
        charlist.append(('&iuml;', '\xc3\xaf'))
        charlist.append(('&#232;', '\xc3\xa8'))
        charlist.append(('&egrave;', '\xc3\xa8'))
        charlist.append(('&#233;', '\xc3\xa9'))
        charlist.append(('&eacute;', '\xc3\xa9'))
        charlist.append(('&#234;', '\xc3\xaa'))
        charlist.append(('&ecirc;', '\xc3\xaa'))
        charlist.append(('&#235;', '\xc3\xab'))
        charlist.append(('&euml;', '\xc3\xab'))
        charlist.append(('&#192;', '\xc3\x80'))
        charlist.append(('&Agrave;', '\xc3\x80'))
        charlist.append(('&#193;', '\xc3\x81'))
        charlist.append(('&Aacute;', '\xc3\x81'))
        charlist.append(('&#194;', '\xc3\x82'))
        charlist.append(('&Acirc;', '\xc3\x82'))
        charlist.append(('&#196;', '\xc3\x84'))
        charlist.append(('&Auml;', '\xc3\x84'))
        charlist.append(('&#217;', '\xc3\x99'))
        charlist.append(('&Ugrave;', '\xc3\x99'))
        charlist.append(('&#218;', '\xc3\x9a'))
        charlist.append(('&Uacute;', '\xc3\x9a'))
        charlist.append(('&#219;', '\xc3\x9b'))
        charlist.append(('&Ucirc;', '\xc3\x9b'))
        charlist.append(('&#220;', '\xc3\x9c'))
        charlist.append(('&Uuml;', '\xc3\x9c'))
        charlist.append(('&#210;', '\xc3\x92'))
        charlist.append(('&Ograve;', '\xc3\x92'))
        charlist.append(('&#211;', '\xc3\x93'))
        charlist.append(('&Oacute;', '\xc3\x93'))
        charlist.append(('&#212;', '\xc3\x94'))
        charlist.append(('&Ocirc;', '\xc3\x94'))
        charlist.append(('&#214;', '\xc3\x96'))
        charlist.append(('&Ouml;', '\xc3\x96'))
        charlist.append(('&#204;', '\xc3\x8c'))
        charlist.append(('&Igrave;', '\xc3\x8c'))
        charlist.append(('&#205;', '\xc3\x8d'))
        charlist.append(('&Iacute;', '\xc3\x8d'))
        charlist.append(('&#206;', '\xc3\x8e'))
        charlist.append(('&Icirc;', '\xc3\x8e'))
        charlist.append(('&#207;', '\xc3\x8f'))
        charlist.append(('&Iuml;', '\xc3\x8f'))
        charlist.append(('&#223;', '\xc3\x9f'))
        charlist.append(('&szlig;', '\xc3\x9f'))
        charlist.append(('&#038;', '&'))
        charlist.append(('&#38;', '&'))
        charlist.append(('&#8230;', '...'))
        charlist.append(('&#8211;', '-'))
        charlist.append(('&#160;', ' '))
        charlist.append(('&#039;', "'"))
        charlist.append(('&#39;', "'"))
        charlist.append(('&#60;', ' '))
        charlist.append(('&#62;', ' '))
        charlist.append(('&lt;', '<'))
        charlist.append(('&gt;', '>'))
        charlist.append(('&nbsp;', ' '))
        charlist.append(('&amp;', '&'))
        charlist.append(('&quot;', '"'))
        charlist.append(('&apos;', "'"))
        charlist.append(('&#8216;', "'"))
        charlist.append(('&#8217;', "'"))
        charlist.append(('&8221;', '\xe2\x80\x9d'))
        charlist.append(('&8482;', '\xe2\x84\xa2'))
        charlist.append(('&#8203;', ''))
        charlist.append(('&#8212;', ''))
        charlist.append(('&#8222;', ''))
        charlist.append(('&#8220;', ''))
        charlist.append(('&raquo;', '"'))
        charlist.append(('&laquo;', '"'))
        charlist.append(('&bdquo;', '"'))
        charlist.append(('&ldquo;', '"'))
        for repl in charlist:
            text = text.replace(repl[0], repl[1])

        from re import sub as re_sub
        text = re_sub('<[^>]+>', '', text)
        return str(text)  # str needed for PLi
