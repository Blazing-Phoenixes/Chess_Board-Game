[app]
title = Professional Chess
package.name = professional_chess
package.domain = org.bharath

source.dir = .
source.include_exts = py,png,jpg,mp3,kv
version = 1.0.0

# Python requirements
requirements = python3,kivy==2.3.1,python-chess==1.11.2,cython

# App icon
icon.filename = assets/icon.png

# Screen settings
orientation = portrait
fullscreen = 0


[buildozer]
log_level = 2
warn_on_root = 1

# Android build settings
android.api = 33
android.ndk = 25.1.8937393
android.build_tools = 33.0.2

# DO NOT set SDK paths for GitHub Actions
# android.sdk_path =
# android.ndk_path =
