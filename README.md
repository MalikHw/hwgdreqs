# HwGDReqs - Geometry Dash Level Request Manager

A desktop application for streamers to manage Geometry Dash level requests from viewers!

## Features

- 🎮 Queue system for submitted levels with difficulty icons
- 📋 Copy ID, delete, choose random, and report functions
- 🔍 Detailed level information display
- ⚙️ Customizable filters (length, difficulty, rated status)
- 🎨 Customize your submission page (gradient/solid/image backgrounds)
- 💬 Custom submission and offline messages
- 📊 Level history and queue export
- 🔄 Real-time sync with web submission page

## Installation

### Windows
1. Download `HwGDReqs-Windows.zip` from [Releases](https://github.com/MalikHw/hwgdreqs/releases)
2. Extract the ZIP file
3. Run `HwGDReqs.exe`

### Linux
1. Download `HwGDReqs-Linux.tar.gz` from [Releases](https://github.com/MalikHw/hwgdreqs/releases)
2. Extract: `tar -xzf HwGDReqs-Linux.tar.gz`
3. Run: `./HwGDReqs`

## Setup

1. Visit https://hwgdreqs.rf.gd
2. Connect your Google account (OAuth) and/or add your Twitch token
3. Set your streamer name
4. Copy your APP-ID
5. Paste the APP-ID into the desktop app when prompted
6. Share your submission link with viewers!

## How It Works

### For Streamers:
- Run the desktop app and authenticate with your APP-ID
- Configure filters to control what levels viewers can submit
- Customize your submission page appearance
- Manage incoming requests in real-time
- Copy level IDs, delete unwanted submissions, or pick random levels

### For Viewers:
- Visit your streamer's submission link
- Enter a Geometry Dash level ID
- If it matches the filters, it gets added to the queue!

## Icon Files

Place these difficulty face icons in the `icons/` folder:
- `na.png` - Not Applicable
- `easy.png` - Easy
- `normal.png` - Normal
- `hard.png` - Hard
- `harder.png` - Harder
- `insane.png` - Insane
- `demon.png` - All demon difficulties

## Building from Source

### Requirements
- Python 3.11+
- PySide6
- Nuitka

### Build Commands

**Windows:**
```bash
pip install -r requirements.txt
pip install nuitka
python -m nuitka --standalone --windows-console-mode=disable --enable-plugin=pyside6 --windows-icon-from-ico=icon.ico --include-data-dir=icons=icons --include-data-file=icon.ico=icon.ico --include-data-file=icon.png=icon.png main.py
```

**Linux:**
```bash
pip install -r requirements.txt
pip install nuitka
python -m nuitka --standalone --enable-plugin=pyside6 --include-data-dir=icons=icons --include-data-file=icon.png=icon.png main.py
```

## Credits

Made with ❤️ by **MalikHw47**

- YouTube: [@MalikHw47](https://youtube.com/@MalikHw47)
- Twitch: [MalikHw47](https://twitch.tv/MalikHw47)
- GitHub: [MalikHw47](https://github.com/MalikHw47)

## Support

If you find this tool helpful, consider [donating](https://malikhw.github.io/donate)!

## License

MIT License - feel free to use and modify!
