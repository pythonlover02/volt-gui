import requests
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QThread, Signal
from version import VERSION

class UpdateCheckThread(QThread):

    update_available = Signal(str)

    def run(self):
        try:
            response = requests.get("https://api.github.com/repos/pythonlover02/volt-gui/releases/latest", timeout=5)
            if response.status_code == 200:
                latest_version = response.json()["tag_name"].lstrip("v")
                if latest_version != VERSION:
                    self.update_available.emit(latest_version)
        except:
            pass

class UpdateChecker:

    @staticmethod
    def check_for_updates(main_window):
        """
        Check for updates on GitHub releases.
        """
        thread = UpdateCheckThread()
        thread.update_available.connect(lambda version: UpdateChecker.show_update_notification(main_window, version))
        thread.start()

        main_window._update_thread = thread

    @staticmethod
    def show_update_notification(main_window, new_version):
        """
        Show update notification window or tray message.
        """
        message = f"A new volt-gui version is available: {new_version}"

        if hasattr(main_window, 'tray_icon') and main_window.use_system_tray:
            main_window.tray_icon.showMessage(
                "volt-gui Update",
                message,
                main_window.tray_icon.MessageIcon.Information,
                5000
            )
        else:
            QMessageBox.information(main_window, "volt-gui Update", message)
