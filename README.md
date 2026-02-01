# HwGDReqs - Geometry Dash Level Request Manager

A desktop application for streamers to manage Geometry Dash level requests from viewers!

## Features

- **Queue System**: Displays submitted levels with difficulty icons
- **Level Management**: Copy ID, delete, choose random, or report levels
- **Live Details**: View complete level information on the right panel
- **Filters**: Configure length, difficulty, and rated/unrated filters
- **Auto-Sync**: Real-time synchronization with your submission website
- **History**: All played levels are archived
- **Export**: Export your queue to a text file

## Setup

1. Go to https://hwgdreqs.rf.gd and connect your accounts (Google/Twitch)
2. Copy your APP-ID from the website
3. Run HwGDReqs and open Settings
4. Paste your APP-ID and configure your preferences
5. Share your submission link with viewers: `hwgdreqs.rf.gd/YOUR-APP-ID/submit`

## Requirements

- Windows 10/11 or Linux (Ubuntu 20.04+)
- No Python installation required (bundled)

## Building from Source

```bash
pip install -r requirements.txt
python main.py
```

To build with Nuitka:
```bash
pip install nuitka
python -m nuitka --standalone --enable-plugin=pyqt6 main.py
```

## Made by MalikHw47

- YouTube: [@MalikHw47](https://youtube.com/@MalikHw47)
- Twitch: [MalikHw47](https://twitch.tv/MalikHw47)
- GitHub: [MalikHw47](https://github.com/MalikHw47)

## Support

If you find this tool useful, please consider [donating](https://malikhw.github.io/donate)!

## License

MIT License - Feel free to use and modify!
