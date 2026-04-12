#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Internationalization (i18n) module for NW.js Automator.
Provides locale detection, fallback, and translation loading.
"""

import json
import locale
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

TRANSLATIONS_DIR = Path(__file__).parent
SUPPORTED_LOCALES = {
    "en": "English",
    "ja": "Japanese",
    "es": "Spanish",
    "fr": "French",
}
DEFAULT_LOCALE = "en"


class I18n:
    """Translation manager with auto-detection and fallback."""

    def __init__(self, locale_code: Optional[str] = None):
        self._strings: dict = {}
        self._fallback: dict = {}
        self._locale = locale_code or self._detect_locale()

        # Always load English as fallback
        self._fallback = self._load_locale(DEFAULT_LOCALE)
        # Load requested locale on top
        self._strings = self._load_locale(self._locale)

    @property
    def current_locale(self) -> str:
        return self._locale

    @staticmethod
    def available_locales() -> dict:
        """Return dict of locale_code -> display_name for installed translations."""
        found = {}
        for code, name in SUPPORTED_LOCALES.items():
            if (TRANSLATIONS_DIR / f"{code}.json").exists():
                found[code] = name
        return found

    def set_locale(self, locale_code: str):
        """Switch locale at runtime."""
        self._locale = locale_code
        self._strings = self._load_locale(locale_code)

    def t(self, key: str) -> str:
        """Translate *key*, falling back to English then to the key itself."""
        return self._strings.get(key) or self._fallback.get(key) or key

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------
    @staticmethod
    def _detect_locale() -> str:
        """Best-effort detection of the system language."""
        try:
            system_locale = locale.getdefaultlocale()[0]  # e.g. "en_US"
            if system_locale:
                lang = system_locale.split("_")[0]
                if lang in SUPPORTED_LOCALES:
                    return lang
        except Exception:
            pass
        return DEFAULT_LOCALE

    @staticmethod
    def _load_locale(locale_code: str) -> dict:
        path = TRANSLATIONS_DIR / f"{locale_code}.json"
        if not path.exists():
            logger.warning("Translation file not found: %s – using fallback", path)
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error("Failed to load translation %s: %s", path, exc)
            return {}
