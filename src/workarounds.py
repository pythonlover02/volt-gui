import sys, os
from PySide6.QtCore import QProcess

class WorkaroundManager:

    @staticmethod
    def setup_qt_platform():
        """
        Default to X11 (xcb)
        Only sets if QT_QPA_PLATFORM is not already defined, allowing users to override if needed.
        """
        if 'QT_QPA_PLATFORM' not in os.environ:
            os.environ['QT_QPA_PLATFORM'] = 'xcb'

    @staticmethod
    def get_clean_env():
        """
        Create a clean environment for process calls, removing PyInstaller library paths.
        Returns a list of strings in QProcess environment format.
        """
        env = os.environ.copy()
        if getattr(sys, 'frozen', False):
            env.pop('LD_LIBRARY_PATH', None)
            env.pop('LD_PRELOAD', None)
        if hasattr(sys, '_MEIPASS') and 'PATH' in env:
            paths = env['PATH'].split(os.pathsep)
            clean_paths = [p for p in paths if sys._MEIPASS not in p]
            env['PATH'] = os.pathsep.join(clean_paths)
        return [f"{key}={value}" for key, value in env.items()]

    @staticmethod
    def setup_clean_process(process):
        """
        Setup a QProcess with clean environment.
        Args:
        process (QProcess): The QProcess instance to configure
        """
        clean_env = WorkaroundManager.get_clean_env()
        process.setEnvironment(clean_env)
