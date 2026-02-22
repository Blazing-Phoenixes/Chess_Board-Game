[app]
title = Professional Chess
package.name = professional_chess
package.domain = org.bharath
source.dir = .
source.include_exts = py,png,jpg,mp3,kv
version = 1.0.0
requirements = python3,kivy==2.3.1,python-chess==1.11.2,cython
icon.filename = assets/icon.png
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

# Android stable settings
android.api = 33
android.ndk = 25b
android.sdk_path = $HOME/android-sdk
android.ndk_path = $HOME/android-sdk/ndk/25b
android.build_tools = 33.0.2
