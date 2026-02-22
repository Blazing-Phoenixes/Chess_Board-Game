[app]
title = Professional Chess
package.name = professional_chess
package.domain = org.bharath

# Source files
source.dir = .
source.include_exts = py,png,jpg,mp3,kv,json,txt
source.exclude_exts = pyc,pyo,swp,DS_Store

version = 1.0.0

# Python & Kivy requirements
requirements = python3,kivy==2.3.1,python-chess==1.11.2,cython

entrypoint = main.py

# App icon (optional)
icon.filename = assets/pieces/wK.png

# Screen settings
orientation = portrait
fullscreen = 0

# Android permissions (optional)
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1

# Android SDK settings
android.api = 33
android.ndk = 25.1.8937393
android.build_tools = 33.0.2
