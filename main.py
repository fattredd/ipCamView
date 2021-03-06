#! /usr/bin/python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#
"""
A program to show 4 ip cam streams fullscreen.
    Zoom in when one is pressed. Return on
    second press.

Author: Jack Butler
Date: July 21, 2017
"""

# import external libraries
import vlc
import os, sys, yaml
frameT = False

if sys.version_info[0] < 3:
    import Tkinter as Tk
    from Tkinter import ttk
    from Tkinter.filedialog import askopenfilename
else:
    import tkinter as Tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename

# import standard libraries
import os
import pathlib
from threading import Thread, Event
import time
import platform

class ttkTimer(Thread):
    """a class serving same function as wxTimer... but there may be better ways to do this
    """
    def __init__(self, callback, tick):
        Thread.__init__(self)
        self.callback = callback
        self.stopFlag = Event()
        self.tick = tick
        self.iters = 0

    def run(self):
        while not self.stopFlag.wait(self.tick):
            self.iters += 1
            self.callback()

    def stop(self):
        self.stopFlag.set()

    def get(self):
        return self.iters

class Player(Tk.Frame):
    """The main window has to deal with events.
    """
    def __init__(self, parent, title=None):
        Tk.Frame.__init__(self, parent)

        self.parent = parent


        '''
        # Menu Bar
        #   File Menu
        menubar = Tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = Tk.Menu(menubar)
        fileMenu.add_command(label="Open", underline=0, command=self.OnOpen)
        fileMenu.add_command(label="Exit", underline=1, command=_quit)
        menubar.add_cascade(label="File", menu=fileMenu)#'''

        # The second panel holds controls
        self.player = None
        self.videopanel = ttk.Frame(self.parent)
        self.canvas = Tk.Canvas(self.videopanel).pack(fill=Tk.BOTH,expand=1)
        self.videopanel.pack(fill=Tk.BOTH,expand=1)

        ctrlpanel = ttk.Frame(self.parent)
        pause  = ttk.Button(ctrlpanel, text="Pause", command=self.OnPause)
        play   = ttk.Button(ctrlpanel, text="Play", command=self.OnPlay)
        stop   = ttk.Button(ctrlpanel, text="Stop", command=self.OnStop)
        volume = ttk.Button(ctrlpanel, text="Volume", command=self.OnSetVolume)
        pause.pack(side=Tk.LEFT)
        play.pack(side=Tk.LEFT)
        stop.pack(side=Tk.LEFT)
        volume.pack(side=Tk.LEFT)
        self.volume_var = Tk.IntVar()
        self.volslider = Tk.Scale(ctrlpanel, variable=self.volume_var, command=self.volume_sel,
                from_=0, to=100, orient=Tk.HORIZONTAL, length=100)
        self.volslider.pack(side=Tk.LEFT)
        ctrlpanel.pack(side=Tk.BOTTOM)
        ctrlpanel2 = ttk.Frame(self.parent)
        self.scale_var = Tk.DoubleVar()
        self.timeslider_last_val = ""
        self.timeslider = Tk.Scale(ctrlpanel2, variable=self.scale_var, command=self.scale_sel,
                from_=0, to=1000, orient=Tk.HORIZONTAL, length=500)
        self.timeslider.pack(side=Tk.BOTTOM, fill=Tk.X,expand=1)
        self.timeslider_last_update = time.time()
        ctrlpanel2.pack(side=Tk.BOTTOM,fill=Tk.X)
        
        
        ctrlpanel.pack_forget()
        ctrlpanel2.pack_forget()
        #'''

        # VLC player controls
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

        # below is a test, now use the File->Open file menu
        #media = self.Instance.media_new('output.mp4')
        #self.player.set_media(media)
        #self.player.play() # hit the player button
        #self.player.video_set_deinterlace(str_to_bytes('yadif'))

        self.timer = ttkTimer(self.OnTimer, 1.0)
        self.timer.start()
        self.parent.update()

        #self.player.set_hwnd(self.GetHandle()) # for windows, OnOpen does does this


    def OnExit(self, evt):
        """Closes the window.
        """
        self.Close()

    def OnOpen(self, ip, profile=2, override=False):
        """Select a streaming ip
        """
        self.OnStop()
        # Creation
        self.link = "rtsp://admin:123456@{0}:554/profile{1}".format(ip, profile)
        if override:
            self.link = "Prim.mp4"
        self.Media = self.Instance.media_new(self.link)
        self.player.set_media(self.Media)
        if platform.system() == 'Windows':
                self.player.set_hwnd(self.GetHandle())
        else:
            self.player.set_xwindow(self.GetHandle()) # this line messes up windows
        self.OnPlay()
        
    def OnClick():
        self.player.stop()
        
    
    def OnPlay(self):
        """Toggle the status to Play/Pause.
        If no file is loaded, open the dialog window.
        """
        # check if there is a file to play, otherwise open a
        # Tk.FileDialog to select a file
        if not self.player.get_media():
            self.OnOpen('1')
        else:
            # Try to launch the media, if this fails display an error message
            if self.player.play() == -1:
                self.errorDialog("Unable to play.")

    def GetHandle(self):
        return self.videopanel.winfo_id()

    #def OnPause(self, evt):
    def OnPause(self):
        """Pause the player.
        """
        self.player.pause()

    def OnStop(self):
        """Stop the player.
        """
        self.player.stop()
        # reset the time slider
        self.timeslider.set(0)

    def OnTimer(self):
        """Update the time slider according to the current movie time.
        """
        if self.player == None:
            return
        # since the self.player.get_length can change while playing,
        # re-set the timeslider to the correct range.
        length = self.player.get_length()
        dbl = length * 0.001
        #self.timeslider.config(to=dbl)

        # update the time on the slider
        tyme = self.player.get_time()
        if tyme == -1:
            tyme = 0
        dbl = tyme * 0.001
        #self.timeslider_last_val = ("%.0f" % dbl) + ".0"
        # don't want to programatically change slider while user is messing with it.
        # wait 2 seconds after user lets go of slider
        #if time.time() > (self.timeslider_last_update + 2.0):
            #self.timeslider.set(dbl)

    def scale_sel(self, evt):
        if self.player == None:
            return
        nval = self.scale_var.get()
        sval = str(nval)
        if self.timeslider_last_val != sval:
            # this is a hack. The timer updates the time slider.
            # This change causes this rtn (the 'slider has changed' rtn) to be invoked.
            # I can't tell the difference between when the user has manually moved the slider and when
            # the timer changed the slider. But when the user moves the slider tkinter only notifies
            # this rtn about once per second and when the slider has quit moving.
            # Also, the tkinter notification value has no fractional seconds.
            # The timer update rtn saves off the last update value (rounded to integer seconds) in timeslider_last_val
            # if the notification time (sval) is the same as the last saved time timeslider_last_val then
            # we know that this notification is due to the timer changing the slider.
            # otherwise the notification is due to the user changing the slider.
            # if the user is changing the slider then I have the timer routine wait for at least
            # 2 seconds before it starts updating the slider again (so the timer doesn't start fighting with the
            # user)
            self.timeslider_last_update = time.time()
            mval = "%.0f" % (nval * 1000)
            self.player.set_time(int(mval)) # expects milliseconds


    def volume_sel(self, evt):
        if self.player == None:
            return
        volume = self.volume_var.get()
        if volume > 100:
            volume = 100
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")



    def OnToggleVolume(self, evt):
        """Mute/Unmute according to the audio button.
        """
        is_mute = self.player.audio_get_mute()

        self.player.audio_set_mute(not is_mute)
        # update the volume slider;
        # since vlc volume range is in [0, 200],
        # and our volume slider has range [0, 100], just divide by 2.
        self.volume_var.set(self.player.audio_get_volume())

    def OnSetVolume(self):
        """Set the volume according to the volume sider.
        """
        volume = self.volume_var.get()
        # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
        if volume > 100:
            volume = 100
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")

    def errorDialog(self, errormessage):
        """Display a simple error dialog.
        """
        Tk.tkMessageBox.showerror(self, 'Error', errormessage)

def Tk_get_root():
    if not hasattr(Tk_get_root, "root"): #(1)
        Tk_get_root.root= Tk.Tk()  #initialization call is inside the function
    return Tk_get_root.root

def _quit():
    print("_quit: bye")
    root = Tk_get_root()
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate
    os._exit(1)

if __name__ == "__main__":
    if os.path.isfile('config.yaml'):
        print('Config file found. Loading it.')
        with open('config.yaml','r') as f:
            config = yaml.load(f)
    else:
        print('No config file found. Creating one.')
        with open('config.yaml', 'w+') as f:
            config = {
                'topLeft': '192.168.1.128',
                'topRight': '192.168.1.131',
                'bottomLeft': '192.168.1.133',
                'bottomRight': '192.168.1.134'}
            f.write(yaml.dump(config, default_flow_style=False))
    ipList = [
        config['topLeft'],
        config['bottomLeft'],
        config['topRight'],
        config['bottomRight']]
    override = True if len(sys.argv)>1 else False
    root = Tk_get_root()
    root.protocol("WM_DELETE_WINDOW", _quit)
    
    # Setup the Major frames
    # Major all
    allFrame = ttk.Frame(root)
    
    holderL = ttk.Frame(allFrame)
    holderL.pack(side="left", fill="both", expand="true")
    player1 = Player(holderL) # Top Left
    player2 = Player(holderL) # Bottom Left

    holderR = ttk.Frame(allFrame)
    holderR.pack(side="right", fill="both", expand="true")
    player3 = Player(holderR) # Top Right
    player4 = Player(holderR) # Bottom Right
    
    # Major single
    singleFrame = ttk.Frame(root)
    singlePlayer = Player(singleFrame)
    
    def singleView(event):
        player1.OnStop() # Stop all videos
        player2.OnStop()
        player3.OnStop()
        player4.OnStop()
        allFrame.pack_forget() # Hide the pack frame
        
        # Determine which video was clicked
        y = root.winfo_pointery()
        x = root.winfo_pointerx()
        cam = 0b00
        
        # This is returning x,y of the subframe, not relative to root.
        print(x, root.winfo_screenwidth())
        if x > root.winfo_screenwidth()/2:
            cam = 0b10
        if y > root.winfo_screenheight()/2:
            cam |= 0b01
        
        # Open and show the single video
        print("Opening cam", cam,  ipList[cam])
        singleFrame.pack(fill=Tk.BOTH,expand=1)
        singlePlayer.OnOpen(ipList[cam], 1, override)
        
    def allView():
        singlePlayer.OnStop()
        singleFrame.pack_forget()
        allFrame.pack(fill=Tk.BOTH,expand=1)
        res = 2
        player1.OnOpen(ipList[0], res, override)
        player2.OnOpen(ipList[1], res, override)
        player3.OnOpen(ipList[2], res, override)
        player4.OnOpen(ipList[3], res, override)
    
    def toggleView(event):
        global frameT
        if frameT:
            allView()
        else:
            singleView(event)
        frameT = not frameT
    
    root.bind("<Button-1>", toggleView)
    allView()
    root.attributes("-fullscreen", True)
    root.mainloop()