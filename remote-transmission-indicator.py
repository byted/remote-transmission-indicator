#!/usr/bin/env python

import sys
import os
import gtk
import appindicator
import transmissionrpc	# $ easy_install transmissionrpc

USER = ''
PASSWORD = ''
HOST = ''
PORT = ''
##
# INLINE: Display mode
# 1 -> inline: show speed info in status bar
# 0 -> symbol: show only a symbol in status bar
INLINE = 1
##
# Refresh rate in seconds
PING_FREQUENCY = 5
##
# Active MenuItem opens 'Transmission remote GUI'
OPEN_TRG = True
##
# Symbols for Up- and Download
UP_SYMBOL = u"\u2191"
DOWN_SYMBOL = u"\u2193"


class RemoteTransmission:
	def __init__(self):
		if INLINE: icon = ""
		else: icon = "transmission-tray-icon"
		#create indicator
		self.indicator = appindicator.Indicator("remote-transmission-applet", icon, appindicator.CATEGORY_APPLICATION_STATUS)
		self.indicator.set_status(appindicator.STATUS_ACTIVE)
		
		self.menu_setup()
		self.indicator.set_menu(self.menu)
	
	def menu_setup(self):
		self.menu = gtk.Menu()
		
		#Quit Item
		self.quit_item = gtk.MenuItem("Quit")
		self.quit_item.connect("activate", self.quit)
		self.quit_item.show()
		self.menu.append(self.quit_item)
		
		# Seperator
		self.seperator = gtk.SeparatorMenuItem()
		self.seperator.show()
		self.menu.prepend(self.seperator)
		
		# Turtle Item
		self.turtle_item = gtk.MenuItem("Turtle Mode: n/a")
		if OPEN_TRG: self.turtle_item.connect("activate", self.toggle_turtle)
		self.turtle_item.show()
		self.menu.prepend(self.turtle_item)
		
		# Error Item
		self.error_item = gtk.MenuItem("no errors")
		if OPEN_TRG: self.error_item.connect("activate", self.openTRG)
		self.menu.prepend(self.error_item)
		
		# Status Item
		self.torrent_status_item = gtk.MenuItem("n/a")
		if OPEN_TRG: self.torrent_status_item.connect("activate", self.openTRG)
		self.torrent_status_item.show()
		self.menu.prepend(self.torrent_status_item)
		
		# Speed Items
		if not INLINE:
			self.down_speed_item = gtk.MenuItem("D: n/a")
			self.down_speed_item.show()
			self.menu.prepend(self.down_speed_item)
		
			self.up_speed_item = gtk.MenuItem("U: n/a")
			self.up_speed_item.show()
			self.menu.prepend(self.up_speed_item)
		
		try:
			self.c = self.connect()
			self.s = self.c.get_session()
		except:
			self.connection_error()
		


	def main(self):
		self.check_transmission()
		gtk.timeout_add(PING_FREQUENCY * 1000, self.check_transmission)
		gtk.main()	#let it recusively call itself
	
	def quit(self, widget):
		sys.exit(0)
		
	def openTRG(self, widget):
		os.system("transgui")
	
	def toggle_turtle(self, widget):
		try:
			if self.s.alt_speed_enabled: self.c.set_session(alt_speed_enabled=False)
			else: self.c.set_session(alt_speed_enabled=True)
		except:
			self.connection_error()
		
	def check_transmission(self):
		try:
			self.s = self.c.get_session()			
			# get specific torrent infos
			down, up, active, error = 0, 0, 0, 0
			for t in self.c.get_torrents():
				down += (t.rateDownload / 1024)
				up += (t.rateUpload / 1024)
				if t.status in ("seeding","downloading"):	active += 1
				if t.error > 1: error += 1

			self.show_speed(down, up)	
			self.show_active(active, self.c.get_torrents())
			self.show_errors(error)
			self.show_turtle(self.s.alt_speed_enabled)
		except:
			self.connection_error()
		finally:
			return True
		

	def connect(self):
		try:
			return transmissionrpc.Client(HOST, PORT, USER, PASSWORD)
		except:
			raise Exception("Can't connect to remote Transmission Client")
		return True
		
		
	def connection_error(self):
		self.show_speed("n/a", "n/a")
		self.torrent_status_item.set_label("Connection Error")
		self.turtle_item.hide()
		self.error_item.hide()

	# methods for updating gui elements		
	def show_errors(self, cnt):
		if cnt > 0: 
			self.error_item.set_label("Errors: "+str(cnt))
			self.error_item.show()
		else: self.error_item.hide()
		
	def show_active(self, active, all_torrents):
		self.torrent_status_item.set_label("Active: "+str(active)+"/"+str(len(all_torrents)))
		
	def show_speed(self, down, up):
		if not INLINE:		
			self.down_speed_item.set_label(DOWN_SYMBOL+" "+str(down)+" KB/s")
			self.up_speed_item.set_label(UP_SYMBOL+" "+str(up)+" KB/s")			
		else:
			self.indicator.set_label(DOWN_SYMBOL+" "+str(down)+u" KB/s - "+UP_SYMBOL+" "+str(up)+" KB/s")
	
	def show_turtle(self, is_activated):
		if is_activated: self.turtle_item.set_label("Turtle Mode: ON")
		else: self.turtle_item.set_label("Turtle Mode: OFF")
		
	
if __name__ == "__main__":
	indicator = RemoteTransmission()
	indicator.main()			

