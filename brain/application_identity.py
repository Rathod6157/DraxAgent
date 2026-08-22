from pathlib import Path


class ApplicationIdentity:

    def __init__(self):

        self.identities = {

            # Browsers
            "chrome.exe": "Google Chrome",
            "msedge.exe": "Microsoft Edge",
            "firefox.exe": "Mozilla Firefox",
            "brave.exe": "Brave",

            # Windows
            "explorer.exe": "File Explorer",
            "notepad.exe": "Notepad",
            "calc.exe": "Calculator",
            "calculatorapp.exe": "Calculator",
            "time.exe": "Clock",
            "systemsettings.exe": "Settings",
            "snippingtool.exe": "Snipping Tool",

            # Development
            "code.exe": "Visual Studio Code",
            "devenv.exe": "Visual Studio",

            # Media
            "spotify.exe": "Spotify",
            "vlc.exe": "VLC Media Player",

            # Communication
            "discord.exe": "Discord",
            "telegram.exe": "Telegram",

            # Gaming
            "steam.exe": "Steam",
            "minecraftlauncher.exe": "Minecraft Launcher",
        }


    def resolve(
        self,
        executable=None,
        process=None
    ):

        # ---------------------------------
        # Prefer executable filename
        # ---------------------------------

        if executable:

            executable_name = Path(
                executable
            ).name.lower()

            identity = self.identities.get(
                executable_name
            )

            if identity:

                return identity


        # ---------------------------------
        # Fallback to process name
        # ---------------------------------

        if process:

            process_name = Path(
                process
            ).name.lower()

            identity = self.identities.get(
                process_name
            )

            if identity:

                return identity


        # ---------------------------------
        # Unknown application
        # ---------------------------------

        if process:

            return Path(
                process
            ).stem

        return "Unknown"


application_identity = ApplicationIdentity()