from PySide import QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken import wrapInstance

def mayaMainWin():
	mayaWinPtr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(mayaWinPtr), QtGui.QWidget)


class TempListWdg(QtGui.QWidget):
	def __init__(self):
		# Widget
		super(TempListWdg, self).__init__(mayaMainWin(), QtCore.Qt.Tool)
		self.setWindowTitle("List Widget")
		self.setGeometry(980, 520, 300, 300)
		
		# Create layout
		tmpLsWdgMainVLo = QtGui.QVBoxLayout(self)
		tmpLsWdgMainVLo.setContentsMargins(0, 0, 0, 0)
		
		# QListWidget
		listWdg = QtGui.QListWidget()

		# Create listWidgetItem and add to listWidget
		for i in xrange(5):
			listWdgItem = QtGui.QListWidgetItem()
			listWdgItem.setSizeHint(ListWdgItem().sizeHint())
			listWdg.addItem(listWdgItem)
			listWdg.setItemWidget(listWdgItem, ListWdgItem("test" + str(i)))
		
		# Add widgets to layout
		tmpLsWdgMainVLo.addWidget(listWdg)


class ListWdgItem(QtGui.QWidget):
	def __init__(self, label=""):
		super(ListWdgItem, self).__init__()
			
		lsWdgHLo = QtGui.QHBoxLayout()
		lsWdgHLo.setContentsMargins(0, 0, 0, 0)
		self.setLayout(lsWdgHLo)

		lsWdgItemLabel = QtGui.QLabel(label)
		lsWdgItemSpinBox = QtGui.QSpinBox()
		lsWdgItemSpinBox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
		lsWdgItemSpinBox1 = QtGui.QSpinBox()
		lsWdgItemSpinBox1.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)


		lsWdgHLo.addWidget(lsWdgItemLabel)
		lsWdgHLo.addWidget(lsWdgItemSpinBox)
		lsWdgHLo.addWidget(lsWdgItemSpinBox1)


if __name__ == "__main__":
	ui = TempListWdg()
	ui.show()


####################################### List Widget ###########################################################

from PySide import QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken import wrapInstance



def mayaMainWin():
	"""
	Get maya main window QWidget.
	"""
	
	MWinPtr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(MWinPtr), QtGui.QWidget)



class CorBsUi(QtGui.QWidget):
	def __init__(self):
		super(CorBsUi, self).__init__( parent=mayaMainWin(), f=QtCore.Qt.Tool )
		
		self.setWindowTitle('Corrective Blend Shape Tool')
		self.resize(300, 300)
		
		self.createWidget()
		self.createLayout()
		self.createConnections()
		
		
	def createWidget(self):
		self.mainMenuBar = QtGui.QMenuBar()
		
		# Create menu
		self.createMenu = self.mainMenuBar.addMenu('Create')
		self.editMenu = self.mainMenuBar.addMenu('Edit')
		
		# Create menu actions
		bsIcon = QtGui.QIcon(r'C:\Users\stlee\Documents\maya\2015-x64\prefs\icons\blendShape.png')
		self.addBsAction = QtGui.QAction(bsIcon, 'Add Blend Shape Node', self)
		self.addSelTrgAction = QtGui.QAction('Add Selected Targets', self)
		self.selBsNodeAction = QtGui.QAction('Select Blend Shape Node', self)
		self.renameBsNodeAction = QtGui.QAction('Rename Blend Shape Node', self)
		
		# Add actions
		self.createMenu.addAction(self.addBsAction)
		self.createMenu.addAction(self.addSelTrgAction)
		self.editMenu.addAction(self.selBsNodeAction)
		self.editMenu.addAction(self.renameBsNodeAction)
		
		self.baseGeoLabel = QtGui.QLabel('<font color=#fff000 size=4>' + 'Base Geometry: ' + '</font>')
		self.baseGeoLE = QtGui.QLineEdit()
		self.baseGeoBtn = QtGui.QPushButton('<<')
		
	
	
	def createLayout(self):
		mainLo = QtGui.QVBoxLayout(self)
		mainLo.setContentsMargins(0, 0, 0, 0)
		mainLo.setSpacing(0)
		
		baseGeoLo = QtGui.QHBoxLayout()
		baseGeoLo.addWidget(self.baseGeoLabel)
		baseGeoLo.addWidget(self.baseGeoLE)
		baseGeoLo.addWidget(self.baseGeoBtn)

		mainLo.addWidget(self.mainMenuBar)
		mainLo.addLayout(baseGeoLo)
		
		mainLo.addStretch()
	
		self.setLayout(mainLo)
				
	
	def createConnections(self):
		self.addBsAction.triggered.connect(self.addBs)
		self.baseGeoBtn.clicked.connect(self.loadSel)


	### Slot ###
	def addBs(self):
		print 'Add Blend Shape!'
	
	def loadSel(self):
		send = self.sender()
		print send.text()
		sel = cmds.ls(sl = True)[0]
		self.baseGeoLE.setText(sel)


if __name__ == '__main__':
	ui = CorBsUi()
	ui.show()





####################################### Popup Menu #######################################################

from PySide.QtCore import *
from PySide.QtGui import *
from maya import OpenMayaUI as omui
from shiboken import wrapInstance


def mayaMainWin():
	mayaWinPtr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(mayaWinPtr), QWidget)


class TestPopupMenu(QWidget):
	def __init__(self):
		super(TestPopupMenu, self).__init__()
		self.setParent(mayaMainWin())
		self.setWindowFlags(Qt.Tool)
		self.setWindowTitle("Tset Popup Menu")
		
		self.createLayouts()
		self.createWidgets()
		self.addWidgetsToLayouts()
			
		self.setLayout(self.mainLo)
	
	
	def createLayouts(self):
		self.mainLo = QVBoxLayout()
		self.mainLo.setContentsMargins(0, 0, 0, 0)
		
		
	def createWidgets(self):
		self.lsWdg = QListWidget()
		self.lsWdg.setContextMenuPolicy(Qt.ActionsContextMenu)
		self.lsWdg.setSelectionMode(QAbstractItemView.ExtendedSelection)
		for i in xrange(5):
			lsWdgItem = QListWidgetItem()	
			lsItemWdg = ListItemWidget("Target Shape " + str(i))	
			
			lsWdgItem.setSizeHint(lsItemWdg.sizeHint())
			
			self.lsWdg.addItem(lsWdgItem)
			self.lsWdg.setItemWidget(lsWdgItem, lsItemWdg)

		self.addMenuActions()
	

	def addMenuActions(self):
		refreshAction = QAction(self.lsWdg)
		refreshAction.setText("Refresh List")
		refreshAction.triggered.connect(self.refreshList)
		self.lsWdg.addAction(refreshAction)
		
		sprt = QAction(self.lsWdg)
		sprt.setSeparator(True)
		self.lsWdg.addAction(sprt)
		
		eidtAction = QAction(self.lsWdg)
		eidtAction.setText("Edit")
		self.lsWdg.addAction(eidtAction)


	def addWidgetsToLayouts(self):
		self.mainLo.addWidget(self.lsWdg)
	

	### Slots ###
	def refreshList(self):
		selItems = self.lsWdg.selectedItems()
		for selItem in selItems:
			itemWdg = self.lsWdg.itemWidget(selItem)
			print itemWdg.label.text()


class ListItemWidget(QWidget):
	def __init__(self, label):
		super(ListItemWidget, self).__init__()
		
		self.bsTrgName = label
		
		self.createLayouts()
		self.createWidgets()
		self.addWidgetsToLayouts()
	

	def createLayouts(self):
		self.mainLo = QHBoxLayout()
		self.mainLo.setContentsMargins(0, 0, 0, 0)
		
		self.setLayout(self.mainLo)
	

	def createWidgets(self):
		self.label = QLabel(self.bsTrgName)
		self.wgtVal = QSpinBox()
		self.startAngle = QSpinBox()
		

	def addWidgetsToLayouts(self):
		self.mainLo.addWidget(self.label)
		self.mainLo.addWidget(self.wgtVal)
		self.mainLo.addWidget(self.startAngle)


if __name__ == "__main__":
	ui = TestPopupMenu()
	ui.show()




#################################
# Connect Qt and Maya Attribute #
#################################

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin
import functools
import maya.OpenMaya as om
from PySide.QtCore import *
from PySide.QtGui import *


class Example_connectAttr(MayaQWidgetDockableMixin, QScrollArea):
	
	def __init__(self, node=None, *args, **kwargs):
		super(Example_connectAttr, self).__init__(*args, **kwargs)
		# Member Variables
		self.nodeName = node               # Node name for the UI
		self.attrUI = None                 # Container widget for the attr UI widgets
		self.attrWidgets = {}              # Dict key=attrName, value=widget
		self._deferredUpdateRequest = {}

		self.setAttribute(Qt.WA_DeleteOnClose)
		self.resize(150, 300)


	def __del__(self):
		for nodeCallback in self.nodeCallbacks:
			om.MMessage.removeCallback(nodeCallback)
			print ">>> Callback {0} is removed.".format(nodeCallback)
	

	def attachToNode(self):
		'''
		Connect UI to the specified node
		'''

		self.attrs = None
		self.nodeCallbacks = []
		self._deferredUpdateRequest.clear()
		self.attrWidgets.clear()

		# Get a sorted list of the attributes
		# attrs = cmds.listAttr(self.nodeName, keyable=True)
		attrs = cmds.listAttr('%s.w' %(self.nodeName), multi = True)
		print attrs
		attrs.sort() # in-place sort the attributes

		# Create container for attribute widgets
		self.setWindowTitle('ConnectAttrs: %s'%self.nodeName)
		self.attrUI = QWidget(parent=self)
		layout = QFormLayout()

		# Loop over the attributes and construct widgets
		acceptedAttrTypes = set(['doubleLinear', 'string', 'double', 'float', 'long', 'short', 'bool', 'time', 'doubleAngle', 'byte', 'enum'])
		for attr in attrs:
			# Get the attr value (and skip if invalid)
			try:
				attrType = cmds.getAttr('%s.%s'%(self.nodeName, attr), type=True)
				if attrType not in acceptedAttrTypes:
					continue # skip attr
				v = cmds.getAttr('%s.%s'%(self.nodeName, attr))
			except Exception, e:
				continue  # skip attr

			# Create the widget and bind the function
			attrValueWidget = QLineEdit()
			attrValueWidget.setText(str(v))

			# Add to layout
			layout.addRow(attr, attrValueWidget)

			# Track the widget associated with a particular attribute
			self.attrWidgets[attr] = attrValueWidget

			# Connect Qt widget to maya attribute
			# Use functools.partial() to dynamically construct a function with additional parameters
			onSetAttrFunc = functools.partial(self.onSetAttr, widget=attrValueWidget, attrName=attr)
			attrValueWidget.editingFinished.connect( onSetAttrFunc )

			# Connect maya attribute to Qt widget
			nodeObj = self.getDependNode(self.nodeName)
			# cb = om.MNodeMessage.addAttributeChangedCallback(nodeObj, self.onAttributeChangedCB, None)
			cb = om.MNodeMessage.addNodeDirtyPlugCallback(nodeObj, self.onDirtyPlug, None)
			self.nodeCallbacks.append( MCallbackIdWrapper(cb) )

		# Attach the QFormLayout to the root attrUI widget
		self.attrUI.setLayout(layout)

	
	def onSetAttr(self, widget, attrName, *args, **kwargs):
		'''Handle setting the attribute when the UI widget edits the value for it.
		If it fails to set the value, then restore the original value to the UI widget
		'''
		print "onSetAttr", attrName, widget, args, kwargs
			
		try:
			attrType = cmds.getAttr('%s.%s'%(self.nodeName, attrName), type=True)
			if attrType == 'string':
				cmds.setAttr('%s.%s'%(self.nodeName, attrName), widget.text(), type=attrType)
			else:
				cmds.setAttr('%s.%s'%(self.nodeName, attrName), eval(widget.text()))
		except Exception, e:
			print e
			curVal = cmds.getAttr('%s.%s'%(self.nodeName, attrName))
			widget.setText( str(curVal) )

	
	def onDirtyPlug(self, node, plug, *args, **kwargs):
		'''Add to the self._deferredUpdateRequest member variable that is then
		deferred processed by self._processDeferredUpdateRequest().
		'''

		# get long name of the attr, to use as the dict key
		attrName = plug.partialName(False, False, False, True, False, True)

		# get widget associated with the attr
		widget = self.attrWidgets.get(attrName, None)
		if widget != None:
			# get node.attr string
			nodeAttrName = plug.name()
			
			# Add to the dict of widgets to defer update
			self._deferredUpdateRequest[widget] = nodeAttrName
			
			# Trigger an evalDeferred action if not already done
			if len(self._deferredUpdateRequest) == 1:
				cmds.evalDeferred(self._processDeferredUpdateRequest, low=True)


	def onAttributeChangedCB(self, msg, plug, otherPlug, *args, **kwargs):
		# get long name of the attr, to use as the dict key
		attrName = plug.partialName(False, False, False, True, False, True)
		# attrName = plug.name()
		print ">>> Attribute Name: " + attrName

		# get widget associated with the attr
		widget = self.attrWidgets.get(attrName, None)
		if widget != None:
			# get node.attr string
			# nodeAttrName = plug.partialName(True, False, False, False, False, True)
			nodeAttrName = plug.name()
			print nodeAttrName
			
			# Add to the dict of widgets to defer update
			self._deferredUpdateRequest[widget] = nodeAttrName
			
			# Trigger an evalDeferred action if not already done
			if len(self._deferredUpdateRequest) == 1:
				cmds.evalDeferred(self._processDeferredUpdateRequest, low=True)

	
	def _processDeferredUpdateRequest(self):
		'''Retrieve the attribute value and set the widget value
		'''
		for widget,nodeAttrName in self._deferredUpdateRequest.items():
			v = cmds.getAttr(nodeAttrName)
			widget.setText(str(v))
			print "_processDeferredUpdateRequest ", widget, nodeAttrName, v
		self._deferredUpdateRequest.clear()

	
	def getDependNode(self, nodeName):
		mSelLs = om.MSelectionList()
		mSelLs.add(nodeName)

		dependNode = om.MObject()
		mSelLs.getDependNode(0, dependNode)

		return dependNode



class MCallbackIdWrapper(object):
	'''
	Wrapper class to handle cleaning up of MCallbackIds from registered MMessage
	'''

	def __init__(self, callbackId):
		super(MCallbackIdWrapper, self).__init__()
		self.callbackId = callbackId

	def __del__(self):
		om.MMessage.removeCallback(self.callbackId)

	def __repr__(self):
		return 'MCallbackIdWrapper(%r)'%self.callbackId



# obj = cmds.polyCube(ch=False)[0]
obj = "blendShape1"
ui = Example_connectAttr(node=obj)
ui.attachToNode()
ui.show(dockable=True, floating=True)




#########################################
## List Widget Connected to Blendshape ##
#########################################

from PySide.QtCore import *
from PySide.QtGui import *
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import pymel.core as pm
from shiboken import wrapInstance


def mayaMainWin():
	mayaWinPtr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(mayaWinPtr), QWidget)


class TargetShapeList(QWidget):
	def __init__(self):
		super(TargetShapeList, self).__init__()
		
		self.setWindowTitle("Target Shape List")
		self.setParent(mayaMainWin())
		self.setWindowFlags(Qt.Tool)
		self.setAttribute(Qt.WA_DeleteOnClose)
	
	def __del__(self):
		print "Widget has deleted."
		

if __name__ == "__main__":
	ui = TargetShapeList()
	ui.show()
	del(ui)


################################
# Frame Widget Using QGroupBox #
################################

from PySide2.QtCore import * 
from PySide2.QtGui import *
from PySide2.QtWidgets import *

 
class FrameWidget(QGroupBox):
	def __init__(self, title='', parent=None):
		super(FrameWidget, self).__init__(title, parent)
		 
		layout = QVBoxLayout()
		layout.setContentsMargins(0, 7, 0, 0)
		layout.setSpacing(0)
		super(FrameWidget, self).setLayout(layout)
		 
		self.__widget = QFrame(parent)
		self.__widget.setFrameShape(QFrame.Panel)
		self.__widget.setFrameShadow(QFrame.Plain)
		self.__widget.setLineWidth(0)
		layout.addWidget(self.__widget)
		 
		self.__collapsed = False
	 
	def setLayout(self, layout):
		self.__widget.setLayout(layout)
		 
	def expandCollapseRect(self):
		return QRect(0, 0, self.width(), 20)
 
	def mouseReleaseEvent(self, event):
		if self.expandCollapseRect().contains(event.pos()):
			self.toggleCollapsed()
			event.accept()
		else:
			event.ignore()
	 
	def toggleCollapsed(self):
		self.setCollapsed(not self.__collapsed)
		 
	def setCollapsed(self, state=True):
		self.__collapsed = state
 
		if state:
			self.setMinimumHeight(20)
			self.setMaximumHeight(20)
			self.__widget.setVisible(False)
		else:
			self.setMinimumHeight(0)
			self.setMaximumHeight(1000000)
			self.__widget.setVisible(True)
			 
	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		 
		font = painter.font()
		font.setBold(True)
		painter.setFont(font)
 
		x = self.rect().x()
		y = self.rect().y()
		w = self.rect().width()
		offset = 25

		painter.setRenderHint(painter.Antialiasing)
		painter.fillRect(self.expandCollapseRect(), QColor(93, 93, 93))
		painter.drawText(
			x + offset, y + 3, w, 16,
			Qt.AlignLeft | Qt.AlignTop,
			self.title()
			)
		self.__drawTriangle(painter, x, y)
		painter.setRenderHint(QPainter.Antialiasing, False)
		painter.end()


	def __drawTriangle(self, painter, x, y):
		if not self.__collapsed:
			points = [  QPoint(x+10,  y+6 ),
						QPoint(x+20, y+6 ),
						QPoint(x+15, y+11)
						]
			 
		else:
			points = [  QPoint(x+10, y+4 ),
						QPoint(x+15, y+9 ),
						QPoint(x+10, y+14)
						]
			 
		currentBrush = painter.brush()
		currentPen   = painter.pen()
		 
		painter.setBrush(
			QBrush(
				QColor(187, 187, 187),
				Qt.SolidPattern
				)
			)
		painter.setPen(QPen(Qt.NoPen))
		painter.drawPolygon(QPolygon(points))
		painter.setBrush(currentBrush)
		painter.setPen(currentPen)



window = QMainWindow()
window.setWindowTitle('Frame Widget Test')
 
frame = FrameWidget('Frame Title', window)
window.setCentralWidget(frame)
 
widget = QWidget(frame)
layout = QVBoxLayout(widget)
frame.setLayout(layout)
for i in range(5):
	layout.addWidget(QPushButton('Button %s' % i, widget))
 
window.show()




# - * - coding : utf-8 - * -

import os
import sys

from PySide import QtCore, QtGui
from PySide.QtUiTools import QUiLoader

CURRENT_PATH = os.path.dirname (__ file__)

# ------------------------------------------------- ---------------------------
## FrameLayout을 만드는 클래스
class FrameLayout (object) :

    def __init __ (self, titleBar, frame) :
        self.titleBar = titleBar #에서 버튼 위젯
        self.frame = frame # 개폐하는 위젯
        self.collapse = False # 개폐 상태 플래그
        self.setSignals () # 신호를 세트

    # ------------------------------------------------- ------------------------
    ## 신호를 설정
    def setSignals (self) :
        self.titleBar.clicked.connect (self.setCollapse)

    # ------------------------------------------------- ------------------------
    ## 프레임을 개폐하는 액션
    def setCollapse (self) :
        # 현재의 상태를 반전
        self.collapse = not self.collapse
        # 프레임의 가시성을 변경하려면
        self.frame.setHidden (self.collapse)

        # 개폐 상황에 맞게 화살표 유형을 변경하려면
        if self.collapse :
            # 닫혀있을 때는 오른쪽으로 조준
            self.titleBar.setArrowType (QtCore.Qt.RightArrow)
        else :
            # 열려있을 때는 아래로 향하게
            self.titleBar.setArrowType (QtCore.Qt.DownArrow)


# ------------------------------------------------- ---------------------------
## GUI를 만드는 클래스
class GUI (QtGui.QMainWindow) :

    def __init __ (self, parent = None) :
        super (GUI, self) .__ init __ (parent)
        loader = QUiLoader ()
        uiFilePath = os.path.join (CURRENT_PATH 'frameLayout.ui')
        self.UI = loader.load (uiFilePath)
        self.setCentralWidget (self.UI)

        # 프레임 레이아웃 클래스에 전달
        self.frameLayout = FrameLayout (self.UI.toolButton, self.UI.frame)

# ------------------------------------------------- -----------------------------
## GUI 시작
def main () :
    app = QtGui.QApplication (sys.argv)
    app.setStyle ( 'plastique') # ← 여기에 스타일을 지정
    ui = (GUI)
    ui.show ()
    sys.exit (app.exec_ ())


if __name__ == '__main__':
    main ()

# ------------------------------------------------- ----------------------------
# EOF
# ------------------------------------------------- ----------------------------





# Dockable Window #
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets
 
class DialogWidget(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(DialogWidget, self).__init__(parent=parent)
        self.setObjectName('MY_CUSTOM_UI1')
        self.setWindowTitle('TEST')
        layout = QtWidgets.QGridLayout()
        button = QtWidgets.QPushButton("HELP")
        layout.addWidget(button)
        self.setLayout(layout)


widget = DialogWidget()
widget.show(dockable=True, floating=True)






# Add QPushButton to Maya Shelf #
from PySide           import QtCore, QtGui
from PySide.QtUiTools import QUiLoader 
from maya import OpenMayaUI as omUI
import shiboken
import pymel.core as pm
  
def getMayaShelfObj(shelfObj):
    ptr = omUI.MQtUtil.findLayout(shelfObj)
    if ptr is not None:
        return shiboken.wrapInstance(long(ptr), QtGui.QWidget)

def testEvent():
    print "hello world!!"
    
def push():
    pos = QtGui.QCursor.pos()
    Menu.popup(pos) 

shelfParent = pm.MelGlobals()['gShelfTopLevel']

shelfName = "qtTest"
if pm.shelfLayout(shelfName,exists=True) == True:
    shelf       = pm.shelfLayout(shelfName,e=True)
else:
    shelf       = pm.shelfLayout(shelfName,p=shelfParent)

widget      = getMayaShelfObj(shelf.name())

LO          = widget.layout()
Btn         = QtGui.QPushButton("MENU")
 
LO.addWidget(Btn)
 
exitAction = QtGui.QAction('TestAction',Btn,triggered=testEvent)
Menu       = QtGui.QMenu()
Menu.addAction(exitAction)

Btn.clicked.connect(push)




from PySide import QtCore, QtGui

import maya.cmds as cmds
import maya.OpenMayaUI as mui

import shiboken

class MyDialog(QtGui.QDialog):

	def __init__(self, parent, **kwargs):
		super(MyDialog, self).__init__(parent, **kwargs)
		print 'here'
		self.setObjectName("MyWindow")
		self.resize(800, 600)
		self.setWindowTitle("PySide ModelPanel Test")

		self.verticalLayout = QtGui.QVBoxLayout(self)
		self.verticalLayout.setContentsMargins(0,0,0,0)

		# need to set a name so it can be referenced by maya node path
		self.verticalLayout.setObjectName("mainLayout")

		# First use shiboken to unwrap the layout into a pointer
		# Then get the full path to the UI in maya as a string
		layout = mui.MQtUtil.fullName(long(shiboken.getCppPointer(self.verticalLayout)[0]))
		print 'layout', layout
		#layout = mui.MQtUtil.fullName(long(shiboken.unwrapInstance(self.verticalLayout)))
		cmds.setParent(layout)

		paneLayoutName = cmds.paneLayout()

		# Find a pointer to the paneLayout that we just created
		ptr = mui.MQtUtil.findControl(paneLayoutName)

		# Wrap the pointer into a python QObject
		self.paneLayout = shiboken.wrapInstance(long(ptr), QtGui.QWidget)

		self.cameraName = cmds.camera()[0]
		self.modelPanelName = cmds.modelPanel("customModelPanel", label="ModelPanel Test", cam=self.cameraName)

		# Find a pointer to the modelPanel that we just created
		ptr = mui.MQtUtil.findControl(self.modelPanelName)

		# Wrap the pointer into a python QObject
		self.modelPanel = shiboken.wrapInstance(long(ptr), QtGui.QWidget)

		# add our QObject reference to the paneLayout to our layout
		self.verticalLayout.addWidget(self.paneLayout)

	def showEvent(self, event):
		super(MyDialog, self).showEvent(event)

		# maya can lag in how it repaints UI. Force it to repaint
		# when we show the window.
		self.modelPanel.repaint()

def show():
	# get a pointer to the maya main window
	ptr = mui.MQtUtil.mainWindow()
	# use shiboken to wrap the pointer into a QObject
	win = shiboken.wrapInstance(long(ptr), QtGui.QWidget)
	d = MyDialog(win)
	d.show()

	return d

try:
	dialog.deleteLater()
except:
	pass
dialog = show()
