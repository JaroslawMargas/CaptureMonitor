# CaptureMonitor
CaptureMonitor is a project in Python language base in the greater part on win32api and pyHook module

Instruction:
- run main.py
- ATL + V - start/stop recording
- ALT + B - play/stop sequence
- ALT + N - clear sequence
- ALT + S - save sequence to xml file
- ALT + L - load all xml files and merge to one sequence

config.ini
TCP_IP = localhost for the server 

rscommand.ini
version - send comand with version to device before command key
key pressed/key relassed -  map :  keyboard key = command hex

HookEvent.py
self.send_rs = True  - send rs232 command

After each click of mouse - the png file with screenshoot will be created

https://sourceforge.net/p/pyhook/wiki/PyHook_Tutorial/

It grabs the cursor position and create a screen shot from the monitor.

Requirements:
- grab mouse event (left, right , wheel click) and keybord events.
- detect display device and monitor params.
- make capture from the monitor after push and down 

Update 03.09.2018
- using logging in multiple modules

Update 29.11.2018
- bug fixing and compressor of PNG

Update 14.01.2019
- full support of mouse event  (move, click, keyboard)
- recording mouse events
- playback mouse events
- bug fixing

Update 29.04.2019
- tcp/ip communication. The server is a recorder and the client is a receiver

Update 20.05.2019
- ack in TCP and config file


Update 01.07.2019
- draw alpha cursor position

Update 08.07.2019
- save project in xml
- find and merge xml files into one command list.

Update 12.12.2019
- rs232 command config
- record keyboard key sequence, map key to hex command and send via rs232

