#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modern GUI Interface for NW.js Automator
Full-featured graphical interface with dark/light themes, drag-and-drop,
dashboard, batch processing, plugin management, and i18n support.
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# Qt imports – prefer PySide6, fall back to PyQt6
# ---------------------------------------------------------------------------
QT_BACKEND: Optional[str] = None
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFileDialog, QMessageBox, QProgressBar,
        QComboBox, QCheckBox, QGroupBox, QListWidget, QListWidgetItem,
        QFormLayout, QLineEdit, QTextEdit, QTabWidget, QStatusBar,
        QSplitter, QFrame, QSpinBox, QSystemTrayIcon, QMenu,
        QToolButton, QSizePolicy, QScrollArea
    )
    from PySide6.QtCore import Qt, QThread, Signal, QObject, QMimeData, QTimer, QSize
    from PySide6.QtGui import (
        QIcon, QFont, QColor, QPalette, QDragEnterEvent,
        QDropEvent, QAction, QPainter
    )
    QT_BACKEND = "PySide6"
except ImportError:
    try:
        from PyQt6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QLabel, QPushButton, QFileDialog, QMessageBox, QProgressBar,
            QComboBox, QCheckBox, QGroupBox, QListWidget, QListWidgetItem,
            QFormLayout, QLineEdit, QTextEdit, QTabWidget, QStatusBar,
            QSplitter, QFrame, QSpinBox, QSystemTrayIcon, QMenu,
            QToolButton, QSizePolicy, QScrollArea
        )
        from PyQt6.QtCore import Qt, QThread, QMimeData, QTimer, QSize
        from PyQt6.QtCore import pyqtSignal as Signal
        from PyQt6.QtGui import (
            QIcon, QFont, QColor, QPalette, QDragEnterEvent,
            QDropEvent, QAction, QPainter
        )
        QT_BACKEND = "PyQt6"
    except ImportError:
        QT_BACKEND = None

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
from nwjs_automator import NWJSAutomator
from batch_processor import BatchProcessor, BatchConfigManager
from plugin_system import PluginManager
from translations.i18n import I18n

logger = logging.getLogger(__name__)

# ===========================================================================
# Colour palettes
# ===========================================================================
DARK_PALETTE = {
    "bg": "#1e1e2e",
    "surface": "#282840",
    "surface2": "#313150",
    "accent": "#7c3aed",
    "accent_hover": "#6d28d9",
    "accent_light": "#a78bfa",
    "text": "#e2e2f0",
    "text_dim": "#9090b0",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "border": "#3f3f5f",
}
LIGHT_PALETTE = {
    "bg": "#f8f9fc",
    "surface": "#ffffff",
    "surface2": "#f0f1f5",
    "accent": "#7c3aed",
    "accent_hover": "#6d28d9",
    "accent_light": "#c4b5fd",
    "text": "#1e1e2e",
    "text_dim": "#6b7280",
    "success": "#16a34a",
    "warning": "#d97706",
    "error": "#dc2626",
    "border": "#e2e4ea",
}


def build_stylesheet(p: dict) -> str:
    """Generate a complete QSS stylesheet from a palette dict."""
    return f"""
    /* ── Global ─────────────────────────────────────────── */
    QMainWindow, QWidget {{
        background-color: {p['bg']};
        color: {p['text']};
        font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
        font-size: 13px;
    }}
    QLabel {{
        color: {p['text']};
    }}
    QLabel[class="dim"] {{
        color: {p['text_dim']};
    }}

    /* ── Tabs ───────────────────────────────────────────── */
    QTabWidget::pane {{
        border: 1px solid {p['border']};
        border-radius: 8px;
        background: {p['surface']};
        padding: 8px;
    }}
    QTabBar::tab {{
        background: {p['surface2']};
        color: {p['text_dim']};
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 500;
    }}
    QTabBar::tab:selected {{
        background: {p['accent']};
        color: #ffffff;
        font-weight: 600;
    }}
    QTabBar::tab:hover:!selected {{
        background: {p['border']};
    }}

    /* ── Group boxes ────────────────────────────────────── */
    QGroupBox {{
        border: 1px solid {p['border']};
        border-radius: 8px;
        margin-top: 14px;
        padding-top: 18px;
        background: {p['surface']};
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 6px;
        color: {p['accent_light']};
    }}

    /* ── Inputs ─────────────────────────────────────────── */
    QLineEdit, QTextEdit, QSpinBox, QComboBox {{
        background: {p['surface2']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 6px;
        padding: 7px 10px;
        selection-background-color: {p['accent']};
    }}
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border-color: {p['accent']};
    }}
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background: {p['surface']};
        color: {p['text']};
        border: 1px solid {p['border']};
        selection-background-color: {p['accent']};
    }}

    /* ── Buttons ────────────────────────────────────────── */
    QPushButton {{
        background: {p['surface2']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 6px;
        padding: 8px 18px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background: {p['border']};
    }}
    QPushButton:pressed {{
        background: {p['accent']};
        color: #ffffff;
    }}
    QPushButton[class="primary"] {{
        background: {p['accent']};
        color: #ffffff;
        border: none;
        font-weight: 600;
    }}
    QPushButton[class="primary"]:hover {{
        background: {p['accent_hover']};
    }}
    QPushButton[class="primary"]:disabled {{
        background: {p['border']};
        color: {p['text_dim']};
    }}
    QPushButton[class="danger"] {{
        background: {p['error']};
        color: #ffffff;
        border: none;
    }}

    /* ── Progress bar ──────────────────────────────────── */
    QProgressBar {{
        background: {p['surface2']};
        border: 1px solid {p['border']};
        border-radius: 6px;
        text-align: center;
        color: {p['text']};
        height: 22px;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {p['accent']}, stop:1 {p['accent_light']});
        border-radius: 5px;
    }}

    /* ── Lists ─────────────────────────────────────────── */
    QListWidget {{
        background: {p['surface2']};
        border: 1px solid {p['border']};
        border-radius: 6px;
        padding: 4px;
        color: {p['text']};
    }}
    QListWidget::item {{
        padding: 6px 10px;
        border-radius: 4px;
    }}
    QListWidget::item:selected {{
        background: {p['accent']};
        color: #ffffff;
    }}
    QListWidget::item:hover:!selected {{
        background: {p['border']};
    }}

    /* ── Check boxes ───────────────────────────────────── */
    QCheckBox {{
        spacing: 8px;
        color: {p['text']};
    }}
    QCheckBox::indicator {{
        width: 18px; height: 18px;
        border-radius: 4px;
        border: 2px solid {p['border']};
        background: {p['surface2']};
    }}
    QCheckBox::indicator:checked {{
        background: {p['accent']};
        border-color: {p['accent']};
    }}

    /* ── Scrollbar ──────────────────────────────────────── */
    QScrollBar:vertical {{
        background: {p['surface']};
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background: {p['border']};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    /* ── Status bar ──────────────────────────────────────── */
    QStatusBar {{
        background: {p['surface']};
        color: {p['text_dim']};
        border-top: 1px solid {p['border']};
        font-size: 12px;
    }}

    /* ── Frames ──────────────────────────────────────────── */
    QFrame[class="card"] {{
        background: {p['surface']};
        border: 1px solid {p['border']};
        border-radius: 10px;
        padding: 16px;
    }}
    """


# ===========================================================================
# Worker thread
# ===========================================================================
class WorkerSignals(QObject):
    progress = Signal(int, str)
    message = Signal(str, str)
    finished = Signal(dict)
    error = Signal(str)


class AutomatorWorker(QThread):
    """Runs NWJSAutomator.process_game in a background thread."""

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.signals = WorkerSignals()
        self._running = True

    def run(self):
        try:
            automator = NWJSAutomator(
                game_path=self.config["game_path"],
                nwjs_version=self.config["nwjs_version"],
                use_sdk=self.config["use_sdk"],
                executable_name=self.config["executable_name"],
                enable_devtools=self.config["enable_devtools"],
                platform_optimized=self.config["platform_optimized"],
                logging_level=self.config["logging_level"],
                config_profile=self.config.get("config_profile"),
                config_template=self.config.get("config_template"),
            )
            self.signals.progress.emit(10, "Validating game directory...")
            result = automator.process_game(create_backup=self.config["create_backup"])
            if result["success"]:
                self.signals.progress.emit(100, "Completed!")
                self.signals.finished.emit(result)
            else:
                self.signals.error.emit(result.get("error", "Unknown error"))
        except Exception as exc:
            self.signals.error.emit(str(exc))

    def stop(self):
        self._running = False


class BatchWorker(QThread):
    """Runs BatchProcessor in a background thread."""

    progress = Signal(int, str)
    message = Signal(str, str)
    finished = Signal(dict)

    def __init__(self, games: list, config: dict, max_workers: int = 2):
        super().__init__()
        self.games = games
        self.config = config
        self.max_workers = max_workers
        self._processor: Optional[BatchProcessor] = None

    def run(self):
        self._processor = BatchProcessor(max_workers=self.max_workers)
        self._processor.set_callbacks(
            progress_callback=lambda p, m: self.progress.emit(int(p), m),
            message_callback=lambda m, l: self.message.emit(m, l),
            completion_callback=lambda r: self.finished.emit(r),
        )
        for game_path in self.games:
            self._processor.add_game(game_path, self.config)
        self._processor.start_processing()
        # Block until the processor's internal threads finish
        self._processor.task_queue.join()

    def stop(self):
        if self._processor:
            self._processor.stop_processing()


# ===========================================================================
# Drag-and-drop list widget
# ===========================================================================
class DropListWidget(QListWidget):
    """QListWidget that accepts drag-and-dropped directories."""

    files_dropped = Signal(list)

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._placeholder = placeholder
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if Path(path).is_dir():
                paths.append(path)
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0 and self._placeholder:
            painter = QPainter(self.viewport())
            painter.setPen(QColor("#888"))
            painter.drawText(self.viewport().rect(), Qt.AlignmentFlag.AlignCenter, self._placeholder)
            painter.end()


# ===========================================================================
# Dashboard card helper
# ===========================================================================
def _card(title: str, value: str, color: str) -> QFrame:
    frame = QFrame()
    frame.setProperty("class", "card")
    frame.setFixedHeight(100)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 12, 16, 12)

    lbl_title = QLabel(title)
    lbl_title.setProperty("class", "dim")
    font_title = lbl_title.font()
    font_title.setPointSize(10)
    lbl_title.setFont(font_title)

    lbl_val = QLabel(value)
    lbl_val.setObjectName("card_value")
    font_val = lbl_val.font()
    font_val.setPointSize(20)
    font_val.setBold(True)
    lbl_val.setFont(font_val)
    lbl_val.setStyleSheet(f"color: {color};")

    layout.addWidget(lbl_title)
    layout.addWidget(lbl_val)
    return frame


# ===========================================================================
# Main window
# ===========================================================================
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self._dark = True
        self._i18n = I18n()
        self._plugin_mgr = PluginManager()
        self._stats = self._load_stats()

        self.setWindowTitle("NW.js Automator")
        self.setMinimumSize(960, 680)
        self.resize(1060, 740)

        # Central
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setCentralWidget(central)

        # ── Toolbar row ────────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(16, 10, 16, 6)

        app_title = QLabel("NW.js Automator")
        title_font = app_title.font()
        title_font.setPointSize(15)
        title_font.setBold(True)
        app_title.setFont(title_font)
        toolbar.addWidget(app_title)
        toolbar.addStretch()

        # Language selector
        self._lang_combo = QComboBox()
        self._lang_combo.setFixedWidth(130)
        for code, name in self._i18n.available_locales().items():
            self._lang_combo.addItem(name, code)
        idx = self._lang_combo.findData(self._i18n.current_locale)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)
        self._lang_combo.currentIndexChanged.connect(self._on_language_changed)
        toolbar.addWidget(QLabel("   "))
        toolbar.addWidget(self._lang_combo)

        # Theme toggle
        self._theme_btn = QPushButton("Light")
        self._theme_btn.setFixedWidth(80)
        self._theme_btn.clicked.connect(self._toggle_theme)
        toolbar.addWidget(self._theme_btn)

        root.addLayout(toolbar)

        # ── Tabs ───────────────────────────────────────────
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        self._build_dashboard_tab()
        self._build_process_tab()
        self._build_batch_tab()
        self._build_plugins_tab()
        self._build_settings_tab()

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage(self._t("ready"))

        # Workers
        self._worker: Optional[AutomatorWorker] = None
        self._batch_worker: Optional[BatchWorker] = None

        # Settings
        self._settings = self._load_settings()
        self._apply_settings()

        # Apply initial theme
        self._apply_theme()

    # ── helpers ──────────────────────────────────────────

    def _t(self, key: str) -> str:
        return self._i18n.t(key)

    def _apply_theme(self):
        pal = DARK_PALETTE if self._dark else LIGHT_PALETTE
        qss = build_stylesheet(pal)
        QApplication.instance().setStyleSheet(qss)
        self._theme_btn.setText("Light" if self._dark else "Dark")
        # refresh dashboard card colours
        self._refresh_dashboard()

    def _toggle_theme(self):
        self._dark = not self._dark
        self._apply_theme()

    def _on_language_changed(self, index: int):
        code = self._lang_combo.itemData(index)
        if code:
            self._i18n.set_locale(code)
            self._retranslate_ui()

    def _retranslate_ui(self):
        """Update visible text when locale changes."""
        self.tabs.setTabText(0, self._t("dashboard"))
        self.tabs.setTabText(1, self._t("process_game"))
        self.tabs.setTabText(2, self._t("batch_processing"))
        self.tabs.setTabText(3, self._t("plugins"))
        self.tabs.setTabText(4, self._t("settings"))
        self._status.showMessage(self._t("ready"))

    # ── stats persistence ────────────────────────────────

    @staticmethod
    def _stats_path() -> Path:
        return Path.home() / ".nwjs_automator_stats.json"

    def _load_stats(self) -> dict:
        defaults = {"games_processed": 0, "space_saved_mb": 0, "last_operation": "N/A"}
        try:
            p = self._stats_path()
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
        return defaults

    def _save_stats(self):
        try:
            with open(self._stats_path(), "w", encoding="utf-8") as f:
                json.dump(self._stats, f, indent=2)
        except Exception:
            pass

    # ==================================================================
    # TAB 0: Dashboard
    # ==================================================================
    def _build_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Welcome
        welcome = QLabel(self._t("welcome"))
        wf = welcome.font()
        wf.setPointSize(16)
        wf.setBold(True)
        welcome.setFont(wf)
        layout.addWidget(welcome)
        self._welcome_label = welcome

        # Cards row
        cards = QHBoxLayout()
        cards.setSpacing(14)
        pal = DARK_PALETTE if self._dark else LIGHT_PALETTE
        self._card_processed = _card(self._t("games_processed"), str(self._stats["games_processed"]), pal["accent"])
        self._card_saved = _card(self._t("space_saved"), f'{self._stats["space_saved_mb"]} MB', pal["success"])
        self._card_last = _card(self._t("last_operation"), self._stats["last_operation"], pal["text_dim"])
        cards.addWidget(self._card_processed)
        cards.addWidget(self._card_saved)
        cards.addWidget(self._card_last)
        layout.addLayout(cards)

        # Recent log
        log_group = QGroupBox(self._t("log"))
        log_lay = QVBoxLayout(log_group)
        self._dash_log = QTextEdit()
        self._dash_log.setReadOnly(True)
        self._dash_log.setMaximumHeight(260)
        log_lay.addWidget(self._dash_log)
        layout.addWidget(log_group)
        layout.addStretch()

        self.tabs.addTab(tab, self._t("dashboard"))

    def _refresh_dashboard(self):
        pal = DARK_PALETTE if self._dark else LIGHT_PALETTE
        self._card_processed.findChild(QLabel, "card_value").setText(str(self._stats["games_processed"]))
        self._card_processed.findChild(QLabel, "card_value").setStyleSheet(f"color: {pal['accent']};")
        self._card_saved.findChild(QLabel, "card_value").setText(f'{self._stats["space_saved_mb"]} MB')
        self._card_saved.findChild(QLabel, "card_value").setStyleSheet(f"color: {pal['success']};")
        self._card_last.findChild(QLabel, "card_value").setText(self._stats["last_operation"])
        self._card_last.findChild(QLabel, "card_value").setStyleSheet(f"color: {pal['text_dim']};")

    # ==================================================================
    # TAB 1: Process single game
    # ==================================================================
    def _build_process_tab(self):
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(tab)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # ── Game path ──────────────────────────────────────
        gp_group = QGroupBox(self._t("select_game"))
        gp_lay = QHBoxLayout(gp_group)
        self._game_path = QLineEdit()
        self._game_path.setPlaceholderText(self._t("drag_drop_hint"))
        self._game_path.setAcceptDrops(True)
        browse = QPushButton(self._t("browse"))
        browse.clicked.connect(self._browse_game)
        gp_lay.addWidget(self._game_path, 1)
        gp_lay.addWidget(browse)
        layout.addWidget(gp_group)

        # ── Configuration ──────────────────────────────────
        cfg_group = QGroupBox(self._t("settings"))
        cfg_form = QFormLayout(cfg_group)
        cfg_form.setSpacing(10)

        self._exe_name = QLineEdit("Game")
        cfg_form.addRow(self._t("executable_name"), self._exe_name)

        self._version_combo = QComboBox()
        self._version_combo.addItems([
            "v0.29.4 – Maximum compatibility",
            "v0.49.2 – Balanced (recommended)",
            "v0.72.0 – Modern stable",
            "v0.90.0 – Latest stable",
        ])
        self._version_combo.setCurrentIndex(1)
        cfg_form.addRow(self._t("nwjs_version"), self._version_combo)

        self._sdk_check = QCheckBox()
        cfg_form.addRow(self._t("use_sdk"), self._sdk_check)

        self._devtools_check = QCheckBox()
        cfg_form.addRow(self._t("enable_devtools"), self._devtools_check)

        self._backup_check = QCheckBox()
        self._backup_check.setChecked(True)
        cfg_form.addRow(self._t("create_backup"), self._backup_check)

        self._platform_check = QCheckBox()
        self._platform_check.setChecked(True)
        cfg_form.addRow(self._t("platform_optimized"), self._platform_check)

        self._profile_combo = QComboBox()
        self._profile_combo.addItems(["default", "development", "production", "compatibility", "modern"])
        cfg_form.addRow(self._t("config_profiles"), self._profile_combo)

        self._template_combo = QComboBox()
        self._template_combo.addItems(["(none)", "minimal", "debug", "multilingual"])
        cfg_form.addRow(self._t("config_templates"), self._template_combo)

        self._log_level_combo = QComboBox()
        self._log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self._log_level_combo.setCurrentIndex(1)
        cfg_form.addRow(self._t("logging_level"), self._log_level_combo)

        layout.addWidget(cfg_group)

        # ── Progress ───────────────────────────────────────
        prog_group = QGroupBox("Progress")
        prog_lay = QVBoxLayout(prog_group)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        prog_lay.addWidget(self._progress)

        self._progress_label = QLabel(self._t("ready"))
        prog_lay.addWidget(self._progress_label)

        btn_row = QHBoxLayout()
        self._start_btn = QPushButton(self._t("start"))
        self._start_btn.setProperty("class", "primary")
        self._start_btn.clicked.connect(self._start_process)
        self._stop_btn = QPushButton(self._t("stop"))
        self._stop_btn.setProperty("class", "danger")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_process)
        btn_row.addWidget(self._start_btn)
        btn_row.addWidget(self._stop_btn)
        btn_row.addStretch()
        prog_lay.addLayout(btn_row)

        layout.addWidget(prog_group)

        # ── Log ────────────────────────────────────────────
        log_group = QGroupBox(self._t("log"))
        log_lay = QVBoxLayout(log_group)
        self._proc_log = QTextEdit()
        self._proc_log.setReadOnly(True)
        self._proc_log.setMaximumHeight(200)
        log_lay.addWidget(self._proc_log)
        layout.addWidget(log_group)

        layout.addStretch()
        self.tabs.addTab(scroll, self._t("process_game"))

    # ==================================================================
    # TAB 2: Batch Processing
    # ==================================================================
    def _build_batch_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # ── Game list with drag-and-drop ───────────────────
        list_group = QGroupBox(self._t("batch_processing"))
        list_lay = QVBoxLayout(list_group)

        self._batch_list = DropListWidget(self._t("drag_drop_hint"))
        self._batch_list.files_dropped.connect(self._on_batch_drop)
        list_lay.addWidget(self._batch_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton(self._t("add_games"))
        add_btn.clicked.connect(self._batch_add)
        rm_btn = QPushButton(self._t("remove_selected"))
        rm_btn.clicked.connect(self._batch_remove)
        clr_btn = QPushButton(self._t("clear_all"))
        clr_btn.clicked.connect(self._batch_clear)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(rm_btn)
        btn_row.addWidget(clr_btn)
        btn_row.addStretch()
        list_lay.addLayout(btn_row)
        layout.addWidget(list_group)

        # ── Options ────────────────────────────────────────
        opt_group = QGroupBox(self._t("settings"))
        opt_lay = QFormLayout(opt_group)
        self._batch_workers_spin = QSpinBox()
        self._batch_workers_spin.setRange(1, 8)
        self._batch_workers_spin.setValue(2)
        opt_lay.addRow("Max parallel workers", self._batch_workers_spin)
        self._batch_backup_check = QCheckBox()
        self._batch_backup_check.setChecked(True)
        opt_lay.addRow(self._t("create_backup"), self._batch_backup_check)
        layout.addWidget(opt_group)

        # ── Progress ───────────────────────────────────────
        prog_group = QGroupBox("Batch Progress")
        prog_lay = QVBoxLayout(prog_group)
        self._batch_progress = QProgressBar()
        self._batch_progress.setRange(0, 100)
        prog_lay.addWidget(self._batch_progress)
        self._batch_status = QLabel(self._t("ready"))
        prog_lay.addWidget(self._batch_status)

        row = QHBoxLayout()
        self._batch_start_btn = QPushButton(self._t("process_all"))
        self._batch_start_btn.setProperty("class", "primary")
        self._batch_start_btn.clicked.connect(self._batch_start)
        self._batch_stop_btn = QPushButton(self._t("stop"))
        self._batch_stop_btn.setProperty("class", "danger")
        self._batch_stop_btn.setEnabled(False)
        self._batch_stop_btn.clicked.connect(self._batch_stop)
        row.addWidget(self._batch_start_btn)
        row.addWidget(self._batch_stop_btn)
        row.addStretch()
        prog_lay.addLayout(row)
        layout.addWidget(prog_group)

        # ── Batch log ──────────────────────────────────────
        blog_group = QGroupBox(self._t("log"))
        blog_lay = QVBoxLayout(blog_group)
        self._batch_log = QTextEdit()
        self._batch_log.setReadOnly(True)
        self._batch_log.setMaximumHeight(180)
        blog_lay.addWidget(self._batch_log)
        layout.addWidget(blog_group)

        layout.addStretch()
        self.tabs.addTab(tab, self._t("batch_processing"))

    # ==================================================================
    # TAB 3: Plugins
    # ==================================================================
    def _build_plugins_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Discover
        disc_group = QGroupBox(self._t("plugin_manager"))
        disc_lay = QVBoxLayout(disc_group)
        self._plugin_list = QListWidget()
        disc_lay.addWidget(self._plugin_list)

        btn_row = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_plugins)
        load_btn = QPushButton("Load Selected")
        load_btn.setProperty("class", "primary")
        load_btn.clicked.connect(self._load_selected_plugin)
        unload_btn = QPushButton("Unload Selected")
        unload_btn.clicked.connect(self._unload_selected_plugin)
        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(load_btn)
        btn_row.addWidget(unload_btn)
        btn_row.addStretch()
        disc_lay.addLayout(btn_row)
        layout.addWidget(disc_group)

        # Info
        info_group = QGroupBox("Plugin Details")
        info_lay = QVBoxLayout(info_group)
        self._plugin_info = QTextEdit()
        self._plugin_info.setReadOnly(True)
        self._plugin_info.setMaximumHeight(180)
        info_lay.addWidget(self._plugin_info)
        layout.addWidget(info_group)

        layout.addStretch()
        self.tabs.addTab(tab, self._t("plugins"))

        # Initial scan
        QTimer.singleShot(200, self._refresh_plugins)

    # ==================================================================
    # TAB 4: Settings
    # ==================================================================
    def _build_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        gen_group = QGroupBox(self._t("settings"))
        gen_lay = QFormLayout(gen_group)

        self._auto_update_check = QCheckBox()
        self._auto_update_check.setChecked(True)
        gen_lay.addRow(self._t("auto_update"), self._auto_update_check)

        self._save_logs_check = QCheckBox()
        self._save_logs_check.setChecked(True)
        gen_lay.addRow(self._t("save_logs"), self._save_logs_check)

        layout.addWidget(gen_group)

        btn_row = QHBoxLayout()
        save_btn = QPushButton(self._t("save_settings"))
        save_btn.setProperty("class", "primary")
        save_btn.clicked.connect(self._save_settings)
        reset_btn = QPushButton(self._t("reset_defaults"))
        reset_btn.clicked.connect(self._reset_settings)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(reset_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # About section
        about_group = QGroupBox(self._t("about"))
        about_lay = QVBoxLayout(about_group)
        about_text = QLabel(
            "<b>NW.js Automator for RPG Maker MV</b> v2.1.1<br>"
            "Copyright 2025 Andrea Giuseppe Santagati<br>"
            "Licensed under the MIT License<br><br>"
            '<a href="https://github.com/aeagisdev/rpgm-nwjs-automator">GitHub Repository</a>'
        )
        about_text.setOpenExternalLinks(True)
        about_text.setWordWrap(True)
        about_lay.addWidget(about_text)
        layout.addWidget(about_group)

        layout.addStretch()
        self.tabs.addTab(tab, self._t("settings"))

    # ==================================================================
    # Actions – single game
    # ==================================================================
    def _browse_game(self):
        d = QFileDialog.getExistingDirectory(self, self._t("select_game"))
        if d:
            self._game_path.setText(d)

    def _get_config(self) -> dict:
        ver_text = self._version_combo.currentText()
        version = ver_text.split()[0]  # e.g. "v0.49.2"
        tmpl = self._template_combo.currentText()
        return {
            "game_path": self._game_path.text().strip(),
            "executable_name": self._exe_name.text().strip() or "Game",
            "nwjs_version": version,
            "use_sdk": self._sdk_check.isChecked(),
            "enable_devtools": self._devtools_check.isChecked(),
            "create_backup": self._backup_check.isChecked(),
            "platform_optimized": self._platform_check.isChecked(),
            "logging_level": self._log_level_combo.currentText(),
            "config_profile": self._profile_combo.currentText(),
            "config_template": tmpl if tmpl != "(none)" else None,
        }

    def _start_process(self):
        cfg = self._get_config()
        if not cfg["game_path"]:
            QMessageBox.warning(self, "Error", self._t("select_game"))
            return
        if not Path(cfg["game_path"]).exists():
            QMessageBox.warning(self, "Error", "Game directory does not exist.")
            return

        answer = QMessageBox.question(
            self, self._t("confirm_update"),
            f"Update NW.js for:\n{cfg['game_path']}?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self._set_process_ui(False)
        self._proc_log.clear()
        self._progress.setValue(0)

        self._worker = AutomatorWorker(cfg)
        self._worker.signals.progress.connect(self._on_proc_progress)
        self._worker.signals.message.connect(self._on_proc_msg)
        self._worker.signals.finished.connect(self._on_proc_done)
        self._worker.signals.error.connect(self._on_proc_error)
        self._worker.start()

    def _stop_process(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.quit()
            self._worker.wait(3000)
        self._set_process_ui(True)
        self._log_msg(self._proc_log, "Stopped by user", "WARNING")

    def _set_process_ui(self, enabled: bool):
        self._start_btn.setEnabled(enabled)
        self._stop_btn.setEnabled(not enabled)

    def _on_proc_progress(self, val: int, msg: str):
        self._progress.setValue(val)
        self._progress_label.setText(msg)
        self._status.showMessage(msg)

    def _on_proc_msg(self, msg: str, level: str):
        self._log_msg(self._proc_log, msg, level)
        self._log_msg(self._dash_log, msg, level)

    def _on_proc_done(self, result: dict):
        self._set_process_ui(True)
        exe = result.get("game_executable", "?")
        self._log_msg(self._proc_log, f"Completed! Executable: {exe}", "SUCCESS")
        self._log_msg(self._dash_log, f"Completed! Executable: {exe}", "SUCCESS")
        self._stats["games_processed"] += 1
        self._stats["last_operation"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._save_stats()
        self._refresh_dashboard()
        QMessageBox.information(self, self._t("success"), f"{self._t('update_completed')}\n\n{exe}")

    def _on_proc_error(self, err: str):
        self._set_process_ui(True)
        self._log_msg(self._proc_log, f"Error: {err}", "ERROR")
        self._log_msg(self._dash_log, f"Error: {err}", "ERROR")
        QMessageBox.critical(self, self._t("error"), err)

    # ==================================================================
    # Actions – batch
    # ==================================================================
    def _on_batch_drop(self, paths: list):
        for p in paths:
            if not self._batch_has(p):
                self._batch_list.addItem(p)

    def _batch_has(self, path: str) -> bool:
        for i in range(self._batch_list.count()):
            if self._batch_list.item(i).text() == path:
                return True
        return False

    def _batch_add(self):
        d = QFileDialog.getExistingDirectory(self, self._t("select_game"))
        if d and not self._batch_has(d):
            self._batch_list.addItem(d)

    def _batch_remove(self):
        for item in self._batch_list.selectedItems():
            self._batch_list.takeItem(self._batch_list.row(item))

    def _batch_clear(self):
        self._batch_list.clear()

    def _batch_start(self):
        count = self._batch_list.count()
        if count == 0:
            QMessageBox.information(self, "Info", self._t("no_games"))
            return

        answer = QMessageBox.question(
            self, self._t("confirm_batch"),
            f"Process {count} games?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        games = [self._batch_list.item(i).text() for i in range(count)]

        # Build config from the main Process tab settings
        cfg = self._get_config()
        cfg["create_backup"] = self._batch_backup_check.isChecked()

        self._batch_start_btn.setEnabled(False)
        self._batch_stop_btn.setEnabled(True)
        self._batch_log.clear()
        self._batch_progress.setValue(0)

        self._batch_worker = BatchWorker(games, cfg, self._batch_workers_spin.value())
        self._batch_worker.progress.connect(self._on_batch_progress)
        self._batch_worker.message.connect(self._on_batch_msg)
        self._batch_worker.finished.connect(self._on_batch_done)
        self._batch_worker.start()

    def _batch_stop(self):
        if self._batch_worker and self._batch_worker.isRunning():
            self._batch_worker.stop()
            self._batch_worker.quit()
            self._batch_worker.wait(5000)
        self._batch_start_btn.setEnabled(True)
        self._batch_stop_btn.setEnabled(False)

    def _on_batch_progress(self, val: int, msg: str):
        self._batch_progress.setValue(val)
        self._batch_status.setText(msg)

    def _on_batch_msg(self, msg: str, level: str):
        self._log_msg(self._batch_log, msg, level)
        self._log_msg(self._dash_log, msg, level)

    def _on_batch_done(self, results: dict):
        self._batch_start_btn.setEnabled(True)
        self._batch_stop_btn.setEnabled(False)
        ok = sum(1 for r in results.values() if r.get("success"))
        fail = len(results) - ok
        self._log_msg(self._batch_log, f"Batch complete: {ok} succeeded, {fail} failed", "SUCCESS")
        self._stats["games_processed"] += ok
        self._stats["last_operation"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._save_stats()
        self._refresh_dashboard()
        QMessageBox.information(
            self, self._t("batch_processing"),
            f"Completed!\nSuccess: {ok}\nFailed: {fail}",
        )

    # ==================================================================
    # Actions – plugins
    # ==================================================================
    def _refresh_plugins(self):
        self._plugin_list.clear()
        discovered = self._plugin_mgr.discover_plugins()
        loaded = [p["name"] for p in self._plugin_mgr.get_loaded_plugins()]

        for name, info in discovered.items():
            prefix = "[Loaded] " if name in loaded else ""
            ver = info["info"].get("version", "?")
            desc = info["info"].get("description", "")
            item = QListWidgetItem(f"{prefix}{name} v{ver} – {desc}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self._plugin_list.addItem(item)

        if not discovered:
            self._plugin_info.setPlainText("No plugins found in plugins/ directory.")
        else:
            self._plugin_info.setPlainText(f"Found {len(discovered)} plugin(s). Select one to load/unload.")

    def _load_selected_plugin(self):
        item = self._plugin_list.currentItem()
        if not item:
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        try:
            self._plugin_mgr.load_plugin(name)
            self._plugin_info.setPlainText(f"Plugin '{name}' loaded successfully.")
            self._refresh_plugins()
        except Exception as exc:
            self._plugin_info.setPlainText(f"Failed to load '{name}': {exc}")

    def _unload_selected_plugin(self):
        item = self._plugin_list.currentItem()
        if not item:
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        if self._plugin_mgr.unload_plugin(name):
            self._plugin_info.setPlainText(f"Plugin '{name}' unloaded.")
        else:
            self._plugin_info.setPlainText(f"Plugin '{name}' is not loaded.")
        self._refresh_plugins()

    # ==================================================================
    # Actions – settings
    # ==================================================================
    @staticmethod
    def _settings_path() -> Path:
        return Path.home() / ".nwjs_automator_settings.json"

    def _load_settings(self) -> dict:
        defaults = {
            "auto_update": True,
            "save_logs": True,
            "dark_theme": True,
            "locale": "en",
            "last_game_path": "",
        }
        try:
            p = self._settings_path()
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
        return defaults

    def _apply_settings(self):
        self._auto_update_check.setChecked(self._settings.get("auto_update", True))
        self._save_logs_check.setChecked(self._settings.get("save_logs", True))
        self._dark = self._settings.get("dark_theme", True)
        if self._settings.get("last_game_path"):
            self._game_path.setText(self._settings["last_game_path"])

    def _save_settings(self):
        self._settings["auto_update"] = self._auto_update_check.isChecked()
        self._settings["save_logs"] = self._save_logs_check.isChecked()
        self._settings["dark_theme"] = self._dark
        self._settings["locale"] = self._i18n.current_locale
        self._settings["last_game_path"] = self._game_path.text().strip()
        try:
            with open(self._settings_path(), "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2)
            self._status.showMessage(self._t("save_settings") + " OK")
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _reset_settings(self):
        self._settings = self._load_settings.__func__(self)  # type: ignore
        self._apply_settings()
        self._status.showMessage(self._t("reset_defaults") + " OK")

    # ==================================================================
    # Utility
    # ==================================================================
    @staticmethod
    def _log_msg(widget: QTextEdit, msg: str, level: str):
        colors = {
            "DEBUG": "#888", "INFO": "#ccc", "WARNING": "#f59e0b",
            "ERROR": "#ef4444", "SUCCESS": "#22c55e",
        }
        color = colors.get(level, "#ccc")
        ts = datetime.now().strftime("%H:%M:%S")
        widget.append(f'<span style="color:{color};">[{ts}] [{level}] {msg}</span>')

    def closeEvent(self, event):
        self._save_settings()
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.quit()
            self._worker.wait(2000)
        if self._batch_worker and self._batch_worker.isRunning():
            self._batch_worker.stop()
            self._batch_worker.quit()
            self._batch_worker.wait(2000)
        event.accept()


# ===========================================================================
# Entry point
# ===========================================================================
def main():
    if QT_BACKEND is None:
        print("Error: PySide6 or PyQt6 is required for the GUI.")
        print("  pip install PySide6   (recommended)")
        print("  pip install PyQt6")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
