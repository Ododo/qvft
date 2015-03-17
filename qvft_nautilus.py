from __future__ import with_statement

import os
import json
import requests

import easygui

from uuid import UUID
from gi.repository import Nautilus, GObject


REQ_URL = 'https://qvft-ododo.rhcloud.com/'
DB_DIR = os.path.join(os.environ['HOME'], '.qvft')
DB_PATH = os.path.join(DB_DIR, 'keys.json')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)


def abs_from_uri(uri):
    uri = str(uri).replace('%20', ' ')
    return '/' + uri.strip("file:/")


class QvftExtension(GObject.GObject, Nautilus.MenuProvider,
                      Nautilus.LocationWidgetProvider):

    def __init__(self):
        print('QVFT Initialization...')
        self.location = None
        self.db_load()
        self.refresh(None)
    
    def db_load(self):
        with open(DB_PATH, 'a+') as fp:
            fp.seek(0)
            try:
                self.db = json.load(fp)
            except ValueError:
                self.db = {}
                fp.seek(0)
                json.dump(self.db, fp)

    def db_save(self):
        with open(DB_PATH, 'r+') as fp:
            json.dump(self.db, fp)    

    def qvft_newkey(self, menu):
        req = requests.get(REQ_URL + 'newkey')
        key = req.text
        easygui.textbox(msg="This is a new key, share it with who you want !", \
                        text=key)
        name = easygui.enterbox(msg="Enter a name for this new key")

        if not name:
            return

        self.db[name] = key
        self.db_save()

    def qvft_addkey(self, menu):
        try:
            name, key = easygui.multenterbox(msg="Enter the new shared key", fields=('name', 'key'))
            UUID(key)
        except ValueError:
            easygui.msgbox(msg="This is not a valid key")
            return self.qvft_addkey(menu)
        except TypeError:
            return

        self.db[name] = key
        self.db_save()

        easygui.msgbox(msg='Key successfully added !')
            
                
    def qvft_list_files(self):
        files = {}
        for key in self.db.values():
            req = requests.get(REQ_URL + 'fileslist', params={'key': key})
            try: 
                a = req.json
                for f in a[:-1]:
                    files[f] = key
            except (ValueError, TypeError):
                continue

        return files

        
    def qvft_download_file(self, menu, filename):
        req = requests.get(REQ_URL + 'getfile',
                           params={'filename' : filename, 
                                   'key': self.last_update_files[filename]})
        if req.status_code != 200:
            return

        with open('%s/%s' % (self.location, filename), 'wb+') as fp:
            for chunk in req.iter_content(chunk_size=1024):
                fp.write(chunk)

    def qvft_upload_files(self, menu, paths, key):
        for p in paths:
            req = requests.post(REQ_URL + 'upload/', data={'key' : key}, 
                               files={'file' : open(p, 'rb')})

    def refresh(self, menu):
        self.last_update_files = self.qvft_list_files()

    def get_widget(self, uri, window):
        self.location = abs_from_uri(uri)

    def get_file_items(self, window, files):
        top_menuitem = Nautilus.MenuItem(name='QvftMenu::Upload', 
                                         label='Qvft Upload to', 
                                         tip='',
                                         icon='')

        submenu = Nautilus.Menu()
        top_menuitem.set_submenu(submenu)

        #print(files[0].get_uri())
        paths = [abs_from_uri(f.get_uri()) for f in files]
        for name, key in self.db.iteritems():
            sub_menuitem = Nautilus.MenuItem(name='QvftMenu::%s' % name, 
                                         label=name, 
                                         tip='',
                                         icon='')
            sub_menuitem.connect('activate', self.qvft_upload_files, paths, key)
            submenu.append_item(sub_menuitem)

        return top_menuitem,

    def get_background_items(self, window, file):
        submenu = Nautilus.Menu()
        downloads_submenu = Nautilus.Menu()


        item_addkey = Nautilus.MenuItem(name='QvftMenu::AddKey', 
                                         label='Add a key', 
                                         tip='',
                                         icon='')

        item_newkey = Nautilus.MenuItem(name='QvftMenu::NewKey', 
                                         label='Request new key', 
                                         tip='',
                                         icon='')

        item_downloads = Nautilus.MenuItem(name='QvftMenu::Downloads', 
                                         label='Downloads', 
                                         tip='',
                                         icon='')

        item_refresh = Nautilus.MenuItem(name='QvftMenu::Refresh', 
                                         label='Refresh', 
                                         tip='',
                                         icon='')


        item_newkey.connect('activate', self.qvft_newkey)
        item_addkey.connect('activate', self.qvft_addkey)
        item_refresh.connect('activate', self.refresh)

        for filename in self.last_update_files:
            if filename != '':
                fm = Nautilus.MenuItem(name='QvftMenu::%s' % filename, 
                                         label=filename, 
                                         tip='',
                                         icon='')

                fm.connect('activate', self.qvft_download_file, filename)
                downloads_submenu.append_item(fm)
      
        item_downloads.set_submenu(downloads_submenu)
        
        submenu.append_item(item_downloads) #will not appear if there is no file
        submenu.append_item(item_newkey)
        submenu.append_item(item_addkey)
        submenu.append_item(item_refresh)

        menuitem = Nautilus.MenuItem(name='QvftMenu::Foo2', 
                                         label='Qvft', 
                                         tip='',
                                         icon='')
        menuitem.set_submenu(submenu)

        return menuitem,

