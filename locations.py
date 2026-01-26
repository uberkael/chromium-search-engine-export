import os
import platform

LOCATIONS = {
    "chrome": {
        "windows": "%LOCALAPPDATA%\\Google\\Chrome\\User Data",
        "darwin": "$HOME/Library/Application Support/Google/Chrome",
        "linux": "$HOME/.config/google-chrome/Default"
    },
    "chromium": {
        "windows": "%LOCALAPPDATA%\\Chromium\\User Data",
        "darwin": "$HOME/Library/Application Support/Chromium",
        "linux": "$HOME/.config/chromium/Default"
    },
    "brave": {
        "windows": "%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data",
        "darwin": "$HOME/Library/Application Support/BraveSoftware/Brave-Browser",
        "linux": "$HOME/.config/BraveSoftware/Brave-Browser/Default/"
    },
    "edge": {
        "windows": "%LOCALAPPDATA%\\Microsoft\\Edge\\User Data",
        "darwin": "$HOME/Library/Application Support/Microsoft Edge",
        "linux": "$HOME/.config/microsoft-edge/Default"
    },
    "vivaldi": {
        "windows": "%LOCALAPPDATA%\\Vivaldi\\User Data",
        "darwin": "$HOME/Library/Application Support/Vivaldi",
        "linux": "$HOME/.config/vivaldi/Default"
    },
    "opera": {
        "windows": "%LOCALAPPDATA%\\Opera Software\\Opera Stable",
        "darwin": "$HOME/Library/Application Support/com.operasoftware.Opera",
        "linux": "$HOME/.config/opera"
    },
    "helium": {
        "windows": "%LOCALAPPDATA%\\net.imput.helium\\User Data",
        "darwin": "$HOME/Library/Application Support/net.imput.helium",
        "linux": "$HOME/.config/net.imput.helium/Default"
    },
}


def get_browser_path(browser: str) -> str | None:
    system = platform.system().lower()
    browser = browser.lower()
    if browser in LOCATIONS and system in LOCATIONS[browser]:
        return os.path.expandvars(LOCATIONS[browser][system])
