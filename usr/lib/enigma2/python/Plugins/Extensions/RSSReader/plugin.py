# -*- coding: utf-8 -*-

# based on the work from Rico Schulte
# (c) 2006 Rico Schulte
# This Software is Free, use it where you want, when you want for whatever you want and modify it
# if you want but don't remove my copyright!
# adapted for py3 and added fhd screens by mrvica
# up @lululla 20240521
from . import _, Utils
from .Console import Console as xConsole

from Components.ActionMap import ActionMap
from Components.config import config
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.ScrollLabel import ScrollLabel
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from enigma import (
    eListboxPythonMultiContent,
    gFont,
    RT_HALIGN_LEFT,
    RT_HALIGN_RIGHT,
    getDesktop,
    eTimer,
)
from six.moves.urllib.request import (urlopen, Request)
from xml.dom.minidom import parse
import ssl
import os
import json
import sys
from datetime import datetime

global HALIGN

myname = 'RSS Reader'
currversion = '1.13'
descplugx = 'RSS Reader by Rico Schulte v.%s\n\nModd.by @lululla 20240521\n\n' % currversion
HALIGN = RT_HALIGN_LEFT
ssl._create_default_https_context = ssl._create_unverified_context
installer_url = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0JlbGZhZ29yMjAwNS9SU1NSZWFkZXIvbWFpbi9pbnN0YWxsZXIuc2g='
developer_url = 'aHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy9CZWxmYWdvcjIwMDUvUlNTUmVhZGVy'
PY3 = False
PY3 = sys.version_info.major >= 3

if PY3:
    PY3 = True
    unidecode = str
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
    return [PluginDescriptor(name=myname, description='RSS Simple Reader v.%s' % currversion, icon='rss.png', where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main), PluginDescriptor(name='RSS Reader', where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]


class RSSFeedScreenList(Screen):
    if (getDesktop(0).size().width() >= 1920):

        skin = '<screen position="center,center" size="1920,1080" title="RSS Reader">\
                    <widget name="info" position="970,45" zPosition="4" size="870,40" font="Regular;35" transparent="1" valign="center" />\
                    <ePixmap position="188,92" size="500,8" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/slider_fhd.png" alphatest="blend" />\
                    <ePixmap position="0,0" size="1920,1080" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/RSSReader/images/RSS_FEED+1.png" transparent="1" alphatest="blend" />\
                    <widget name="mylist" itemHeight="55" position="970,120" size="870,875" scrollbarMode="showOnDemand" zPosition="2" transparent="1" />\
                    <eLabel backgroundColor="yellow" position="1542,1064" size="300,6" zPosition="10" />\
                    <widget source="key_yellow" render="Label" position="1542,1016" size="300,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="background" transparent="1" foregroundColor="white" />\
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
                    <widget name="opisi" font="Regular; 34" position="14,416" size="887,139" zPosition="2" transparent="1" />\
                    <eLabel backgroundColor="yellow" position="389,593" size="250,6" zPosition="10" />\
                    <widget source="key_yellow" render="Label" position="389,548" size="250,45" zPosition="11" font="Regular; 24" valign="center" halign="center" backgroundColor="background" transparent="1" foregroundColor="white" />\
                    <widget name="mylist" itemHeight="38" position="12,79" size="890,333" scrollbarMode="showOnDemand" zPosition="2" />\
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
        self['key_yellow'] = Label(_('Update'))
        self['opisi'] = Label(descplugx)
        self.Update = False
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'DirectionActions',
                                     'HotkeyActions',
                                     'InputActions',
                                     'InfobarEPGActions',
                                     'ChannelSelectBaseActions'], {'ok': self.go,
                                                                   'back': self.close,
                                                                   'cancel': self.close,
                                                                   'yellow': self.update_me,  # update_me,
                                                                   'green': self.go,
                                                                   '0': self.arabic,
                                                                   'yellow_long': self.update_dev,
                                                                   'info_long': self.update_dev,
                                                                   'infolong': self.update_dev,
                                                                   'showEventInfoPlugin': self.update_dev,
                                                                   'red': self.close}, -1)
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.check_vers)
        else:
            self.timer.callback.append(self.check_vers)
        self.timer.start(500, 1)
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.getFeedList)
        else:
            self.timer.callback.append(self.getFeedList)
        self.timer.start(200, True)
        self.onClose.append(self.cleanup)

    def check_vers(self):
        remote_version = '0.0'
        remote_changelog = ''
        req = Utils.Request(Utils.b64decoder(installer_url), headers={'User-Agent': 'Mozilla/5.0'})
        page = Utils.urlopen(req).read()
        if PY3:
            data = page.decode("utf-8")
        else:
            data = page.encode("utf-8")
        if data:
            lines = data.split("\n")
            for line in lines:
                if line.startswith("version"):
                    remote_version = line.split("=")
                    remote_version = line.split("'")[1]
                if line.startswith("changelog"):
                    remote_changelog = line.split("=")
                    remote_changelog = line.split("'")[1]
                    break
        self.new_version = remote_version
        self.new_changelog = remote_changelog
        if float(currversion) < float(remote_version):
        # if currversion < remote_version:
            self.Update = True
            # self['key_yellow'].show()
            # self['key_green'].show()
            self.session.open(MessageBox, _('New version %s is available\n\nChangelog: %s\n\nPress info_long or yellow_long button to start force updating.') % (self.new_version, self.new_changelog), MessageBox.TYPE_INFO, timeout=5)
        # self.update_me()

    def update_me(self):
        if self.Update is True:
            self.session.openWithCallback(self.install_update, MessageBox, _("New version %s is available.\n\nChangelog: %s \n\nDo you want to install it now?") % (self.new_version, self.new_changelog), MessageBox.TYPE_YESNO)
        else:
            self.session.open(MessageBox, _("Congrats! You already have the latest version..."),  MessageBox.TYPE_INFO, timeout=4)

    def update_dev(self):
        try:
            req = Utils.Request(Utils.b64decoder(developer_url), headers={'User-Agent': 'Mozilla/5.0'})
            page = Utils.urlopen(req).read()
            data = json.loads(page)
            remote_date = data['pushed_at']
            strp_remote_date = datetime.strptime(remote_date, '%Y-%m-%dT%H:%M:%SZ')
            remote_date = strp_remote_date.strftime('%Y-%m-%d')
            self.session.openWithCallback(self.install_update, MessageBox, _("Do you want to install update ( %s ) now?") % (remote_date), MessageBox.TYPE_YESNO)
        except Exception as e:
            print('error xcons:', e)

    def install_update(self, answer=False):
        if answer:
            cmd1 = 'wget -q "--no-check-certificate" ' + Utils.b64decoder(installer_url) + ' -O - | /bin/sh'
            self.session.open(xConsole, 'Upgrading...', cmdlist=[cmd1], finishedCallback=self.myCallback, closeOnSuccess=False)
        else:
            self.session.open(MessageBox, _("Update Aborted!"),  MessageBox.TYPE_INFO, timeout=3)

    def myCallback(self, result=None):
        print('result:', result)
        return

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
            nodex['title'] = self.decodeHtml(self.get_txt(node, 'title', '<no title>'))
            nodex['date'] = self.get_txt(node, 'pubDate', self.get_txt(node, 'date', ''))
            nodex['desc'] = self.decodeHtml(self.get_txt(node, 'description', ''))
            data.append(nodex)
        return data

    def decodeHtml(self, text):
        charlist = []
        charlist.append(('&#034;', '"'))
        charlist.append(('&#038;', '&'))
        charlist.append(('&#039;', "'"))
        charlist.append(('&#060;', ' '))
        charlist.append(('&#062;', ' '))
        charlist.append(('&#160;', ' '))
        charlist.append(('&#174;', ''))
        charlist.append(('&#192;', '\xc3\x80'))
        charlist.append(('&#193;', '\xc3\x81'))
        charlist.append(('&#194;', '\xc3\x82'))
        charlist.append(('&#196;', '\xc3\x84'))
        charlist.append(('&#204;', '\xc3\x8c'))
        charlist.append(('&#205;', '\xc3\x8d'))
        charlist.append(('&#206;', '\xc3\x8e'))
        charlist.append(('&#207;', '\xc3\x8f'))
        charlist.append(('&#210;', '\xc3\x92'))
        charlist.append(('&#211;', '\xc3\x93'))
        charlist.append(('&#212;', '\xc3\x94'))
        charlist.append(('&#214;', '\xc3\x96'))
        charlist.append(('&#217;', '\xc3\x99'))
        charlist.append(('&#218;', '\xc3\x9a'))
        charlist.append(('&#219;', '\xc3\x9b'))
        charlist.append(('&#220;', '\xc3\x9c'))
        charlist.append(('&#223;', '\xc3\x9f'))
        charlist.append(('&#224;', '\xc3\xa0'))
        charlist.append(('&#225;', '\xc3\xa1'))
        charlist.append(('&#226;', '\xc3\xa2'))
        charlist.append(('&#228;', '\xc3\xa4'))
        charlist.append(('&#232;', '\xc3\xa8'))
        charlist.append(('&#233;', '\xc3\xa9'))
        charlist.append(('&#234;', '\xc3\xaa'))
        charlist.append(('&#235;', '\xc3\xab'))
        charlist.append(('&#236;', '\xc3\xac'))
        charlist.append(('&#237;', '\xc3\xad'))
        charlist.append(('&#238;', '\xc3\xae'))
        charlist.append(('&#239;', '\xc3\xaf'))
        charlist.append(('&#242;', '\xc3\xb2'))
        charlist.append(('&#243;', '\xc3\xb3'))
        charlist.append(('&#244;', '\xc3\xb4'))
        charlist.append(('&#246;', '\xc3\xb6'))
        charlist.append(('&#249;', '\xc3\xb9'))
        charlist.append(('&#250;', '\xc3\xba'))
        charlist.append(('&#251;', '\xc3\xbb'))
        charlist.append(('&#252;', '\xc3\xbc'))
        charlist.append(('&#8203;', ''))
        charlist.append(('&#8211;', '-'))
        charlist.append(('&#8211;', '-'))
        charlist.append(('&#8212;', ''))
        charlist.append(('&#8212;', '—'))
        charlist.append(('&#8216;', "'"))
        charlist.append(('&#8216;', "'"))
        charlist.append(('&#8217;', "'"))
        charlist.append(('&#8217;', "'"))
        charlist.append(('&#8220;', "'"))
        charlist.append(('&#8220;', ''))
        charlist.append(('&#8221;', '"'))
        charlist.append(('&#8222;', ''))
        charlist.append(('&#8222;', ', '))
        charlist.append(('&#8230;', '...'))
        charlist.append(('&#8230;', '...'))
        charlist.append(('&#8234;', ''))
        charlist.append(('&#x21;', '!'))
        charlist.append(('&#x26;', '&'))
        charlist.append(('&#x27;', "'"))
        charlist.append(('&#x3f;', '?'))
        charlist.append(('&#xB7;', '·'))
        charlist.append(('&#xC4;', 'Ä'))
        charlist.append(('&#xD6;', 'Ö'))
        charlist.append(('&#xDC;', 'Ü'))
        charlist.append(('&#xDF;', 'ß'))
        charlist.append(('&#xE4;', 'ä'))
        charlist.append(('&#xE9;', 'é'))
        charlist.append(('&#xF6;', 'ö'))
        charlist.append(('&#xF8;', 'ø'))
        charlist.append(('&#xFB;', 'û'))
        charlist.append(('&#xFC;', 'ü'))
        charlist.append(('&8221;', '\xe2\x80\x9d'))
        charlist.append(('&8482;', '\xe2\x84\xa2'))
        charlist.append(('&Aacute;', '\xc3\x81'))
        charlist.append(('&Acirc;', '\xc3\x82'))
        charlist.append(('&Agrave;', '\xc3\x80'))
        charlist.append(('&Auml;', '\xc3\x84'))
        charlist.append(('&Iacute;', '\xc3\x8d'))
        charlist.append(('&Icirc;', '\xc3\x8e'))
        charlist.append(('&Igrave;', '\xc3\x8c'))
        charlist.append(('&Iuml;', '\xc3\x8f'))
        charlist.append(('&Oacute;', '\xc3\x93'))
        charlist.append(('&Ocirc;', '\xc3\x94'))
        charlist.append(('&Ograve;', '\xc3\x92'))
        charlist.append(('&Ouml;', '\xc3\x96'))
        charlist.append(('&Uacute;', '\xc3\x9a'))
        charlist.append(('&Ucirc;', '\xc3\x9b'))
        charlist.append(('&Ugrave;', '\xc3\x99'))
        charlist.append(('&Uuml;', '\xc3\x9c'))
        charlist.append(('&aacute;', '\xc3\xa1'))
        charlist.append(('&acirc;', '\xc3\xa2'))
        charlist.append(('&acute;', '\''))
        charlist.append(('&agrave;', '\xc3\xa0'))
        charlist.append(('&amp;', '&'))
        charlist.append(('&apos;', "'"))
        charlist.append(('&auml;', '\xc3\xa4'))
        charlist.append(('&bdquo;', '"'))
        charlist.append(('&bdquo;', '"'))
        charlist.append(('&eacute;', '\xc3\xa9'))
        charlist.append(('&ecirc;', '\xc3\xaa'))
        charlist.append(('&egrave;', '\xc3\xa8'))
        charlist.append(('&euml;', '\xc3\xab'))
        charlist.append(('&gt;', '>'))
        charlist.append(('&hellip;', '...'))
        charlist.append(('&iacute;', '\xc3\xad'))
        charlist.append(('&icirc;', '\xc3\xae'))
        charlist.append(('&igrave;', '\xc3\xac'))
        charlist.append(('&iuml;', '\xc3\xaf'))
        charlist.append(('&laquo;', '"'))
        charlist.append(('&ldquo;', '"'))
        charlist.append(('&lsquo;', '\''))
        charlist.append(('&lt;', '<'))
        charlist.append(('&mdash;', '—'))
        charlist.append(('&nbsp;', ' '))
        charlist.append(('&ndash;', '-'))
        charlist.append(('&oacute;', '\xc3\xb3'))
        charlist.append(('&ocirc;', '\xc3\xb4'))
        charlist.append(('&ograve;', '\xc3\xb2'))
        charlist.append(('&ouml;', '\xc3\xb6'))
        charlist.append(('&quot;', '"'))
        charlist.append(('&raquo;', '"'))
        charlist.append(('&rsquo;', '\''))
        charlist.append(('&szlig;', '\xc3\x9f'))
        charlist.append(('&uacute;', '\xc3\xba'))
        charlist.append(('&ucirc;', '\xc3\xbb'))
        charlist.append(('&ugrave;', '\xc3\xb9'))
        charlist.append(('&uuml;', '\xc3\xbc'))
        charlist.append(('\u0026', '&'))
        charlist.append(('\u003d', '='))
        charlist.append(('\u00a0', ' '))
        charlist.append(('\u00b4', '\''))
        charlist.append(('\u00c1', 'Á'))
        charlist.append(('\u00c4', 'Ä'))
        charlist.append(('\u00c6', 'Æ'))
        charlist.append(('\u00d6', 'Ö'))
        charlist.append(('\u00dc', 'Ü'))
        charlist.append(('\u00df', 'ß'))
        charlist.append(('\u00e0', 'à'))
        charlist.append(('\u00e1', 'á'))
        charlist.append(('\u00e4', 'ä'))
        charlist.append(('\u00e7', 'ç'))
        charlist.append(('\u00e8', 'é'))
        charlist.append(('\u00e9', 'é'))
        charlist.append(('\u00f6', 'ö'))
        charlist.append(('\u00fc', 'ü'))
        charlist.append(('\u014d', 'ō'))
        charlist.append(('\u016b', 'ū'))
        charlist.append(('\u2013', '–'))
        charlist.append(('\u2018', '\"'))
        charlist.append(('\u2019s', '’'))
        charlist.append(('\u201a', '\"'))
        charlist.append(('\u201c', '\"'))
        charlist.append(('\u201d', '\''))
        charlist.append(('\u201e', '\"'))
        charlist.append(('\u2026', '...'))
        for repl in charlist:
            text = text.replace(repl[0], repl[1])
        from re import sub as re_sub
        text = re_sub('<[^>]+>', '', text)
        return str(text).encode('utf-8').decode('unicode_escape')  # str needed for PLi
