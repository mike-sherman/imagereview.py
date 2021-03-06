# imagereview.py

**imagereview.py** is a program for reviewing and managing motion capture images saved by [motioneye](https://github.com/ccrisan/motioneye)
 / [motioneyeOS](https://github.com/ccrisan/motioneyeos).

The program allows you to browse thru folders of images, mark images for deletion, and delete marked images.
The images are on the local computer.

My usage is to have [motioneye](https://github.com/ccrisan/motioneye) upload the images to a cloud file storage, including sub folders, and then the cloud storage is synced to my computer to be reviewed. Images deleted from the local copy are deleted from the cloud.

The images reviewd are tracked in in a json file.

## Revision 9 adds 
* A button to create an animation of any days images with controlable framerate.
* A progress bar for functions that can take some time.
* Doesn't crash if the log file doesn't exist.

## Requirements
* Python 3
* PyQt5
* Json


## Instalation
Enter values for the following in the code:
* "/path/to/imagereview.ui"           - where the imagereview.ui file is located
* base_dir = '/path/to/images/'       - where the local folders of images are located
* prog_dir = '/path/to/imagereview/'  - where the program data file is stored
