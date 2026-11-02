# Hand Gesture Mouse Controller

A Windows desktop application that uses a webcam, MediaPipe hand landmarks, OpenCV, and PyAutoGUI to control the primary display with one hand.

## Features

- Real-time one-hand tracking with MediaPipe.
- Smooth index-fingertip cursor movement with configurable interpolation.
- Left click, right click, scrolling, and optional drag-and-drop.
- FPS, tracking, gesture, fingertip, and pinch overlays.
- Safe screen-edge clamping and graceful webcam/resource cleanup.
- No background services or elevated permissions are required.

## Installation

### Prerequisites

- Windows 10 or Windows 11.
- Python 3.11 or newer.
- A working webcam.
- A desktop session where PyAutoGUI is allowed to control the mouse.

### Clone and install

```powershell
git clone <repository-url>
cd virtual-mouse
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
```

MediaPipe downloads its hand-landmark model on the first launch and stores it in the user cache at:

```text
%USERPROFILE%\.cache\hand-gesture-mouse\hand_landmarker.task
```

The model is not stored in this repository.

## Running

From the project directory:

```powershell
python src\main.py
```

Press `q` or `Esc` in the camera window to exit. Grant camera permission if Windows asks.

The default capture configuration is 640×480 at 30 FPS. Adjust the constants in `src\config.py` if your webcam requires a different resolution.

## Committing the project

Review the files before committing:

```powershell
git status
git diff -- README.md .gitignore requirements.txt src
```

Then stage and commit:

```powershell
git add .gitignore README.md requirements.txt src screenshots/.gitkeep
git commit -m "Add hand gesture mouse controller"
git push
```

The `.gitignore` excludes virtual environments, Python caches, IDE files, local environment files, and generated screenshots while preserving `screenshots/.gitkeep`.

## Gesture mappings

| Gesture | Action |
| --- | --- |
| Index fingertip | Move cursor |
| Index + middle fingertips pinch | Left click on release |
| Hold index + middle pinch | Drag while held |
| Thumb + index pinch | Right click |
| Open palm | Scroll up |
| Closed fist | Scroll down |

Clicks and scroll events are debounced by a 300 ms cooldown. The camera image is mirrored so movement feels natural.

## Project architecture

- `src/main.py`: application loop, action state machine, and overlay.
- `src/hand_tracker.py`: MediaPipe initialization and landmark conversion.
- `src/gesture_detector.py`: reusable finger and distance-based gesture logic.
- `src/mouse_controller.py`: screen mapping, smoothing, bounds, and PyAutoGUI actions.
- `src/config.py`: all tunable configuration values.
- `src/utils.py`: FPS and overlay helpers.

## Configuration

Edit the constants in `src/config.py` or construct an `AppConfig` with custom values. Important settings include camera dimensions, `SMOOTHING_FACTOR`, click thresholds, `CLICK_COOLDOWN`, `FRAME_REDUCTION`, and drag hold duration.

## Troubleshooting

- **Webcam unavailable:** close other camera applications, check Windows camera permissions, and verify that the selected camera index is available.
- **Cursor is jittery:** increase `SMOOTHING_FACTOR` toward `1.0` only if you want faster response; reduce it for stronger smoothing.
- **Gestures trigger unexpectedly:** improve lighting, keep the full hand visible, and adjust thresholds in `config.py`.
- **Low FPS:** lower the camera resolution, close other camera-using applications, or use a well-lit scene.
- **PyAutoGUI security warning:** check that the desktop session is active and that the application is not being run in a restricted remote session.

## Future enhancements

- User calibration for personalized hand geometry.
- Configurable gesture profiles and a settings UI.
- Optional multi-hand shortcuts.
- GPU-backed inference where supported.
