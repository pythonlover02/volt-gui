#!/usr/bin/env python3

import sys
import os
import glob
import subprocess
import signal
import socket
import threading
import configparser
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QSystemTrayIcon, QMenu, QMessageBox,
    QTabWidget, QCheckBox, QSpinBox, QDoubleSpinBox, QScrollArea, QFrame
)
from PySide6.QtCore import (
    Qt, QEvent, QProcess, Signal, QObject, QTimer, 
    QPropertyAnimation, QEasingCurve, QSize
)
from PySide6.QtGui import QIcon, QAction
from theme import ThemeManager
from gpu_launch import GPULaunchManager
from cpu import CPUManager
from extras import ExtrasManager
from options import OptionsTab


class ConfigManager:
    @staticmethod
    def get_config_path():
        config_dir = Path(os.path.expanduser("~/.config/volt-gui"))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "volt-config.ini"
    
    @staticmethod
    def save_settings(cpu_widgets, mesa_widgets, nvidia_widgets):
        config = configparser.ConfigParser()
        
        config['CPU'] = {
            'governor': cpu_widgets['gov_combo'].currentText(),
            'scheduler': cpu_widgets['sched_combo'].currentText()
        }
        
        config['Mesa'] = {
            'vsync_gl': mesa_widgets['mesa_vsync_gl_combo'].currentText(),
            'vsync_vk': mesa_widgets['mesa_vsync_vk_combo'].currentText(),
            'thread_opt': mesa_widgets['mesa_thread_opt_combo'].currentText(),
            'dither': mesa_widgets['mesa_dither_combo'].currentText(),
            'shader_cache': mesa_widgets['mesa_shader_cache_combo'].currentText(),
            'cache_size': mesa_widgets['mesa_cache_size_combo'].currentText(),
            'error_check': mesa_widgets['mesa_error_check_combo'].currentText(),
            'fake_gl': mesa_widgets['mesa_fake_gl_combo'].currentText(),
            'fake_glsl': mesa_widgets['mesa_fake_glsl_combo'].currentText(),
            'fake_vk': mesa_widgets['mesa_fake_vk_combo'].currentText()
        }
        
        config['NVIDIA'] = {
            'vsync_gl': nvidia_widgets['nvidia_vsync_gl_combo'].currentText(),
            'thread_opt': nvidia_widgets['nvidia_thread_opt_combo'].currentText(),
            'tex_quality': nvidia_widgets['nvidia_tex_quality_combo'].currentText(),
            'fsaa': nvidia_widgets['nvidia_fsaa_combo'].currentText(),
            'fxaa': nvidia_widgets['nvidia_fxaa_combo'].currentText(),
            'aniso': nvidia_widgets['nvidia_aniso_combo'].currentText(),
            'gsync': nvidia_widgets['nvidia_gsync_combo'].currentText(),
            'shader_cache': nvidia_widgets['nvidia_shader_cache_combo'].currentText(),
            'cache_size': nvidia_widgets['nvidia_cache_size_combo'].currentText(),
            'glsl_ext': nvidia_widgets['nvidia_glsl_ext_combo'].currentText(),
            'glx': nvidia_widgets['nvidia_glx_combo'].currentText()
        }
        
        if GPULaunchManager.render_selector_widgets:
            config['RenderSelector'] = {
                'opengl_render': GPULaunchManager.render_selector_widgets['opengl_render_combo'].currentText(),
                'vulkan_render': GPULaunchManager.render_selector_widgets['vulkan_render_combo'].currentText()
            }
            
        if hasattr(GPULaunchManager, 'launch_options_widgets'):
            launch_options = GPULaunchManager.launch_options_widgets['launch_options_input'].text()
            launch_options = launch_options.replace('%', '%%')
            config['LaunchOptions'] = {
                'launch_options': launch_options
            }
        
        with open(ConfigManager.get_config_path(), 'w') as configfile:
            config.write(configfile)
    
    @staticmethod
    def load_settings(cpu_widgets, mesa_widgets, nvidia_widgets):
        config = configparser.ConfigParser()
        config_path = ConfigManager.get_config_path()
        
        if not os.path.exists(config_path):
            return False
        
        config.read(config_path)
        
        if 'CPU' in config:
            if 'governor' in config['CPU']:
                cpu_widgets['gov_combo'].setCurrentText(config['CPU']['governor'])
            if 'scheduler' in config['CPU']:
                cpu_widgets['sched_combo'].setCurrentText(config['CPU']['scheduler'])
        
        if 'Mesa' in config:
            mesa_mappings = {
                'vsync_gl': 'mesa_vsync_gl_combo',
                'vsync_vk': 'mesa_vsync_vk_combo',
                'thread_opt': 'mesa_thread_opt_combo',
                'dither': 'mesa_dither_combo',
                'shader_cache': 'mesa_shader_cache_combo',
                'cache_size': 'mesa_cache_size_combo',
                'error_check': 'mesa_error_check_combo',
                'fake_gl': 'mesa_fake_gl_combo',
                'fake_glsl': 'mesa_fake_glsl_combo',
                'fake_vk': 'mesa_fake_vk_combo'
            }
            
            for key, widget_key in mesa_mappings.items():
                if key in config['Mesa']:
                    mesa_widgets[widget_key].setCurrentText(config['Mesa'][key])
        
        if 'NVIDIA' in config:
            nvidia_mappings = {
                'vsync_gl': 'nvidia_vsync_gl_combo',
                'thread_opt': 'nvidia_thread_opt_combo',
                'tex_quality': 'nvidia_tex_quality_combo',
                'fsaa': 'nvidia_fsaa_combo',
                'fxaa': 'nvidia_fxaa_combo',
                'aniso': 'nvidia_aniso_combo',
                'gsync': 'nvidia_gsync_combo',
                'shader_cache': 'nvidia_shader_cache_combo',
                'cache_size': 'nvidia_cache_size_combo',
                'glsl_ext': 'nvidia_glsl_ext_combo',
                'glx': 'nvidia_glx_combo'
            }
            
            for key, widget_key in nvidia_mappings.items():
                if key in config['NVIDIA']:
                    nvidia_widgets[widget_key].setCurrentText(config['NVIDIA'][key])
        
        if 'RenderSelector' in config and GPULaunchManager.render_selector_widgets:
            if 'opengl_render' in config['RenderSelector']:
                GPULaunchManager.render_selector_widgets['opengl_render_combo'].setCurrentText(
                    config['RenderSelector']['opengl_render']
                )
            if 'vulkan_render' in config['RenderSelector']:
                GPULaunchManager.render_selector_widgets['vulkan_render_combo'].setCurrentText(
                    config['RenderSelector']['vulkan_render']
                )
                
        if 'LaunchOptions' in config and hasattr(GPULaunchManager, 'launch_options_widgets'):
            if 'launch_options' in config['LaunchOptions']:
                launch_options = config['LaunchOptions']['launch_options']
                launch_options = launch_options.replace('%%', '%')
                GPULaunchManager.launch_options_widgets['launch_options_input'].setText(launch_options)
        
        return True


class SingletonSignals(QObject):
    show_window = Signal()


class SingleInstanceChecker:
    def __init__(self, port=47832):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', self.port)
        self.signals = SingletonSignals()
        self.listener_thread = None
        self.running = False
        
    def is_already_running(self):
        try:
            self.sock.bind(self.server_address)
            self.start_listener()
            return False
        except socket.error:
            self.signal_first_instance()
            return True
    
    def start_listener(self):
        self.sock.listen(1)
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_for_signals)
        self.listener_thread.daemon = True
        self.listener_thread.start()
    
    def listen_for_signals(self):
        while self.running:
            try:
                connection, _ = self.sock.accept()
                try:
                    self.signals.show_window.emit()
                finally:
                    connection.close()
            except:
                break
    
    def signal_first_instance(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.server_address)
            sock.close()
        except:
            pass
    
    def cleanup(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass


class MainWindow(QMainWindow):
    def __init__(self, instance_checker):
        super().__init__()
        
        self.instance_checker = instance_checker
        self.instance_checker.signals.show_window.connect(self.handle_show_window_signal)
        
        self.setWindowTitle("volt-gui")
        self.setMinimumSize(640, 480)
        
        self.use_system_tray = True
        self.start_minimized = False
        self.restore_cpu_on_close = True
        
        self.governor_actions = {}
        self.scheduler_actions = {}
        
        self.process = None
        self.is_process_running = False
        self.scheduler_process = None
        self.current_scheduler = None
        self.cpu_settings_applied = False
        self.cpu_governor_labels = {}
        
        self.setAttribute(Qt.WA_DontShowOnScreen, True)
        
        self.apply_dark_theme()
        self.setup_ui()
        self.setup_system_tray()
        self.setup_refresh_timer()
        self.load_saved_settings()
        
        self.app = QApplication.instance()
        self.setAttribute(Qt.WA_DontShowOnScreen, False)
        
        if not self.start_minimized:
            QTimer.singleShot(0, self.show_and_activate)
        else:
            self.tray_icon.showMessage(
                "volt-gui",
                "Application is running in the system tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
    
    def setup_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        self.setup_cpu_tab()
        self.setup_gpu_tab()
        self.setup_launch_options_tab()
        self.setup_extras_tab()
        
        self.options_tab = OptionsTab(self.tab_widget, self)
        self.tab_widget.addTab(self.options_tab, "Options")
        
        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(central_widget)
    
    def setup_cpu_tab(self):
        cpu_tab, self.cpu_widgets = CPUManager.create_cpu_tab()

        self.gov_combo = self.cpu_widgets['gov_combo']
        self.sched_combo = self.cpu_widgets['sched_combo']
        self.cpu_apply_button = self.cpu_widgets['cpu_apply_button']
        self.governors_layout = self.cpu_widgets['governors_layout']
        self.current_sched_value = self.cpu_widgets['current_sched_value']
        self.sched_status_layout = self.cpu_widgets['sched_status_layout']

        self.cpu_apply_button.clicked.connect(
            lambda: self.button_clicked_animation(self.cpu_apply_button)
        )

        try:
            self.original_governor = CPUManager.get_current_governor()
        except Exception as e:
            self.log_to_terminal(f"Error getting current governor: {e}")
            self.original_governor = "powersave"
        
        self.schedulers = ["none", "scx_bpfland", "scx_flash", "scx_lavd", "scx_rusty"]

        self.refresh_cpu_governors()
        self.refresh_current_scheduler()
        
        self.tab_widget.addTab(cpu_tab, "CPU")
    
    def setup_gpu_tab(self):
        gpu_tab, gpu_subtabs, self.mesa_widgets, self.nvidia_widgets = GPULaunchManager.create_gpu_tab()

        self.mesa_widgets['mesa_apply_button'].clicked.connect(
            lambda: self.button_clicked_animation(self.mesa_widgets['mesa_apply_button'])
        )
        self.nvidia_widgets['nvidia_apply_button'].clicked.connect(
            lambda: self.button_clicked_animation(self.nvidia_widgets['nvidia_apply_button'])
        )
        GPULaunchManager.render_selector_widgets['render_selector_apply_button'].clicked.connect(
            lambda: self.button_clicked_animation(GPULaunchManager.render_selector_widgets['render_selector_apply_button'])
        )

        self.mesa_apply_button = self.mesa_widgets['mesa_apply_button']
        self.nvidia_apply_button = self.nvidia_widgets['nvidia_apply_button']
        self.render_selector_apply_button = GPULaunchManager.render_selector_widgets['render_selector_apply_button']
        self.mesa_fake_gl_combo = self.mesa_widgets['mesa_fake_gl_combo']
        self.mesa_fake_glsl_combo = self.mesa_widgets['mesa_fake_glsl_combo']
        self.mesa_fake_vk_combo = self.mesa_widgets['mesa_fake_vk_combo']
        
        self.tab_widget.addTab(gpu_tab, "GPU")
    
    def setup_launch_options_tab(self):
        launch_options_tab = GPULaunchManager.create_launch_options_tab()
        
        GPULaunchManager.launch_options_widgets['apply_button'].clicked.connect(
            lambda: self.button_clicked_animation(GPULaunchManager.launch_options_widgets['apply_button'])
        )
        
        self.launch_options_apply_button = GPULaunchManager.launch_options_widgets['apply_button']
        
        self.tab_widget.addTab(launch_options_tab, "Launch Options")
    
    def setup_extras_tab(self):
        extras_tab, extras_subtabs = ExtrasManager.create_extras_tab()
        self.tab_widget.addTab(extras_tab, "Extras")
        
    def setup_refresh_timer(self):
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_cpu_governors)
        self.refresh_timer.timeout.connect(self.refresh_current_scheduler)
        self.refresh_timer.start(5000)
    
    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("preferences-system"))
        
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_and_activate)
        tray_menu.addAction(show_action)
        
        governor_menu = QMenu("CPU Governor", self)
        self.governor_actions = {}
        for governor in CPUManager.get_available_governors():
            action = QAction(governor, self, checkable=True)
            action.triggered.connect(lambda checked, g=governor: self.handle_governor_selection(g))
            self.governor_actions[governor] = action
            governor_menu.addAction(action)
        tray_menu.addMenu(governor_menu)
        
        scheduler_menu = QMenu("Pluggable CPU Scheduler", self)
        self.scheduler_actions = {}
        for scheduler in CPUManager.get_available_schedulers():
            action = QAction(scheduler, self, checkable=True)
            action.triggered.connect(lambda checked, s=scheduler: self.handle_scheduler_selection(s))
            self.scheduler_actions[scheduler] = action
            scheduler_menu.addAction(action)
        tray_menu.addMenu(scheduler_menu)
        
        apply_cpu_action = QAction("Apply CPU Settings", self)
        apply_cpu_action.triggered.connect(self.apply_cpu_settings)
        tray_menu.addAction(apply_cpu_action)
        
        tray_menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        self.update_tray_menu_state()
    
    def show_and_activate(self):
        self.showMaximized()
        self.activateWindow()
        self.raise_()
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show_and_activate()
    
    def closeEvent(self, event):
        if hasattr(self, '_quitting') and self._quitting:
            event.accept()
            return
        
        if not hasattr(self, 'use_system_tray') or self.use_system_tray:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "volt-gui",
                "Application is still running in the system tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            self._quitting = True
            self.quit_application()
            event.accept()
    
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            event.ignore()
            self.hide()
            return
        
        super().changeEvent(event)
    
    def load_saved_settings(self):
        self.log_to_terminal("Loading settings from config file...")
        success = ConfigManager.load_settings(self.cpu_widgets, self.mesa_widgets, self.nvidia_widgets)
        if not success:
            self.log_to_terminal("No config file found, initializing with default settings")
    
    def save_settings(self):
        self.log_to_terminal("Saving settings to config file...")
        ConfigManager.save_settings(self.cpu_widgets, self.mesa_widgets, self.nvidia_widgets)
    
    def apply_cpu_settings(self):
        if self.is_process_running:
            self.log_to_terminal("A process is already running. Please wait.")
            return
        
        governor = self.gov_combo.currentText()
        scheduler = self.sched_combo.currentText()
        
        self.log_to_terminal(f"Applying CPU governor: {governor}")
        self.log_to_terminal(f"Applying CPU scheduler: {scheduler}")
        
        self.animate_button_click(self.cpu_apply_button)
        self.cpu_apply_button.setEnabled(False)
        
        apply_script, _ = CPUManager.create_cpu_scripts()
        self.process = CPUManager.write_and_execute_script(
            apply_script,
            "ocpu_apply",
            [governor, scheduler]
        )
        self.process.finished.connect(self.on_process_finished)
        self.is_process_running = True
        self.cpu_settings_applied = True
        
        if scheduler != "none":
            self.current_scheduler = scheduler
        else:
            self.current_scheduler = None
        
        self.save_settings()
    
    def reset_cpu_governor(self):
        if hasattr(self, 'original_governor'):
            self.log_to_terminal(f"Resetting CPU governor to original: {self.original_governor}")
            _, reset_script = CPUManager.create_cpu_scripts()
            process = CPUManager.write_and_execute_script(
                reset_script,
                "ocpu_reset",
                [self.original_governor]
            )
            process.waitForFinished()
            self.current_scheduler = None
    
    def terminate_current_scheduler(self):
        if not self.current_scheduler:
            return
        
        self.log_to_terminal("Terminating SCX schedulers...")
        try:
            subprocess.run(["pkill", "-f", "^scx_"], check=False)
            self.current_scheduler = None
        except Exception as e:
            self.log_to_terminal(f"Error terminating schedulers: {e}")
    
    def refresh_cpu_governors(self):
        CPUManager.refresh_cpu_governors(self.governors_layout, self.cpu_governor_labels)
        if hasattr(self, 'governor_actions'):
            self.update_tray_menu_state()
    
    def refresh_current_scheduler(self):
        self.current_scheduler = CPUManager.refresh_current_scheduler(
            self.current_sched_value,
            self.schedulers,
            self.sched_combo
        )
        if hasattr(self, 'governor_actions'):
            self.update_tray_menu_state()
    
    def apply_gpu_settings(self):
        if self.is_process_running:
            self.log_to_terminal("A process is already running. Please wait.")
            return
        
        current_subtab_index = self.tab_widget.widget(1).layout().itemAt(0).widget().currentIndex()
        
        if current_subtab_index == 0:
            self.animate_button_click(self.mesa_apply_button)
            self.mesa_apply_button.setEnabled(False)
            self.nvidia_apply_button.setEnabled(False)
            self.render_selector_apply_button.setEnabled(False)
        elif current_subtab_index == 1:
            self.animate_button_click(self.nvidia_apply_button)
            self.mesa_apply_button.setEnabled(False)
            self.nvidia_apply_button.setEnabled(False)
            self.render_selector_apply_button.setEnabled(False)
        else:
            self.animate_button_click(self.render_selector_apply_button)
            self.mesa_apply_button.setEnabled(False)
            self.nvidia_apply_button.setEnabled(False)
            self.render_selector_apply_button.setEnabled(False)
        
        self.log_to_terminal("Applying all GPU settings (Mesa, NVIDIA, Render Selector, and Launch Options)...")
        
        try:
            script_path = GPULaunchManager.write_volt_script_with_all_settings(
                self.mesa_widgets,
                self.nvidia_widgets
            )
            
            self.log_to_terminal(f"GPU settings and Launch Options saved to {script_path}")
            
            self.tray_icon.showMessage(
                "volt-gui",
                f"All GPU settings and Launch Options applied and saved to {script_path}",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            
            self.save_settings()
            
        except Exception as e:
            self.log_to_terminal(f"Error applying GPU settings: {e}")
            
            self.tray_icon.showMessage(
                "volt-gui",
                f"Error applying GPU settings: {e}",
                QSystemTrayIcon.MessageIcon.Critical,
                2000
            )
        finally:
            self.mesa_apply_button.setEnabled(True)
            self.nvidia_apply_button.setEnabled(True)
            self.render_selector_apply_button.setEnabled(True)
    
    def on_process_finished(self, exit_code, exit_status):
        self.is_process_running = False
        self.cpu_apply_button.setEnabled(True)
        self.mesa_apply_button.setEnabled(True)
        self.nvidia_apply_button.setEnabled(True)
        
        self.refresh_cpu_governors()
        self.refresh_current_scheduler()
        
        self.tray_icon.showMessage(
            "volt-gui",
            "Settings have been applied successfully" if exit_code == 0 else "Error applying settings",
            QSystemTrayIcon.MessageIcon.Information if exit_code == 0 else QSystemTrayIcon.MessageIcon.Critical,
            2000
        )
        
        if self.process:
            self.process.deleteLater()
            self.process = None
    
    def apply_dark_theme(self):
        ThemeManager.apply_theme(QApplication.instance())

    def create_section_header(self, text):
        label = QLabel(text)
        label.setProperty("isHeader", "true")
        return label
    
    def animate_button_click(self, button):
        original_size = button.size()
        
        shrink_anim = QPropertyAnimation(button, b"size")
        shrink_anim.setDuration(100)
        shrink_anim.setStartValue(original_size)
        shrink_anim.setEndValue(QSize(original_size.width() * 0.95, original_size.height() * 0.95))
        shrink_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        grow_anim = QPropertyAnimation(button, b"size")
        grow_anim.setDuration(100)
        grow_anim.setStartValue(QSize(original_size.width() * 0.95, original_size.height() * 0.95))
        grow_anim.setEndValue(original_size)
        grow_anim.setEasingCurve(QEasingCurve.OutBounce)
        
        shrink_anim.start()
        shrink_anim.finished.connect(grow_anim.start)

    def button_clicked_animation(self, button):
        self.animate_button_click(button)
        
        if button in [self.mesa_apply_button, self.nvidia_apply_button, self.render_selector_apply_button, self.launch_options_apply_button]:
            self.apply_gpu_settings()
        elif button == self.cpu_apply_button:
            self.apply_cpu_settings()

    def apply_all_settings(self):
        current_tab_index = self.tab_widget.currentIndex()
        
        if current_tab_index == 0:
            self.apply_cpu_settings()
        elif current_tab_index == 1:
            self.apply_gpu_settings()
    
    def log_to_terminal(self, text):
        print(text)
    
    def quit_application(self):
        self._quitting = True
        
        if self.cpu_settings_applied and self.restore_cpu_on_close:
            self.log_to_terminal("Resetting CPU settings to original state...")
            self.reset_cpu_governor()
            self.terminate_current_scheduler()
        else:
            if not self.restore_cpu_on_close:
                self.log_to_terminal("CPU settings restore is disabled, skipping reset...")
            else:
                self.log_to_terminal("No CPU settings were applied, skipping reset...")
        
        self.save_settings()
        
        self.tray_icon.showMessage(
            "volt-gui",
            "Application is closing...",
            QSystemTrayIcon.MessageIcon.Information,
            1000
        )
        
        self.instance_checker.cleanup()
        QApplication.quit()

    def handle_show_window_signal(self):
        self.show_and_activate()

    def update_tray_menu_state(self):
        if not hasattr(self, 'governor_actions') or not hasattr(self, 'scheduler_actions'):
            return
        
        current_governor = self.gov_combo.currentText()
        for governor, action in self.governor_actions.items():
            action.setChecked(governor == current_governor)
        
        current_scheduler = self.sched_combo.currentText()
        for scheduler, action in self.scheduler_actions.items():
            action.setChecked(scheduler == current_scheduler)

    def handle_governor_selection(self, governor):
        self.gov_combo.setCurrentText(governor)
        self.update_tray_menu_state()
        self.save_settings()

    def handle_scheduler_selection(self, scheduler):
        self.sched_combo.setCurrentText(scheduler)
        self.update_tray_menu_state()
        self.save_settings()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "System Tray", "System tray is not available on this system")
        sys.exit(1)
    
    app.setQuitOnLastWindowClosed(False)
    
    if len(sys.argv) > 1:
        scheduler_name = sys.argv[0].split('/')[-1]
        if scheduler_name in ["scx_bpfland", "scx_flash", "scx_lavd", "scx_rusty"]:
            result = subprocess.run([scheduler_name] + sys.argv[1:])
            sys.exit(result.returncode)
    
    instance_checker = SingleInstanceChecker()
    if instance_checker.is_already_running():
        QMessageBox.information(None, "volt-gui", "The application is already running and will be displayed.")
        sys.exit(0)
    
    main_window = MainWindow(instance_checker)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()