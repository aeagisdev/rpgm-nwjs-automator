"""
Sample Plugin for RPG Maker NW.js Automator
Demonstrates the class-based PluginInterface API.
"""

import sys
import logging
from pathlib import Path

# Allow imports when loaded from the plugins/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from plugin_system import PluginInterface

logger = logging.getLogger(__name__)


class SamplePlugin(PluginInterface):
    """A sample plugin that demonstrates the PluginInterface hooks."""

    def __init__(self):
        super().__init__()
        self.name = "Sample Plugin"
        self.version = "1.0.0"
        self.author = "AeagisDev"
        self.description = "A sample plugin demonstrating the plugin system"
        self.requires = []
        self.compatible_with = ["2.0.0", "2.1.0", "2.1.1"]

    def get_hooks(self):
        return {
            "pre_process_game": self.pre_process,
            "post_process_game": self.post_process,
            "validate_package_json": self.validate_game,
        }

    def pre_process(self, game_path: str) -> dict:
        """Called before game processing starts."""
        logger.info("Sample Plugin: pre-processing game at %s", game_path)
        return {"status": "success", "message": "Pre-processing completed"}

    def post_process(self, game_path: str, result: dict) -> dict:
        """Called after game processing completes."""
        status = "successful" if result.get("success") else "failed"
        logger.info("Sample Plugin: post-processing %s for %s", status, game_path)
        return {"status": "success", "message": "Post-processing completed"}

    def validate_game(self, package_json_data: dict) -> dict:
        """Called during game validation."""
        logger.info("Sample Plugin: validating package.json")
        return {"valid": True, "warnings": []}
