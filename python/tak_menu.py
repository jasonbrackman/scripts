'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 2014-06-12

Description:
This script is for that add custom menu to maya main window.

Usage:
1. Place tak_menu.py in your maya scripts folder.
2. Open userSetup.mel and write a line below.
python("import tak_menu");
python("tak_menu.takMenu()");
3. Restart maya.
'''

import maya.cmds as cmds

def takMenu():
    cmds.menu('takMenu', to = True, label = 'Tak', parent = 'MayaWindow')
    cmds.menuItem(label = 'Tak Tools', c = "import tak_tools\nreload(tak_tools)\ntak_tools.UI()")