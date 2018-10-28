# remote-transmission-indicator

This is a small Ubuntu/Unity Indicator-applet which constantly checks a remote Transmission-Bittorrent ( http://www.transmissionbt.com/ ) Session.
It's written in Python and uses the __transmissionrpc__ library ( https://bitbucket.org/blueluna/transmissionrpc/wiki/Home )

## Features

* shows:
    * up- and download speed
    * number of active torrents
    * number of torrents with errors
    * turtle mode enabled or not
* start __Transmission remote GUI__ by clicking on either _Errors_ or _Active_
* toggle turtle mode by clicking on _Turtle Mode_
* two different display style:
    * inline => show speed in show speed info in status bar
    * symbol => show only a symbol in status bar

## Install

__transmissionrpc__ is needed and it is available at Python Package Index so a simple
```
$ easy_install transmissionrpc
```
should be fine. If not, head over to https://bitbucket.org/blueluna/transmissionrpc/wiki/Home

After that, just run the file
```
$ ./remote_transmission_indicator.py
```

For an automatic start after login, use Ubuntu's __Startup Application__ (via Dash)

## Settings

Just edit the first few lines of the source code to suit your needs.

### Tested on Ubuntu 13.04/13.10/14.04 with Transmission 2.71
