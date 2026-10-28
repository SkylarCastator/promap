"""Screenshot the editor windows for the README, with docs/showcase.promap loaded (writes no QSettings)."""
import os, sys
os.environ["PROMAP_NO_CAMERA_SCAN"] = "1"
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SP))
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

OUT = os.path.join(SP, "images")
fmt = QSurfaceFormat(); fmt.setVersion(3, 3); fmt.setProfile(QSurfaceFormat.CoreProfile); fmt.setSwapInterval(0)
QSurfaceFormat.setDefaultFormat(fmt)
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
app = QApplication(sys.argv[:1]); app.setApplicationName("promap-shot")
from promap.ui.main_window import MainWindow
from promap.ui.state import AppState
state = AppState()
win = MainWindow(state)
win.resize(1500, 940); win.move(40, 40)
win.load_project(f"{SP}/showcase.promap")
win.show()

steps = []
def later(ms, fn): steps.append((ms, fn))
def shot(w, name):
    w.grab().save(f"{OUT}/{name}.png"); print("saved", name)

def prep():
    win.canvas.zoom_fit()
    for sf in state.project.surfaces:
        if sf.name == "Pumpkin": state.select(sf.id)
later(1500, prep)
later(1500, lambda: shot(win, "editor"))
def open_cues():
    win.open_cues_window(); win.cues_window.resize(1500, 560); win.cues_window.move(40, 1000)
    state.goto(1)
later(300, open_cues)
later(2500, lambda: shot(win.cues_window, "cues"))
def open_anim():
    win.open_animations_window(); win.animations_window.resize(560, 900)
    # select the Pumpkin surface so the panel shows its neon glow parameters
    for s in state.project.surfaces:
        if s.name == "Pumpkin":
            state.select(s.id) if hasattr(state, "select") else None
later(300, open_anim)
later(2500, lambda: shot(win.animations_window, "animations_window"))
def to3d():
    win.cues_window.hide(); win.animations_window.hide(); win._select_tab("3d")
later(300, to3d)
def shot3d():
    v = win.view3d
    v.grid_np.show(); v.orbit_yaw, v.orbit_pitch, v.orbit_dist = 38.0, -22.0, 6.0; v.set_view("orbit")
    for _ in range(5): v.base.taskMgr.step()
    v.base.win.setClearColorActive(True); v.base.win.setClearDepthActive(True)
    v.buffer.setActive(False)
    for _ in range(3): v.base.taskMgr.step()
    v.base.screenshot(f"{OUT}/_panda.png", defaultFilename=False)
    from PySide6.QtGui import QPixmap, QPainter
    pm = win.grab(); w = win.view3d_widget
    tl = w.mapTo(win, w.rect().topLeft())
    from PIL import Image
    im = Image.open(f"{OUT}/_panda.png").convert("RGB")
    p = QPainter(pm); p.drawPixmap(tl, QPixmap(f"{OUT}/_panda.png").scaled(w.size())); p.end()
    pm.save(f"{OUT}/editor_3d.png"); print("saved editor_3d")
later(6000, shot3d)
later(500, lambda: (os.remove(f"{OUT}/_panda.png"), os._exit(0)))

t = 0
for ms, fn in steps:
    t += ms
    QTimer.singleShot(t, fn)
sys.exit(app.exec())
