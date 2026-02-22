[app]
# (str) Title of your app
title = Professional Chess

# (str) Package name
package.name = professional_chess

# (str) Package domain (use reverse domain notation)
package.domain = org.bharath

# (str) Source code main file
source.dir = .
source.include_exts = py,png,jpg,mp3,kv

# (list) Source files to include (let empty to include all)
#source.include_patterns = assets/*

# (str) Application version
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy==2.3.1,python-chess==1.11.2,cython

# (str) Icon of the app
icon.filename = assets/icon.png

# (str) Supported orientation
orientation = portrait

# (bool) fullscreen
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
