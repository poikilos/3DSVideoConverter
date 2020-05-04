#!/usr/bin/env python
"""
Convert side-by-side stereoscopic videos to 3DS stereoscopic video format!

The Poikilos fork adds cross-platform support and reduces dependencies.
"""
from __future__ import print_function

import sys
import os
import subprocess
import re
import string
import time
import math
import shutil
import argparse
from mydialog import MyDialog

gVersionStr = "Version 0.1 (Poikilos' 2020 tkinter fork)"
testPath = ("/home/owner/Videos/YouTube-archive/3D/3D HD Relaxing Video"
            " - Magic Forest  - yt3d Youtube 3D-GMkqdhRGkmI.mp4")

try:
    input = raw_input
except NameError:
    pass

try:
    import Tkinter as tk
    import tkFont
    import ttk
    import tkMessageBox as messagebox
except ImportError:  # Python 3
    import tkinter as tk
    import tkinter.font as tkFont
    import tkinter.ttk as ttk
    from tkinter import messagebox

root = None
ap = None


def init_args():
    global ap
    ap = argparse.ArgumentParser(
        description=('Convert side-by-side stereoscopic videos to'
                     ' 3DS stereoscopic video format!')
    )
    # derived from upstream 3DSVideoConverter.xaml
    # - formerly title case
    # - sbs was formerly SideBySideCheckBox
    # - input was formerly InputFile
    ap.add_argument('--quality', type=str,
                    choices=('VeryHigh', 'High', 'Standard', 'Low'),
                    default='Standard',
                    help=('The quality of video (2, 4, 6, 8)'))
    ap.add_argument('--sbs', action='store_const', const=True,
                    default=True,
                    help=('SBS (Side By Side)'))
    ap.add_argument('--input', type=str,  default=None,
                    help=('Original video'))
    print("Arguments: '''{}'''".format(ap.format_help()))
    # print(dir(ap))
    # print("argument_default: {}".format(ap.argument_default()))
    # ^ TypeError: 'NoneType' object is not callable
    # print("format_usage: {}".format(ap.format_usage()))
    # ^ usage: 3DSVideoConverter.py
    #   [-h] [--quality {VeryHigh,High,Standard,Low}]
    #                       [--sbs] [--input INPUT]
    print("get_default: {}".format(ap.get_default("quality")))
    # ^ "Standard"
    print("usage: {}".format(ap.usage))
    # print("_optionals: {}".format(dir(ap._optionals)))

def parse_args():
    args = ap.parse_args()
    return vars(args)


# derived from upstream 3DSVideoConverter.xaml:
option_descriptions = {}
option_values = {}
option_values["quality"] = {}
option_values["quality"]["VeryHigh"] = 2
option_values["quality"]["High"] = 4
option_values["quality"]["Standard"] = 6
option_values["quality"]["Low"] = 8


class AboutBox(MyDialog):
    def __init__(self, parent):
        # wpf.LoadComponent(self, 'WizardDialog.xaml')
        f = open('license.txt')
        opl = f.read()
        f.close()
        # r = gVersionStr + '\n'
        # r += ('This software is created by JunHyeok Heo'
        #       ' (junek69@gmail.com)'
        #       ' and Jake "Poikilos" Gustafson\n')
        # r += ('under MIT License.\n')
        MyDialog.__init__(self, parent, opl, btnNames=["Close"],
                          args=None)

    def buttonClick(self, s, e):
        self.Close()


class BackGroundTask():
    def __init__(self, doFunc, param, doneFunc, progressFunc):
        self.doFunc = doFunc
        self.param = param
        self.doneFunc = doneFunc
        thread = BackgroundWorker()
        self.thread = thread
        if progressFunc:
            thread.WorkerReportsProgress = True
            thread.ProgressChanged += progressFunc
        else:
            thread.WorkerReportsProgress = False
        thread.WorkerSupportsCancellation = False
        thread.DoWork += DoWorkEventHandler(self.doWork)
        thread.RunWorkerAsync()
        self.done = False

    def doWork(self, sender, event):
        # print("BackGroundTaskRun~!")
        self.result = self.doFunc(sender, event, self.param)
        if self.doneFunc is not None:
            self.doneFunc(sender, event, self.param)
        self.done = True

    def getResult(self):
        return self.result

    def isDone(self):
        return self.done


class Progress3D(MyDialog):
    def __init__(self, parent):
        # derived from upstream Progress3D.xaml:
        MyDialog.__init__(self, parent, '',
                          title="Convert to 3DS Progress",
                          btnNames=["Cancel"],
                          args={"Progressbar left": 100.0,
                                "Progressbar right": 100.0,
                                "Progressbar final": 100.0},
                          handlers={"Cancel": self.closeHandle})

    def show(self):
        self.ShowDialog()

    def closeHandle(self):
        while True:
            allDone = True
            if self.parent.leftPipe is not None:
                self.parent.leftPipeCancel = True
                allDone = False
            if self.parent.rightPipe is not None:
                self.parent.rightPipeCancel = True
                allDone = False
            if self.parent.finalPipe is not None:
                self.parent.finalPipeCancel = True
                allDone = False
            if allDone:
                break
            time.sleep(0.1)
            print('wait done')
        print('canceled')

    def cancel(self):
        print('Progress3D cancel')
        self.top.destroy()

    def closeByOthers(self):
        print('Progress3D closeByOthers')
        self.top.destroy()


def findInfo(info):
    fileName = info['input']
    command = ['ffprobe', '-i', fileName]
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    # stdout, stderr = proc.communicate()
    # print("stderr : %s" % stderr)
    lines = ""
    while p.poll() is None:
        lines += p.stderr.read()
    # matchObj = re.search("^*Duration:\s*([^,]+),.+bitrate:"
    #                      "\s*([0-9]+\s*.+/s).*\n.+Video:"
    #                      "[^,]+,\s*[^,]+,\s*([0-9]+x[0-9]+)[^,]*,",
    #                      lines)
    matchObj = re.search("^*Duration:\\s*([^,]+),.+bitrate:"
                         "\\s*([0-9]+\\s*.+/s).*\n.+Video:"
                         ".*[\\s]+([0-9]+x[0-9]+)[^,]*,", lines)
    if matchObj is None:
        print("No Match!!!")
        return False
    duration = matchObj.group(1)
    bitrate = matchObj.group(2)
    resolution = matchObj.group(3)
    matchObj = re.search('([0-9]+):([0-9]+):([0-9]+).([0-9]+)',
                         duration)
    if matchObj is None:
        return False
    info['seconds'] = (string.atoi(matchObj.group(1)) * 3600
                       + string.atoi(matchObj.group(2)) * 60
                       + string.atoi(matchObj.group(3)))
    matchObj = re.search('([0-9]+)x([0-9]+)', resolution)
    if matchObj is None:
        return False
    info['width'] = string.atoi(matchObj.group(1))
    info['height'] = string.atoi(matchObj.group(2))
    matchObj = re.search('([0-9]+)\\s*[mM]', bitrate)
    if matchObj is None:
        matchObj = re.search('([0-9]+)\\s*[kK]', bitrate)
        if matchObj is None:
            return False
        else:
            info['bitrate'] = matchObj.group(1) + 'K'
    else:
        info['bitrate'] = matchObj.group(1) + 'M'
    return True


def findFileName(info):
    fileName = info['input']
    # newStr = fileName.replace('\\','/')
    # print(newStr)
    # matchObj = re.search("([^/]+)\.",newStr)
    # if matchObj is None :
    #     return False
    # print(matchObj.group(1))
    head, tail = os.path.split(fileName)
    fnameWithoutExt = os.path.splitext(tail)[0]
    if fnameWithoutExt == "":
        return False
    print(fnameWithoutExt)
    info['outfolder'] = fnameWithoutExt
    # ^ Purposely use filename as directory.
    return True


def seconds2Str(seconds):
    hour = seconds/3600
    minute = (seconds % 3600) / 60
    second = seconds % 60
    return "%02d:%02d:%02d" % (hour, minute, second)


class MyWindow(ttk.Frame):
    def __init__(self, parent, ap):
        """
        Sequential arguments:
        parent -- the Tk root (should already be set to `tk.Tk()`)
        ap -- an argparser instance to use as a basis for GUI elements.
        """

        # self.filename_v = tk.StringVar()
        ttk.Frame.__init__(self, parent)
        self.pack(fill=tk.BOTH, expand=True)
        row = 0
        wide_width = 30

        # input_l = ttk.Label(self, text="Original video:")
        # input_l.grid(column=0, row=row, sticky=tk.E)
        # self.filename_entry = ttk.Entry(
        #     self,
        #     width=25,
        #     textvariable=self.info["input"]
        # )
        # self.filename_entry.grid(column=1, columnspan=3, row=row,
        #                          sticky=tk.W)
        # row += 1
        self._labels = {}
        self._entries = {}
        self._vars = {}
        options = parse_args()
        for k, v in options.items():
            if False: #(v is True) or (v is False):
                # Checkbutton(self, ...
                self._entries[k] = ttk.Checkbutton(text=k,
                                                   variable=self._vars)
                self._entries[k].grid(column=0, columnspan=4, row=row,
                                      sticky=tk.W)
            else:
                self._vars[k] = tk.StringVar()
                self._labels[k] = ttk.Label(self, text="{}:".format(k))
                self._labels[k].grid(column=0, row=row, sticky=tk.E)
                self._entries[k] = ttk.Entry(
                    self,
                    width=25,
                    textvariable=self._vars[k]
                )
                if v is not None:
                    self._vars[k].set(v)
                self._entries[k].grid(column=1, columnspan=3, row=row,
                                      sticky=tk.W)
            print("added {}:{}".format(k, v))
            row += 1

        self.convert_button = ttk.Button(self, text="Convert",
                                         command=self.convertHandler)
        self.convert_button.grid(column=1, row=row, sticky=tk.E)
        self.about_button = ttk.Button(self, text="About",
                                       command=self.aboutHandler)
        self.about_button.grid(column=2, row=row, sticky=tk.W)
        row += 1

        self.info = {}
        self.initPipeVars()

    def updateParamsFromWindow(self):
        for k, v in self._vars.items():
            self.info[k] = self._vars[k].get().strip()
        findFileName(self.info)
        print("* got info: {}".format(self.info))

    def initFinalPipeVars(self):
        self.finalPipe = None
        self.finalPercent = 0.0
        self.finalPipeCode = 0
        self.finalPipeCancel = False

    def initPipeVars(self):
        self.leftPipe = None
        self.leftPercent = 0.0
        self.leftPipeCode = 0
        self.leftPipeCancel = False
        self.rightPipe = None
        self.rightPercent = 0.0
        self.rightPipeCode = 0
        self.rightPipeCancel = False
        self.initFinalPipeVars()

    # def dropHandler(self, s, e):
    #     pass
    #     if e.Data.GetDataPresent(DataFormats.FileDrop):
    #         files = e.Data.GetData(DataFormats.FileDrop)
    #         self.InputFile.Items.Clear()
    #         self.fileInfo.Text = ""
    #         self.InputFile.Items.Add(files[0])
    #         self.info = {}
    #         self.info['input'] = files[0]
    #         if findFileName(self.info) and findInfo(self.info):
    #             s = "Duration :\t" + seconds2Str(self.info['seconds'])
    #             s += ("\nResolution :\t%dx%d"
    #                   % (self.info['width'], self.info['height']))
    #             s += "\nBitrate :\t\t" + self.info['bitrate']
    #             s += "\nOutput Folder :\t" + self.info['outfolder']
    #             self.fileInfo.Text = s
    #         pass

    def convertHandler(self):
        self.updateParamsFromWindow()
        filename = self.info.get('input')
        if (filename is None) or (filename.strip() == ""):
            messagebox.showerror("Error",
                                 'There is no file to be converted.')
            return
        outfolder = self.info.get('outfolder')
        if (outfolder is None) or (outfolder.strip() == ""):
            messagebox.showerror("Error",
                                 'The output folder is not set.')
            return
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)
        quality = self.info.get('quality')
        vq = 6
        if quality.find('VeryHigh') >= 0:
            vq = 2
        elif quality.find('High') >= 0:
            vq = 4
        elif quality.find('Low') >= 0:
            vq = 8
        print("Quality %d" % vq)
        self.initPipeVars()
        self.p3d = Progress3D(self)
        if self.SideBySideCheckBox.IsChecked:
            leftParams = ['left', vq]
            lb = BackGroundTask(self.convertSideBySideStep1,
                                leftParams,  self.progressLeftDone,
                                self.progressLeftChanged)
            rightParams = ['right', vq]
            rb = BackGroundTask(self.convertSideBySideStep1,
                                rightParams, self.progressRightDone,
                                self.progressRightChanged)
            while (self.leftPipe is None) or (self.rightPipe is None):
                time.sleep(0.5)
            finalParams = [vq, True]
            fb = BackGroundTask(self.convertSideBySideStep2,
                                finalParams, self.progressFinalDone,
                                self.progressFinalChanged)
        else:
            finalParams = [vq, False]
            fb = BackGroundTask(self.convertSideBySideStep2,
                                finalParams, self.progressFinalDone,
                                self.progressFinalChanged)
        self.p3d.show()
        # wait until background tasks stop
        if self.SideBySideCheckBox.IsChecked:
            while not lb.isDone() or not lb.isDone():
                time.sleep(0.2)
        while not fb.isDone():
            time.sleep(0.2)
        print('Done : %d' % self.finalPipeCode)
        if self.finalPipeCode != 0:
            print('Try to remove outfolder!!!')
            shutil.rmtree(outfolder)
            print('Removed outfolder!!!')
            if self.finalPipeCancel or \
                    (self.leftPipeCancel and self.rightPipeCancel):
                pass
            else:
                messagebox.showerror("Error", 'Conversion failed!')
        elif self.SideBySideCheckBox.IsChecked:
            os.remove(os.path.join(outfolder, 'left.avi'))
            os.remove(os.path.join(outfolder, 'right.avi'))

    def aboutHandler(self):
        AboutBox(self)

    def convertSideBySideStep1(self, sender, event, params):
        leftOrRight = params[0]
        vq = params[1]
        # command = ['ffmpeg', '-y', '-i',
        #            self.info['input'],
        #            '-b:v', self.info['bitrate'],
        #            '-vf',
        #            ('crop='
        #             + ('%s:%s:%s:0' % (self.info['width']/2,
        #                                self.info['height'],
        #                                self.info['width']/2))),
        #            '-aspect', '2:1',
        #            os.path.join(self.info['outfolder'], 'right.avi')]
        crops = {}
        crops['left'] = '480:240:0:0'
        crops['right'] = '480:240:480:0'
        command = ['ffmpeg', '-y', '-i', self.info['input'],
                   '-vcodec', 'mjpeg', '-q:v', '%d' % vq, '-r', '20',
                   '-vf',
                   ('\"scale=960:240,'
                    + 'crop=' + crops[leftOrRight] + '\"'),
                   '-aspect', '2:1',
                   '-acodec', 'adpcm_ima_wav', '-ac', '2',
                   os.path.join(self.info['outfolder'],
                                leftOrRight+'.avi')]
        print(' '.join(command))
        p = subprocess.Popen(command, shell=True,
                             stderr=subprocess.PIPE)
        if leftOrRight == 'left':
            self.leftPipe = p
        else:
            self.rightPipe = p
        line = ""
        while p.poll() is None:
            if leftOrRight == 'left' and self.leftPipeCancel:
                p.kill()
                print('request the left pipe to stop')
            if leftOrRight == 'right' and self.rightPipeCancel:
                p.kill()
                print('request the right pipe to stop')
            a = p.stderr.read(1)
            if a != '\r' and a != '\n':
                line += a
                continue
            matchObj = re.search('time=([0-9]+):([0-9]+):([0-9]+)\\.', line)
            # print(matchObj)
            if matchObj is not None:
                seconds = string.atoi(matchObj.group(1))*3600 \
                        + string.atoi(matchObj.group(2))*60 \
                        + string.atoi(matchObj.group(3))
                percent = (seconds*100)/self.info['seconds']
                if leftOrRight == 'left':
                    self.leftPercent = percent
                    print("left %d" % percent)
                else:
                    self.rightPercent = percent
                    print("right %d" % percent)
                sender.ReportProgress(percent)
            line = ""
        if leftOrRight == 'left':
            self.leftPipeCode = p.returncode
        else:
            self.rightPipeCode = p.returncode
        print("%s returncode = %d" % (leftOrRight, p.returncode))
        time.sleep(1)
        return True

    def progressLeftChanged(self, s, e):
        self.p3d.leftBar.Value = e.ProgressPercentage

    def progressRightChanged(self, s, e):
        self.p3d.rightBar.Value = e.ProgressPercentage

    def progressLeftDone(self, s, e, params):
        print('left done')
        self.leftPipe = None
        if self.leftPipeCode == 0:
            s.ReportProgress(100)
        else:  # error
            while self.rightPipe is not None:
                self.rightPipeCancel = True

    def progressRightDone(self, s, e, params):
        print('right done')
        self.rightPipe = None
        if self.rightPipeCode == 0:
            s.ReportProgress(100)
        else:  # error
            while self.leftPipe is not None:
                self.leftPipeCancel = True

    def convertSideBySideStep2(self, sender, event, params):
        while True:
            time.sleep(0.5)
            if (self.leftPipe is None) and (self.rightPipe is None):
                break
        if (self.rightPipeCode != 0) or (self.leftPipeCode != 0):
            # ^ error or canceled
            self.finalPipeCode = 1
            print("final canceled %d" % self.finalPipeCode)
            return False
        leftFile = os.path.join(self.info['outfolder'], 'left.avi')
        rightFile = os.path.join(self.info['outfolder'], 'right.avi')
        vq = params[0]
        sbs = params[1]
        # add the created time for AVI
        # ffmpeg -i old.avi -metadata ICRD="2013-05-02 22:01:04"
        #   -c copy new.avi
        now = time.localtime()
        recordedTime = ("%04d-%02d-%02d %02d:%02d:%02d"
                        % (now.tm_year, now.tm_mon, now.tm_mday,
                           now.tm_hour, now.tm_min, now.tm_sec))
        # command = ['ffmpeg', '-y', '-i', leftFile, '-i ', rightFile,
        #            '-vcodec', 'mjpeg', '-s', '400x240', '-r', '24',
        #            '-qscale', '1', '-acodec', 'adpcm_ima_wav', '-ac',
        #            '2', '-map', '0:0', '-map', '0:1', '-map', '1:0',
        #            outFile]
        clipOpt = ""
        outNum = math.ceil(self.info['seconds'] / 600.0)
        outCount = 0
        command = None
        while outCount < outNum:
            # Split the file into 10 minute clips.
            outFile = os.path.join(self.info['outfolder'],
                                   ('NIN_%04d.AVI' % (outCount+1)))
            if self.info['seconds'] > 600:
                hour = (outCount * 600) / 3600
                minute = ((outCount * 600) % 3600) / 60
                clipOpt = ("-ss %02d:%02d:00 -t 00:10:00"
                           % (hour, minute))
            if sbs:
                command = ['ffmpeg', '-y', '-i', leftFile, '-i',
                           rightFile, clipOpt,
                           '-vcodec', 'mjpeg', '-q:v', '%d' % vq,
                           '-r', '20 ',
                           '-acodec', 'adpcm_ima_wav -ac', '2',
                           '-metadata', 'ICRD=\"' + recordedTime + '\"',
                           '-map', '0:0', '-map', '0:1', '-map', '1:0',
                           outFile]
            else:
                command = ['ffmpeg', '-y', '-i',
                           self.info['input'],
                           clipOpt,
                           '-vcodec', 'mjpeg', '-q:v', '%d' % vq,
                           '-r', '20',
                           '-vf scale=480:240',
                           '-aspect 2:1',
                           '-acodec', 'adpcm_ima_wav', '-ac', '2',
                           '-metadata', 'ICRD=\"' + recordedTime + '\"',
                           outFile]
            print(' '.join(command))
            p = subprocess.Popen(command, shell=True,
                                 stderr=subprocess.PIPE)
            self.finalPipe = p
            line = ""
            while p.poll() is None:
                if self.finalPipeCancel:
                    p.kill()
                    print('request the final pipe to stop')
                a = p.stderr.read(1)
                if a != '\r' and a != '\n':
                    line += a
                    continue
                print(line)
                matchObj = re.search(
                    'time=([0-9]+):([0-9]+):([0-9]+)\\.',
                    line
                )
                # print(matchObj)
                if matchObj is None:
                    seconds = string.atoi(matchObj.group(1))*3600 \
                            + string.atoi(matchObj.group(2))*60 \
                            + string.atoi(matchObj.group(3))
                    percent = ((outCount*600*100+seconds*100)
                               / self.info['seconds'])
                    self.finalPercent = percent
                    print("final %d" % percent)
                    sender.ReportProgress(percent)
                line = ""
            if p.returncode != 0:
                self.finalPipeCode = p.returncode
                print("final returncode = %d" % (p.returncode))
                return False
            outCount += 1
        print("final returncode = %d" % (p.returncode))
        return True

    def progressFinalChanged(self, s, e):
        self.p3d.finalBar.Value = e.ProgressPercentage

    def progressFinalDone(self, s, e, params):
        self.finalPipe = None
        if self.finalPipeCode == 0:
            s.ReportProgress(100)
        print('final done %d' % self.finalPipeCode)
        self.p3d.closeByOthers()


def main():
    global root
    root = tk.Tk()
    root.title("3DS Video Converter (Poikilos' Fork)")
    init_args()
    MyWindow(root, ap)
    root.mainloop()


if __name__ == "__main__":
    main()
