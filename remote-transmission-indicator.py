#!/usr/bin/env python

import sys
import time
import logging
import os
import gtk
import appindicator
import transmissionrpc	# $ easy_install transmissionrpc

USER = ''
PASSWORD = ''
HOST = ''
PORT = ''
##
# Refresh rate in seconds
PING_FREQUENCY = 5
##
# Active MenuItem opens 'Transmission remote GUI'
OPEN_TRG = True
##
# Several symbols
UP_SYMBOL = u"\u2191"
DOWN_SYMBOL = u"\u2193"
TURTLE_MODE_SYMBOL = u"\u231B"
##
# Time between reconnect attempts
RECONNECT_BACKOFF_TIME = 60

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d.%m.%Y - %H:%M:%S: ', level = logging.DEBUG)

class RemoteTransmission:
	def __init__(self):
		#values to draw
		self.up = -1
		self.down = -1
		self.active_torrents = -1
		self.nbr_of_torrents = -1
		self.nbr_of_errors = -1
		self.turtle_mode_active = False
		#create indicator
		self.indicator = appindicator.Indicator("remote-transmission-applet", "",  appindicator.CATEGORY_APPLICATION_STATUS)
		self.indicator.set_status(appindicator.STATUS_ACTIVE)
		
		self.menu_setup()
		self.indicator.set_menu(self.menu)
		
		self.time_of_disconnect = 0
		self.connected = False
		self.first_run = True
		self.connection_error_shown = True
		
		try:
			self.connect()
			self.s = self.c.get_session()
		except:
			self.set_error_mode()

	
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
		
		# Error Item
		self.error_item = gtk.MenuItem("no errors")
		if OPEN_TRG: self.error_item.connect("activate", self.openTRG)
		self.menu.prepend(self.error_item)
		
		# Status Item
		self.torrent_status_item = gtk.MenuItem("n/a")
		if OPEN_TRG: self.torrent_status_item.connect("activate", self.openTRG)
		self.menu.prepend(self.torrent_status_item)

		# Turtle Item
		self.turtle_item = gtk.MenuItem("Toogle Turtle Mode")
		self.turtle_item.connect("activate", self.toggle_turtle)
		self.menu.prepend(self.turtle_item)


	def main(self):
		self.check_transmission()
		gtk.timeout_add(PING_FREQUENCY * 1000, self.check_transmission)
		gtk.main()	#let it recursively call itself
	
	def quit(self, widget):
		sys.exit(0)

	def refresh_indicator(self):
		if self.connected:
			self.show_speed_and_mode(self.down, self.up, self.turtle_mode_active)	
			self.show_active(self.active_torrents, self.nbr_of_torrents)
			self.show_errors(self.nbr_of_errors)

		else:
			self.indicator.set_label("No Transmission connection!")

		logging.info("Indicator redrawn")


	def check_transmission(self):
		if self.first_run: 
			self.connect()
			self.refresh_indicator()
			self.first_run = False
			return True

		if not self.connected and self.connection_error_shown: self.reconnect_loop()

		try:
			self.s = self.c.get_session()			
			# get specific torrent infos
			down, up, active, error = 0, 0, 0, 0
			for t in self.c.get_torrents():
				down += (t.rateDownload / 1024)
				up += (t.rateUpload / 1024)
				if t.status in ("seeding","downloading"):	active += 1
				if t.error > 1: error += 1
			self.up = up
			self.down = down
			self.nbr_of_errors = error
			self.active_torrents = active
			self.nbr_of_torrents = len(self.c.get_torrents())
			self.turtle_mode_active = self.s.alt_speed_enabled
			logging.info("Info updated")
		except:
			if not self.connected: self.connection_error_shown = True
			self.set_error_mode();

		self.refresh_indicator()

		return True

	def openTRG(self, widget):
		os.system("transgui")

	#
	# connection methods		
	#
	def connect(self):
		try:
			self.c = transmissionrpc.Client(HOST, PORT, USER, PASSWORD)
			self.set_working_mode()
			logging.info("We're connected to remote Transmission on %s:%s", HOST, PORT)
		except:
			logging.warning("Can't connect to remote Transmission!")

	def reconnect_loop(self):
		while not self.connected:
			time.sleep(RECONNECT_BACKOFF_TIME)		
			self.connect()

	#
	# helper
	#
	def show_errors(self, cnt):
		if cnt > 0: 
			self.error_item.set_label("Errors: "+str(cnt))
			self.error_item.show()
		else: self.error_item.hide()
		
	def toggle_turtle(self, widget):
		try:
			if self.s.alt_speed_enabled: self.c.set_session(alt_speed_enabled=False)
			else: self.c.set_session(alt_speed_enabled=True)
		except:
			self.connection_error()

	def show_active(self, active, all_torrents):
		self.torrent_status_item.set_label("Active: "+str(active)+"/"+str(all_torrents))
		
	def show_speed_and_mode(self, down, up, turtle_mode_active):
		turtle_sym = ""
		if turtle_mode_active: turtle_sym = TURTLE_MODE_SYMBOL
		self.indicator.set_label(turtle_sym + DOWN_SYMBOL+str(down)+u" KB/s - "+UP_SYMBOL+str(up)+" KB/s")

	def set_error_mode(self):
		if self.time_of_disconnect == 0:	self.time_of_disconnect = time.time()
		self.connected = False
		self.torrent_status_item.hide()
		self.error_item.hide()
		self.connection_error_item.show()
		logging.warning("Connection to remote Transmission lost")

	def set_working_mode(self):
		self.connected = True
		self.time_of_disconnect = 0
		self.connection_error_shown = False
		self.connection_error_item.hide()
		self.torrent_status_item.show()
		self.error_item.show()
		self.turtle_item.show()

	
if __name__ == "__main__":
	indicator = RemoteTransmission()
	indicator.main()			