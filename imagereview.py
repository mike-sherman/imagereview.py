# image review script   Nov 2019
# m.e.sherman
# to make it quicker to review and delete images captured by my security cameras
#
# the starting point was
#   https://stackoverflow.com/questions/44750439/using-simple-pyqt-ui-to-choose-directory-path-crushing
#
# imagereview6 released
# imagereview7 - select folder always starts at base dir
# imagereview8 - add animate button to make a video of the current folder
# imagereview9 - add progress bar

import sys
import os
import json
import shutil
import fnmatch
import subprocess
import re

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5 import uic, QtGui


Ui_MainWindow, QtBaseClass = uic.loadUiType("/home/mike/Dropbox/src/python/imagereview/imagereview.ui")

            
            
class MyApp(QMainWindow, Ui_MainWindow):
    #
    # class scope variables
    #
    # where the images are
    base_dir = '/path/to/images/'           # where image folders are
    
    # where the program and datafile are
    prog_dir = '/path/to/imagereview/'      # where the program is
    temp_dir = prog_dir + 'temp/'           # used for animations
    
    # the name of the log file
    log_file = prog_dir + "data.json"      # database of images
    input_dir = ''                          # the current driectory we are tagging
    prev_dir = ''                           # the previous direcotry in the directory list
    next_dir = ''                           # the next direcotry in the directory list
    filekeys = ['index', 'name', 'status']  # our data and log file structure
    files = []                              # files in the current directory
    number_of_images = 0                    # number of files in the current directory
    defaultstatus = 'keep'                  # default status of files in a new directory
    currentselected = 0                     # index into displaed file list widget
    autoenabled = 0;                        # someday we will auto step thru the files...
    sleeptime = 0.5                         # how fast we will someday auto step
    data = []                               # local log data
    dataupdate = []                         # list of to-be-removed
    changes = 0                             # have we changed anything?
    fps = 15                                # animation frames per second
    percentstep = 1
    percentdone = 0
    
    # class init
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        logo_src = "appLogo.png"
        self.setWindowIcon(QtGui.QIcon(logo_src))
        self.ui.folderLabel.setText(self.base_dir)
        self.ui.fpsLabel.setText(str(self.fps) + " fps")
        self.ui.progress.setValue(self.percentdone)
        
        self.ui.folderButton.clicked.connect(self.choose_directory)
        self.ui.folderButton.setToolTip('Choose directory')
        
        # read the log file
        with open(self.log_file, 'r') as filelist:
            self.data = json.load(filelist)
        
        # Buttons
        self.ui.nextButton.clicked.connect(self.nextimage)
        self.ui.prevButton.clicked.connect(self.previmage)
        self.ui.keepButton.clicked.connect(self.keepimage)
        self.ui.deleteButton.clicked.connect(self.delete)
        self.ui.keepALLbutton.clicked.connect(self.toggleall)
        self.ui.nextfolderButton.clicked.connect(self.nextfolder)
        self.ui.prevfolderButton.clicked.connect(self.prevfolder)
        self.ui.tognextButton.clicked.connect(self.keepnextimage)
        self.ui.filelistWidget.itemClicked.connect(self.itemclicked)
        self.ui.animate.clicked.connect(self.animate)
        self.ui.fpsSlider.valueChanged.connect(self.set_framerate)
        
#        self.ui.testButton.clicked.connect(self.testProgress)
        
        # File menu
        self.ui.actionselect_folder.triggered.connect(self.choose_directory)
        
        
        
    # ------------------------------------------------------------------
    # class methods
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # set the animation frames per second
    def set_framerate(self):
        self.fps = self.ui.fpsSlider.value()
        self.ui.fpsLabel.setText(str(self.fps) + " fps")
        
    # ------------------------------------------------------------------
    # create an animation of the current days images
    #  animation is written to the current imput_dir
    def animate(self):
        filecount = len(os.listdir(self.input_dir))
        self.percentstep = 100/(filecount * 2)
        self.percentdone = 0
        
        a=1
        have_images = False
        for file in sorted(os.listdir(self.input_dir)):
            in_file = self.input_dir + file
            print(in_file)
            
            if fnmatch.fnmatch(file, '*.jpg'):
                self.percentdone = self.percentdone + self.percentstep
                self.ui.progress.setValue(self.percentdone)
                have_images = True
                out_file = self.temp_dir + str(a).zfill(4) + '.jpg'
                print(out_file)
                shutil.copy(in_file, out_file)
                a = a + 1
            
        if have_images:
            # first remove old animation
            if os.path.exists(self.input_dir + "today-" + str(self.fps) + "_fps.mp4"):
                os.remove(self.input_dir + "today-" + str(self.fps) + "_fps.mp4")
                
            command = f"ffmpeg -framerate {self.fps} -i {self.temp_dir}%04d.jpg -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p {self.input_dir}today-{self.fps}_fps.mp4"
            print(command)
            subprocess.call(command,shell=True)
            
            # clean up
            for file in os.listdir(self.temp_dir):
                if re.search('.jpg', file):
                    os.remove(os.path.join(self.temp_dir, file))
                    self.percentdone = self.percentdone + self.percentstep
                    self.ui.progress.setValue(self.percentdone)
            #os.remove(self.temp_dir + "*.jpg")
        
        #self.show_done()
        self.percentdone = 0
        self.ui.progress.setValue(self.percentdone)

    # ------------------------------------------------------------------
    # check in case the directory we are in was deleted
    def adjustinput_dir(self):
        if os.path.isdir(self.input_dir):
            self.getprevnext()
        elif os.path.isdir(self.next_dir):
            self.input_dir = self.next_dir
            self.getprevnext()
        elif os.path.isdir(self.prev_dir):
            self.input_dir = self.prev_dir
            self.getprevnext()
            
    # ------------------------------------------------------------------
    # looks up what the previous and next folders are and saves in self
    def getprevnext(self):
        folderup = self.input_dir[:len(self.input_dir)-11]          # the parent folder
        currentfolder = self.input_dir[len(self.input_dir)-11:]     # current folder
        currentfolder = currentfolder[:10]                          # current folder without trailing /
        files = sorted(os.listdir(folderup))                        # get the files in parent folder
        foundcurrent = 0
        for name in files:
            if foundcurrent == 1:
                self.next_dir = folderup + name + '/'
                break
            if name == currentfolder:
                foundcurrent = 1
            if foundcurrent != 1:
                self.prev_dir = folderup + name + '/'
            
    # ------------------------------------------------------------------
    # a file in the list box was clicked
    def itemclicked(self):
        itemtext = self.ui.filelistWidget.currentItem().text()
        itemnumber = int(itemtext[0:4]) - 1
        self.currentselected = itemnumber
        self.updatefilecount()
        self.updateimage()
        
    # ------------------------------------------------------------------
    # togglethe current image and select the next image
    def keepnextimage(self):
        self.keepimage()
        self.nextimage()
        self.updatefilecount()

    # ------------------------------------------------------------------
    # for each file in list, if status == delete, delete it and change status to deleted
    # if folder is empty, delete it
    def delete(self):
        changed = 0
        self.ui.filecount.setText('Deleting marked images...')
        self.ui.filecount.update()
        # show progress
        self.percentstep = 100/len(self.data) * 3
        
        # go thru the data/log and delete any files marked for deletion
        for item in self.data:
            # show progress
            self.percentdone = self.percentdone + self.percentstep
            self.ui.progress.setValue(self.percentdone)
            if item['status'] == 'delete':
                changed = 1
                path = item['folder']
                file = item['file']
                self.ui.filecount.setText('Deleting file: ' + file)
                self.ui.filecount.update()
                if os.path.isfile(path + file):
                    try:
                        os.remove(path + file)
                    except:
                        print("No such file.")
                # add deleted files to the delete list
                self.dataupdate.append({'folder':path,  "file":file, "status":'delete'})
                
        # go thru the delete list and remove the entries from the data/log
        # show progress
        self.percentdone = 0
        self.percentstep = 100/len(self.dataupdate)
        for item in self.dataupdate:
            thisfolder = item['folder']
            self.ui.filecount.setText('Checking folder: ' + thisfolder)
            self.ui.filecount.update()
            # show progress
            self.percentdone = self.percentdone + self.percentstep
            self.ui.progress.setValue(self.percentdone)
            # check the folder
            if os.path.isdir(thisfolder):
                list = os.listdir(thisfolder)
                # if the folder is empty, delete it
                if len(list) == 0:
                    changed = 1
                    self.ui.filecount.setText('Deleting folder: ' + item['folder'])
                    self.ui.filecount.update()
                    os.rmdir(thisfolder)
        # if the data changed, update the file
        if changed == 1:
            self.ui.filecount.setText('Updating data file...')
            self.ui.filecount.update()
            # show progress
            self.percentdone = 0
            self.percentstep = 100/len(self.dataupdate)
            for updates in self.dataupdate:
                # show progress
                self.percentdone = self.percentdone + self.percentstep
                self.ui.progress.setValue(self.percentdone)
                try:
                    self.data.remove({'folder':updates['folder'],  'file':updates['file'],  'status':updates['status']})
                except:
                    print("No such file in list.")
            self.savedatafile()
        self.changes = 0
        self.ui.filecount.setText('Done.')
        self.adjustinput_dir()
        self.openfolder()
        # show progress
        self.percentdone = 0
        self.ui.progress.setValue(self.percentdone)
            
    # ------------------------------------------------------------------
    # move to the previous folder in the parent directory
    def prevfolder(self):
        self.input_dir = self.prev_dir
        self.getprevnext()
        self.openfolder()
        
    # ------------------------------------------------------------------
    # move to the next folder in the parent direcotry
    def nextfolder(self):
        self.input_dir = self.next_dir
        self.getprevnext()
        self.openfolder()
    
    # ------------------------------------------------------------------
    # toggle all files in the current folder
    def toggleall(self):
        for selectedfile in self.files:
            if selectedfile[2] == 'keep':
                prevstat = 'keep'
                selectedfile[2] = 'delete'
            elif selectedfile[2] == 'delete':
                prevstat = 'delete'
                selectedfile[2] = 'keep'
            self.data.remove({'folder':self.input_dir,  "file":selectedfile[1], "status":prevstat})
            self.data.append({'folder':self.input_dir,  "file":selectedfile[1], "status":selectedfile[2]})
        self.updatelist()
        self.savedatafile()
        self.changes = 1

    
    # ------------------------------------------------------------------
    # toggle the current image
    def keepimage(self):
        if self.files[self.currentselected][2] == 'keep':
            prevstat = 'keep'
            self.files[self.currentselected][2] = 'delete'
        elif self.files[self.currentselected][2] == 'delete':
            prevstat = 'delete'
            self.files[self.currentselected][2] = 'keep'
        # update the displayed list
        self.updatelist()
        # update the data file
        self.data.remove({'folder':self.input_dir, "file":self.files[self.currentselected][1], "status":prevstat})
        self.data.append({'folder':self.input_dir, "file":self.files[self.currentselected][1], "status":self.files[self.currentselected][2]})
        self.savedatafile()
        self.changes = 1
        
    # ------------------------------------------------------------------
    # move to the next image without changing state of the current image
    def nextimage(self):
        if  self.currentselected +1 < self.number_of_images :
            self.currentselected = self.currentselected + 1
            self.updatelist()
            self.updateimage()
            self.updatefilecount()
            
    # ------------------------------------------------------------------
    # move to the previous image without changing state of the current image
    def previmage(self):
        if  self.currentselected - 1 > -1 :
            self.currentselected = self.currentselected - 1
            self.updatelist()
            self.updateimage()
            self.updatefilecount()

    # ------------------------------------------------------------------
    # open a dialog to select a directory
    def choose_directory(self):
        search_dir = self.base_dir
        newdir = QFileDialog.getExistingDirectory(None, 'Select a folder:', search_dir)
        if newdir != '':
            self.input_dir = newdir
        self.input_dir = self.input_dir + '/'
        self.getprevnext()
        self.openfolder()
        
    # ------------------------------------------------------------------
    # open the directory that was selected
    def openfolder(self):
        if not os.path.isdir(self.input_dir):
            self.choose_directory()
        self.ui.folderLabel.setText(self.input_dir)
        count = 0
        self.files.clear()
        self.clearlist()
        self.ui.filelistWidget.clear()
        self.ui.filecount.setText('0   image files')
        self.currentselected = 0;
        list = os.listdir(self.input_dir)
        if len(list) == 0:
            self.ui.filelistWidget.addItem("Empty Folder")
        else:
            self.percentstep = 100/len(os.listdir(self.input_dir))
            for filename in sorted(os.listdir(self.input_dir)):
                status = self.defaultstatus
                newfile = 1
                # show progress
                self.percentdone = self.percentdone + self.percentstep
                self.ui.progress.setValue(self.percentdone)
                if ('.jpg' in filename):
                    for item in self.data:
                        if self.input_dir == item["folder"]:
                            if filename == item["file"]:
                                newfile = 0
                                status = item["status"]
                    if newfile == 1:
                        self.data.append({'folder':self.input_dir,  "file":filename, "status":self.defaultstatus})
                        self.savedatafile()
                    self.files.append([count, filename, status])
                    count = count + 1
                    self.number_of_images = count
                                    
            self.updatelist()
            if self.number_of_images > 0:
                self.updatefilecount()
                self.updateimage()
                
            self.percentdone = 0
            self.ui.progress.setValue(self.percentdone)
            
    # ------------------------------------------------------------------
    # update the display of current image number and cound of images in the selected folder
    def updatefilecount(self):
        countstring = str(self.currentselected + 1) + ' of ' + str(self.number_of_images) + " images"
        self.ui.filecount.setText(countstring)
            
    # ------------------------------------------------------------------
    # write the log file from the current data[]
    def savedatafile(self):
        with open(self.log_file, 'w') as file:
            json.dump(self.data,  file)
            
    # ------------------------------------------------------------------
    # display the current image
    def updateimage(self):
        pixmap = QPixmap(self.input_dir + self.files[self.currentselected][1])
        self.ui.imagelabel.setPixmap(pixmap)
        
    # ------------------------------------------------------------------
    # update the file list box
    def updatelist(self):
        self.clearlist()
        for itemindex in range(len(self.files)):
            ourindex = self.files[itemindex][0]
            ourname = self.files[itemindex][1]
            ourstatus = self.files[itemindex][2]
            if ourindex < 9:
               countstring = '   ' + str(ourindex + 1)
            elif ourindex < 99:
               countstring = '  ' + str(ourindex + 1)
            elif ourindex < 999:
                countstring = ' ' + str(ourindex + 1)
            else:
                countstring = str(ourindex + 1)
            listitemstring = countstring + '      ' + ourname + '      ' + ourstatus
            self.ui.filelistWidget.addItem(listitemstring)
        self.ui.filelistWidget.setCurrentRow(self.currentselected)

    # ------------------------------------------------------------------
    # clear the file list box
    def clearlist(self):
        while self.number_of_images > 0:
            listItems = self.ui.filelistWidget.selectedItems()
            if not listItems: return        
            for item in listItems:
               self.ui.filelistWidget.takeItem(self.ui.filelistWidget.row(item))

# ------------------------------------------------------------------
# ------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())


