"""Test-wide setup: never touch cameras (the probe lights the webcam LED), render offscreen."""
import os

os.environ.setdefault("PROMAP_NO_CAMERA_SCAN", "1")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Closing a MainWindow saves its layout through QSettings; point that at a throwaway
# directory so the suite never rewrites the real ~/.config/promap/promap.conf.
import tempfile

from PySide6.QtCore import QSettings

_SETTINGS_DIR = tempfile.mkdtemp(prefix="promap-test-settings-")
QSettings.setPath(QSettings.NativeFormat, QSettings.UserScope, _SETTINGS_DIR)
QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, _SETTINGS_DIR)
