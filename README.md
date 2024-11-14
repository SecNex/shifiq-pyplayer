# ShifIQ Python Player

**ShifIQ Python Player** is a Python application that allows you to surf a web page and interact with it.

## Features

- Guided access to a web page or the **ShifIQ Kisok Web Engine**
- A button to go back to the main page
- Global mouse tracking
- Inactivity warning after 5 minutes
- Automatic return to the main page after 10 minutes of inactivity

## Installation

1. Install Python 3.10+
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python player.py
```

## Configuration

If you want to change the URL, you can do so by editing the `url` variable in the `player.py` file in line 200.

```python
if __name__ == "__main__":
    app = QApplication(sys.argv)
    url = "https://docs.secnex.io/" # Change this to the URL you want to surf
    window = ShifIQKioskBrowser(url)
    window.show()

    sys.exit(app.exec())
```

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions to improve the player. Please open an issue or submit a pull request.

## Contact

For questions or feedback, please contact us at support@secnex.io.