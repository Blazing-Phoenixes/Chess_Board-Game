[app]
title = Professional Chess
package.name = professional_chess
package.domain = org.bharath

source.dir = .
source.include_exts = py,png,jpg,kv,mp3
version = 1.0.0

requirements = python3,kivy==2.3.1,python-chess==1.11.2,cython
entrypoint = main.py

icon.filename = assets/pieces/wK.png
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

android.api = 33
android.ndk = 25.1.8937393
android.build_tools = 33.0.2
