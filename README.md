# imagereview.py

**imagereview.py** is a program for reviewing and managing motion capture images saved by [motioneye](https://github.com/ccrisan/motioneye)
 / [motioneyeOS](https://github.com/ccrisan/motioneyeos).

The program is ment to run on a Windows or Linux  computer with access to the images captured by motion. It allows you to browse thru folders of images, mark images for deletion, and delete marked images.

My use case is to have [motioneye](https://github.com/ccrisan/motioneye) upload the images to a cloud file storage, including sub folders, and then the cloud storage is synced to my computer to be reviewed. Images deleted from the local copy are deleted from the cloud.

The images reviewd are tracked in in a json file.

## Requirements
* Python 3
* PyQt5
* Json


## Installation
Enter values for the following in the code:
* "/path/to/imagereview.ui"           - where the imagereview.ui file is located
* base_dir = '/path/to/images/'       - where the local folders of images are located
* prog_dir = '/path/to/imagereview/'  - where the program data file is stored

![Screenshot](https://raw.githubusercontent.com/mike-sherman/imagereview.py/master/image%20review.png?raw=true)
