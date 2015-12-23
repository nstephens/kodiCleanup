#!/usr/bin/env python3
import npyscreen
import requests
import json
import re
import os,sys

## url to your web enabled kodi
url = "http://192.168.0.99:8080/jsonrpc" ## IP of your kodi install

## pipe separate a list of names of tv shows that you never want to delete
## leave excludeList commented out if you aren't whitelisting anything
# excludeList = re.compile("\/an\/entire directory\/|TV Show|Other Show")

class Kodi(object):

    def clean_up(self):
        self.cleanList = []
        for fileStr in self.watchedDict:
            # my library is hosted in a DB with hardcoded smb paths, need to strip that
            tmpStr = fileStr.lstrip("smb://")
            startStr = tmpStr.find("/")
            self.cleanList.append(tmpStr[startStr:])

    def cleanLibrary(self):
        cleanLib = {"jsonrpc": "2.0",
               "method": "VideoLibrary.Clean",
               "id": "1",
               "params": {}
               }

        self.r = requests.post(url, data=json.dumps(cleanLib).encode('utf-8'), headers=self.headers)

    def getWatchedList(self, clean=False):
        global url
        global excludeList

        self.headers = {'content-type': 'application/json'}

        getVideos = {"jsonrpc": "2.0",
                     "method": "VideoLibrary.GetEpisodes",
                     "id": "1",
                     "params": {
                         "filter": {
                             "field": "playcount",
                             "operator": "is",
                             "value": "1"
                         },
                         "properties": [
                             "season",
                             "episode",
                             "resume",
                             "playcount",
                             "tvshowid",
                             "lastplayed",
                             "file"
                         ],
                         "sort": {
                             "order": "descending",
                             "method": "lastplayed",
                         },
                     }
                     }
        getShowNames = {"jsonrpc": "2.0",
                        "method": "VideoLibrary.GetTVShows",
                        "id": "1",
                        "params": {}
                        }

        r = requests.post(url, data=json.dumps(getVideos).encode('utf-8'), headers=self.headers)

        xbmc_json = r.json()
        self.watchedDict = []
        for i in xbmc_json['result']['episodes']:
            if 'excludeList' in globals():
                if re.search(excludeList, i['file']):
                    pass
                else:
                    self.watchedDict.append(i['file'])
            else:
                self.watchedDict.append(i['file'])

        if clean:
            self.clean_up()
            return self.cleanList
        else:
            return self.watchedDict


class MyCleanupApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.myKodi = Kodi()
        self.fileList = ""
        self.addForm("MAIN", FileListForm, name="KodiCleanup | Select files for deletion", color="IMPORTANT",)

    def goodbye(self):
        npyscreen.notify_wait("Goodbye!")
        exit(0)

    def onCleanExit(self):
        self.goodbye()

    def getHumanReadable(self,size,precision=2):
        suffixes=['B','KB','MB','GB','TB']
        suffixIndex = 0
        while size > 1024 and suffixIndex < 4:
            suffixIndex += 1 #increment the index of the suffix
            size = size/1024.0 #apply the division
        return "%.*f%s"%(precision,size,suffixes[suffixIndex])

    def rm(self):
        self.byteCount = 0
        self.fCount = 0
        for item in self.fileList:
            if os.path.isfile(item):
                self.mySize = os.path.getsize(item)
                os.remove(item)
                self.byteCount += self.mySize
                self.fCount += 1
        self.humanCount = self.getHumanReadable(self.byteCount)


class FileListForm(npyscreen.ActionFormV2):
    def create(self):
        global url
        fileCount = ""
        npyscreen.notify("Please wait while we build your file list\n[ Fetching from: " + url + " ]", title="Welcome to KodiCleanup", form_color='STANDOUT',
                  wrap=True, wide=False)
        self.myFiles = self.add(npyscreen.MultiSelect, max_height=0, editable=True,
                         values=self.parentApp.myKodi.getWatchedList(clean=True), scroll_exit=False)

    def on_ok(self):
        if self.myFiles.get_selected_objects():
            self.parentApp.fileList = self.myFiles.get_selected_objects()
            self.fileCount = str(len(self.parentApp.fileList))
            self.confirmMsg = "Really delete " + self.fileCount + " files?"
            if npyscreen.notify_ok_cancel(self.confirmMsg, "KodiCleanup | Confirm Deletion", editw=1):
                self.myResults = self.parentApp.rm()
                if npyscreen.notify_ok_cancel("Would you like to clean Kodi's Library now?", "KodiCleanup | VideoLibrary.Clean", editw=1):
                    self.parentApp.myKodi.cleanLibrary()

                npyscreen.notify_confirm("Requested Files for Deletion: " + str(self.fileCount) +
                                    "\nActual Files Deleted: " + str(self.parentApp.fCount) +
                                    "\nTotal Space Freed: " + self.parentApp.humanCount, "KodiCleanup Complete")
                self.parentApp.goodbye()
            else:
                pass
        else:
            npyscreen.notify_wait("No files selected!")

    def on_cancel(self):
        # exit the app on cancel
        self.parentApp.setNextForm(None)

def main():
    myApp = MyCleanupApp()
    myApp.run()


if __name__ == '__main__':
    main()
