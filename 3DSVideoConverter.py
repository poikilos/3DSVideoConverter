import sys

gVersionStr = 'Version 0.1 2018/06/22'

import clr
clr.AddReference("IronPython.Wpf")
import wpf

clr.AddReference("StdLib")
import os
import subprocess
import shlex
import re
import string
import time
import math
import shutil

from Queue import Queue,Empty

from System import Action
from System.ComponentModel import BackgroundWorker, DoWorkEventHandler
from System.Windows import Application, Window, Media, Shapes, FontWeight, Documents, TextWrapping, Media
from System.Windows import Thickness, SizeToContent, DataFormats, HorizontalAlignment
from System.Windows import Controls

clr.AddReference("FontAwesome.WPF")
from FontAwesome.WPF import *

class AboutBox(Window) :
    def __init__(self, parent) :
        wpf.LoadComponent(self, 'WizardDialog.xaml')
        f = open('OpenSourceLicenseTerms.txt')
        opl = f.read()
        f.close()
        self.Title = "About"
        self.SizeToContent = SizeToContent.WidthAndHeight
        #self.WindowStartupLocation = WindowStartupLocation.Manual
        self.Left = parent.Left + parent.ActualWidth/4
        self.Top= parent.Top + parent.ActualHeight/4
        stack = Controls.StackPanel()
        sv = Controls.ScrollViewer()
        sv.Width = 500
        sv.Height = 300
        tb = Controls.TextBlock()
        #tb.FontSize = 16
        tb.TextWrapping = TextWrapping.Wrap
        r = Documents.Run(gVersionStr + '\n')
        r.Foreground = Media.Brushes.Blue
        tb.Inlines.Add(r)
        r = Documents.Run('This software is created by JunHyeok Heo (junek69@gmail.com)\n')
        r.Foreground = Media.Brushes.Blue
        tb.Inlines.Add(r)
        r = Documents.Run('under MIT License.\n')
        r.Foreground = Media.Brushes.Blue
        tb.Inlines.Add(r)
        tb.Inlines.Add(opl)
        sv.AddChild(tb)
        stack.AddChild(sv)
        btn = Controls.Button()
        btn.Click += self.buttonClick
        btn.Content = "Close"
        btn.Width = 70
        btn.Height = 30
        btn.Margin = Thickness(0.0, 6.0, 0.0, 12.0)
        stack.AddChild(btn)
        self.Base.AddChild(stack)
        self.ShowDialog()
    def buttonClick(self, s, e) :
        self.Close()

class BackGroundTask() :
    def __init__(self, doFunc, param, doneFunc, progressFunc) :
        self.doFunc = doFunc
        self.param = param
        self.doneFunc = doneFunc
        thread = BackgroundWorker()
        self.thread = thread
        if progressFunc :
            thread.WorkerReportsProgress = True
            thread.ProgressChanged += progressFunc
        else :
            thread.WorkerReportsProgress = False
        thread.WorkerSupportsCancellation = False
        thread.DoWork += DoWorkEventHandler(self.doWork)
        thread.RunWorkerAsync()
        self.done = False
    def doWork(self, sender, event) :
        #print "BackGroundTaskRun~!"
        self.result = self.doFunc(sender, event, self.param)
        if self.doneFunc != None :
            self.doneFunc(sender, event, self.param)
        self.done = True
    def getResult(self) :
        return self.result
    def isDone(self) :
        return self.done

class MyErrorMsgBox(Window) :
    def __init__(self, parent, msg) :
        wpf.LoadComponent(self, 'WizardDialog.xaml')
        self.Title = "Error"
        self.SizeToContent = SizeToContent.WidthAndHeight
        #self.WindowStartupLocation = WindowStartupLocation.Manual
        self.Left = parent.Left + parent.ActualWidth/4
        self.Top= parent.Top + parent.ActualHeight/4
        stack = Controls.StackPanel()
        stack.Orientation = Controls.Orientation.Horizontal
        stack.HorizontalAlignment = HorizontalAlignment.Center
        stack.Margin = Thickness(10.0, 6.0, 10.0, 6.0)
        errorImage = Controls.Image()
        errorImage.Margin = Thickness(6.0, 6.0, 0.0, 10.0)
        errorImage.Source = ImageAwesome.CreateImageSource(FontAwesomeIcon.ExclamationCircle, Media.Brushes.Red)
        errorImage.Width = 14
        errorImage.Height = 18
        stack.Children.Add(errorImage)
        label = Controls.Label()
        #label.Style = self.FindResource("ctrl")
        #label.FontSize = 16
        label.Content = msg
        label.Margin = Thickness(0.0, 6.0, 0.0, 10.0)
        stack.Children.Add(label)
        self.Base.Children.Add(stack)
        self.button = Controls.Button()
        #self.button.Style = self.FindResource("wzdbtn")
        self.button.Click += self.buttonClick
        self.button.Content = "OK"
        self.button.Width = 70
        self.button.Height = 30
        self.button.Margin = Thickness(0.0, 6.0, 0.0, 12.0)
        self.Base.Children.Add(self.button)
        self.ShowDialog()
    def buttonClick(self, s, e ) :
        self.Close()

class Progress3D(Window) :
    def __init__(self, parent) :
        wpf.LoadComponent(self, 'Progress3D.xaml')
        self.SizeToContent = SizeToContent.WidthAndHeight
        #self.WindowStartupLocation = WindowStartupLocation.Manual
        self.Left = parent.Left + parent.ActualWidth/4
        self.Top= parent.Top + parent.ActualHeight/4
        self.CancelBtn.Click += self.cancel
        self.Closed += self.closeHandle
        self.parent = parent
    def show(self) :
        self.ShowDialog()
    def closeHandle(self, s, e) :
        while True :
            allDone = True
            if self.parent.leftPipe != None :
                self.parent.leftPipeCancel = True
                allDone = False
            if self.parent.rightPipe != None :
                self.parent.rightPipeCancel = True
                allDone = False
            if self.parent.finalPipe != None :
                self.parent.finalPipeCancel = True
                allDone = False
            if allDone :
                break
            time.sleep(0.1)
            print 'wait done'
        print 'canceled'
    def cancel(self, s, e) :
        print 'Progress3D cancel'
        self.Close()
    def closeByOthers(self) :
        print 'Progress3D closeByOthers'
        self.Dispatcher.BeginInvoke(Action(self.Close))

def findInfo(info) :
    fileName = info['filename']
    command = 'FFMPEG\\\\ffprobe.exe -i ' + '\"' + fileName +'\"'
    p = subprocess.Popen(shlex.split(command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #stdout, stderr = proc.communicate()
    #print "stderr : %s" % stderr
    lines = ""
    while p.poll() is None :
        lines += p.stderr.read()
    #matchObj = re.search("^*Duration:\s*([^,]+),.+bitrate:\s*([0-9]+\s*.+/s).*\n.+Video:[^,]+,\s*[^,]+,\s*([0-9]+x[0-9]+)[^,]*,",lines)
    matchObj = re.search("^*Duration:\s*([^,]+),.+bitrate:\s*([0-9]+\s*.+/s).*\n.+Video:.*[\s]+([0-9]+x[0-9]+)[^,]*,",lines)
    if matchObj == None :
        print "No Match!!!"
        return False
    duration = matchObj.group(1)
    bitrate = matchObj.group(2)
    resolution = matchObj.group(3)
    matchObj = re.search('([0-9]+):([0-9]+):([0-9]+).([0-9]+)',duration)
    if matchObj == None :
        return False
    info['seconds'] = string.atoi(matchObj.group(1)) * 3600 + string.atoi(matchObj.group(2)) * 60 + string.atoi(matchObj.group(3))
    matchObj = re.search('([0-9]+)x([0-9]+)',resolution)
    if matchObj == None :
        return False
    info['width'] = string.atoi(matchObj.group(1))
    info['height'] = string.atoi(matchObj.group(2))
    matchObj = re.search('([0-9]+)\s*[mM]',bitrate)
    if matchObj == None :
        matchObj = re.search('([0-9]+)\s*[kK]',bitrate)
        if matchObj == None :
            return False
        else :
            info['bitrate'] = matchObj.group(1) + 'K'
    else :
        info['bitrate'] = matchObj.group(1) + 'M'
    return True

def findFileName(info) :
    fileName = info['filename']
    #newStr = fileName.replace('\\','/')
    #print newStr
    #matchObj = re.search("([^/]+)\.",newStr)
    #if matchObj == None :
    #    return False
    #print matchObj.group(1)
    head,tail = os.path.split(fileName)
    fnameWithoutExt = os.path.splitext(tail)[0]
    if fnameWithoutExt == "" :
        return False
    print fnameWithoutExt
    info['outfolder'] = fnameWithoutExt
    return True

def seconds2Str(seconds) :
    hour = seconds/3600
    minute = (seconds%3600) / 60
    second = seconds%60
    return "%02d:%02d:%02d" % (hour, minute, second)

class MyWindow(Window):
    def __init__(self):
        wpf.LoadComponent(self, '3DSVideoConverter.xaml')
        self.InputFile.Drop += self.dropHandler
        self.ConvertBtn.Click += self.convertHandler
        self.AboutBtn.Click += self.aboutHandler
        self.info = {}
        self.initPipeVars()
    def initFinalPipeVars(self) :
        self.finalPipe = None
        self.finalPercent = 0.0
        self.finalPipeCode = 0
        self.finalPipeCancel = False
    def initPipeVars(self) :
        self.leftPipe = None
        self.leftPercent = 0.0;
        self.leftPipeCode = 0
        self.leftPipeCancel = False
        self.rightPipe = None
        self.rightPercent = 0.0;
        self.rightPipeCode = 0
        self.rightPipeCancel = False
        self.initFinalPipeVars()
    def dropHandler(self, s, e) :
        pass
        if e.Data.GetDataPresent(DataFormats.FileDrop) :
            files = e.Data.GetData(DataFormats.FileDrop)
            self.InputFile.Items.Clear()
            self.fileInfo.Text = ""
            self.InputFile.Items.Add(files[0])
            self.info = {}
            self.info['filename'] = files[0]
            if findFileName(self.info) and findInfo(self.info) :
                s = "Duration :\t" + seconds2Str(self.info['seconds'])
                s += "\nResolution :\t%dx%d" % (self.info['width'],self.info['height'])
                s += "\nBitrate :\t\t" + self.info['bitrate']
                s += "\nOutput Folder :\t" + self.info['outfolder']
                self.fileInfo.Text = s
            pass
    def convertHandler(self, s, e) :
        if not ('filename' in self.info.keys()) :
            MyErrorMsgBox(self,'There is no file to be converted')
            return
        if not os.path.exists(self.info['outfolder']) :
            os.makedirs(self.info['outfolder'])
        quality = self.Quality.SelectedItem.Content.ToString()
        vq = 6
        if quality.find('VeryHigh') >= 0 :
            vq = 2
        elif quality.find('High') >= 0 :
            vq = 4
        elif quality.find('Low') >= 0 :
            vq = 8
        print "Quality %d" % vq
        self.initPipeVars()
        self.p3d = Progress3D(self)
        if self.SideBySideCheckBox.IsChecked :
            leftParams = ['left', vq]
            lb = BackGroundTask(self.convertSideBySideStep1,leftParams,self.progressLeftDone,self.progressLeftChanged)
            rightParams = ['right', vq]
            rb = BackGroundTask(self.convertSideBySideStep1,rightParams,self.progressRightDone,self.progressRightChanged)
            while self.leftPipe == None or self.rightPipe == None :
                time.sleep(0.5)
            finalParams = [vq, True]
            fb = BackGroundTask(self.convertSideBySideStep2,finalParams,self.progressFinalDone,self.progressFinalChanged)
        else :
            finalParams = [vq, False]
            fb = BackGroundTask(self.convertSideBySideStep2,finalParams,self.progressFinalDone,self.progressFinalChanged)
        self.p3d.show()
        # wait until background tasks stop
        if self.SideBySideCheckBox.IsChecked :
            while not lb.isDone() or not lb.isDone() :
                time.sleep(0.2)
        while not fb.isDone() :
            time.sleep(0.2)
        print 'Done : %d' % self.finalPipeCode
        if self.finalPipeCode != 0 :
            print 'Try to remove outfolder!!!'
            shutil.rmtree(self.info['outfolder'])
            print 'Removed outfolder!!!'
            if self.finalPipeCancel or (self.leftPipeCancel and self.rightPipeCancel) :
                pass
            else :
                MyErrorMsgBox(self, 'Error occured!')
        elif self.SideBySideCheckBox.IsChecked :
            os.remove(self.info['outfolder'] + '\\left.avi')
            os.remove(self.info['outfolder'] + '\\right.avi')
    def aboutHandler(self, sender, event) :
        AboutBox(self)
    def convertSideBySideStep1(self, sender, event, params) :
        leftOrRight = params[0]
        vq = params[1]
        #command = 'FFMPEG\\\\ffmpeg.exe -y -i ' + '\"' + self.info['filename'] +'\"' \
        #            + ' -b:v ' + self.info['bitrate'] \
        #            + ' -vf crop='  \
        #            + ('%s:%s:%s:0' % (self.info['width']/2,self.info['height'],self.info['width']/2)) \
        #           +' -aspect 2:1 \"' + self.info['outfolder'] + '\\\\right.avi\"'
        if leftOrRight == 'left' :
            command = 'FFMPEG\\\\ffmpeg.exe -y -i ' + '\"' + self.info['filename'] +'\"' \
                        + (' -vcodec mjpeg -q:v %d -r 20' % vq) \
                        + ' -vf \"scale=960:240,' \
                        + 'crop=480:240:0:0\"' \
                        +' -aspect 2:1' \
                        +' -acodec adpcm_ima_wav -ac 2 \"' \
                        + self.info['outfolder'] + '\\\\left.avi\"'
        else :
            command = 'FFMPEG\\\\ffmpeg.exe -y -i ' + '\"' + self.info['filename'] +'\"' \
                        + (' -vcodec mjpeg -q:v %d -r 20 ' % vq) \
                        + ' -vf \"scale=960:240,' \
                        + 'crop=480:240:480:0\"' \
                        +' -aspect 2:1' \
                        +' -acodec adpcm_ima_wav -ac 2 \"' \
                        + self.info['outfolder'] + '\\\\right.avi\"'
        print command
        p = subprocess.Popen(shlex.split(command), shell=True, stderr=subprocess.PIPE)
        if leftOrRight == 'left' :
            self.leftPipe = p
        else :
            self.rightPipe = p
        line = ""
        while p.poll() is None :
            if leftOrRight == 'left' and self.leftPipeCancel :
                p.kill()
                print 'request the left pipe to stop'
            if leftOrRight == 'right' and self.rightPipeCancel :
                p.kill()
                print 'request the right pipe to stop'
            a = p.stderr.read(1)
            if a != '\r' and a != '\n' :
               line += a
               continue
            matchObj = re.search('time=([0-9]+):([0-9]+):([0-9]+)\.', line)
            #print matchObj
            if matchObj != None :
                seconds = string.atoi(matchObj.group(1))*3600 \
                        + string.atoi(matchObj.group(2))*60 \
                        + string.atoi(matchObj.group(3))
                percent = (seconds*100)/self.info['seconds']
                if leftOrRight == 'left' :
                    self.leftPercent = percent
                    print "left %d" % percent
                else :
                    self.rightPercent = percent
                    print "right %d" % percent
                sender.ReportProgress(percent)
            line = ""
        if leftOrRight == 'left' :
            self.leftPipeCode = p.returncode
        else :
            self.rightPipeCode = p.returncode
        print "%s returncode = %d" % (leftOrRight, p.returncode)
        time.sleep(1)
        return True
    def progressLeftChanged(self, s, e) :
        self.p3d.leftBar.Value = e.ProgressPercentage;
    def progressRightChanged(self, s, e) :
        self.p3d.rightBar.Value = e.ProgressPercentage;
    def progressLeftDone(self, s, e, params) :
        print 'left done'
        self.leftPipe = None
        if self.leftPipeCode == 0 :
            s.ReportProgress(100)
        else :# error
            while self.rightPipe != None :
                self.rightPipeCancel = True
    def progressRightDone(self, s, e, params) :
        print 'right done'
        self.rightPipe = None
        if self.rightPipeCode == 0 :
            s.ReportProgress(100)
        else : # error
            while self.leftPipe != None :
                self.leftPipeCancel = True
    def convertSideBySideStep2(self, sender, event, params) :
        while True :
            time.sleep(0.5)
            if self.leftPipe == None and self.rightPipe == None :
                break
        if self.rightPipeCode != 0 or self.leftPipeCode != 0 : # error or canceled
            self.finalPipeCode = 1
            print "final canceled %d" % self.finalPipeCode
            return False
        leftFile = '\"' + self.info['outfolder'] + '\\\\left.avi\"'
        rightFile = '\"' + self.info['outfolder'] + '\\\\right.avi\"'
        vq = params[0]
        sbs = params[1]
        # add the created time for AVI
        # ffmpeg -i old.avi -metadata ICRD="2013-05-02 22:01:04" -c copy new.avi
        now = time.localtime()
        recordedTime = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        #command = 'FFMPEG\\\\ffmpeg.exe -y -i ' +  leftFile + ' -i ' + rightFile \
        #            + ' -vcodec mjpeg -s 400x240 -r 24 -qscale 1 '\
        #            + ' -acodec adpcm_ima_wav -ac 2 -map 0:0 -map 0:1 -map 1:0 '  \
        #            + outFile
        clipOpt = ""
        outNum = math.ceil(self.info['seconds'] / 600.0)
        outCount = 0
        while outCount < outNum : # split the file into files with 10 minutes
            outFile = '\"' + self.info['outfolder'] + ('\\\\NIN_%04d.AVI\"' % (outCount+1))
            if self.info['seconds'] > 600 :
                hour = (outCount * 600) / 3600
                minute = ((outCount * 600) % 3600) / 60
                clipOpt = " -ss %02d:%02d:00 -t 00:10:00" % (hour,minute)
            if sbs :
                command = 'FFMPEG\\\\ffmpeg.exe -y -i ' +  leftFile + ' -i ' + rightFile \
                            + clipOpt \
                            + (' -vcodec mjpeg -q:v %d -r 20 ' % vq) \
                            + ' -acodec adpcm_ima_wav -ac 2' \
                            + ' -metadata ICRD=\"' + recordedTime +'\"' \
                            + ' -map 0:0 -map 0:1 -map 1:0 '  \
                            + outFile
            else :
                command = 'FFMPEG\\\\ffmpeg.exe -y -i ' +  '\"' + self.info['filename'] +'\"' \
                            + clipOpt \
                            + (' -vcodec mjpeg -q:v %d -r 20 ' % vq) \
                            + ' -vf scale=480:240' \
                            + ' -aspect 2:1' \
                            + ' -acodec adpcm_ima_wav -ac 2' \
                            + ' -metadata ICRD=\"' + recordedTime +'\"' \
                            + ' ' + outFile
            print command
            p = subprocess.Popen(shlex.split(command), shell=True, stderr=subprocess.PIPE)
            self.finalPipe = p
            line = ""
            while p.poll() is None :
                if self.finalPipeCancel :
                    p.kill()
                    print 'request the final pipe to stop'
                a = p.stderr.read(1)
                if a != '\r' and a != '\n' :
                   line += a
                   continue
                print line
                matchObj = re.search('time=([0-9]+):([0-9]+):([0-9]+)\.', line)
                #print matchObj
                if matchObj != None :
                    seconds = string.atoi(matchObj.group(1))*3600 \
                            + string.atoi(matchObj.group(2))*60 \
                            + string.atoi(matchObj.group(3))
                    percent = (outCount*600*100+seconds*100)/self.info['seconds']
                    self.finalPercent = percent
                    print "final %d" % percent
                    sender.ReportProgress(percent)
                line = ""
            if p.returncode != 0 :
                self.finalPipeCode = p.returncode
                print "final returncode = %d" % (p.returncode)
                return False
            outCount += 1
        print "final returncode = %d" % (p.returncode)
        return True
    def progressFinalChanged(self, s, e) :
        self.p3d.finalBar.Value = e.ProgressPercentage
    def progressFinalDone(self, s, e, params) :
        self.finalPipe = None
        if self.finalPipeCode == 0 :
            s.ReportProgress(100)
        print 'final done %d' % self.finalPipeCode
        self.p3d.closeByOthers()

if __name__ == '__main__':
    Application().Run(MyWindow())
