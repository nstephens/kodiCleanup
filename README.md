# kodiCleanup

kodiCleanup provides an easy way to have granular control over deleting videos that you have watched on Kodi.  Note: This is
a command line python script, designed for user interaction, NOT as a kodi plugin.  With this, you would run it from a comput
er with direct access (or a remote mount) to the storage device with the media files. 

This python script queries Kodi via JSON RPC to get a list of all of the TV Episodes that have been marked as "watched".  It
then presents them to you in a curses multiselect environment, so that you can simply check off everything you are ok with de
leting.  This makes keeping your storage space in check very easy.

## Requirements
pip3 install npycurses
pip3 install requests

## Screenshots

  ![](http://manipulate.org/downloads/kodiCleanup/demos/confirm_delete.png)
  
  ![](http://manipulate.org/downloads/kodiCleanup/demos/kodi_libraryclean.png)
  
  ![](http://manipulate.org/downloads/kodiCleanup/demos/results.png)
