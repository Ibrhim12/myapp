[app]
# Application Info
title = EZI Phishing Detection
package.name = ezi_phishing
package.domain = org.example
source.dir = .
source.include_exts = py,png,kv,tflite,pkl,csv
version = 1.0
requirements = python3,kivy,kivymd,beautifulsoup4,requests,numpy,tensorflow==2.9.1,joblib,libffi
icon.filename = assets/icon.png
presplash.filename = assets/icon.png
orientation = portrait
fullscreen = 1

# Supported Screens
android.screen_dpi = nodpi

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Python Environment
python3 = 1
requirements.source = pypi

[buildozer]
log_level = 2
warn_on_root = 1

[android]
# Target API and NDK
android.api = 31
android.minapi = 21
android.ndk = 21e
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r21e

# Architectures
android.arch = armeabi-v7a,arm64-v8a

# Compilation Settings
p4a.branch = release-2023.01
p4a.source_dir = ~/.buildozer/android/platform/python-for-android

# Optimizations
android.heap_size = 512m

[debug]
debug = 1
