# Contributing to NW.js Automator

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.10+
- Git

### Setup

```bash
git clone https://github.com/aeagisdev/rpgm-nwjs-automator.git
cd rpgm-nwjs-automator
pip install -r requirements.txt
pip install PySide6  # optional, for GUI development
```

### Running the Tool

```bash
# CLI interactive mode
python nwjs_automator.py --interactive

# GUI mode (requires PySide6 or PyQt6)
python gui_interface.py
```

### Running Tests

```bash
# Full test suite
python -m unittest test_suite -v

# Single test
python -m unittest test_suite.TestNWJSAutomator.test_backup_creation -v
```

All tests must pass before submitting a pull request.

## How to Contribute

### Reporting Bugs

Open an issue on [GitHub Issues](https://github.com/aeagisdev/rpgm-nwjs-automator/issues) with:

- Steps to reproduce
- Expected vs actual behavior
- NW.js version and OS
- RPG Maker version (MV or MZ)
- Python version (`python --version`)

### Submitting Changes

1. Fork the repository
2. Create a feature branch from `main`: `git checkout -b feature/your-feature`
3. Make your changes
4. Run the test suite: `python -m unittest test_suite -v`
5. Commit with a clear message describing the change
6. Push and open a pull request against `main`

### Game Compatibility Reports

Testing with different games and NW.js versions is extremely valuable. If you test a game, open an issue or PR with:

- Game name and RPG Maker version (MV/MZ)
- NW.js version used
- OS and architecture
- Result (success/failure) and any issues encountered

## Project Structure

| File | Purpose |
|------|---------|
| `nwjs_automator.py` | Core automation engine and CLI |
| `gui_interface.py` | PySide6/PyQt6 graphical interface |
| `batch_processor.py` | Multi-game parallel processing |
| `plugin_system.py` | Plugin framework and manager |
| `translations/i18n.py` | Internationalization module |
| `translations/*.json` | Translation files |
| `plugins/` | Plugin directory |
| `test_suite.py` | Test suite (unittest) |

## Code Guidelines

### Style

- Follow PEP 8 conventions
- Use type hints for function signatures
- Keep imports organized: stdlib, third-party, local

### GUI Development

The GUI supports both PySide6 (preferred) and PyQt6 as backends. When writing GUI code:

- Import from the conditional block at the top of `gui_interface.py` -- never import Qt directly
- Test with PySide6 at minimum
- Use the `build_stylesheet()` function for theming -- do not hardcode colors
- Long operations must run in a `QThread` to keep the UI responsive

### Plugin Development

Create plugins by subclassing `PluginInterface` in the `plugins/` directory:

```python
from plugin_system import PluginInterface

class MyPlugin(PluginInterface):
    def __init__(self):
        super().__init__()
        self.name = "My Plugin"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "What it does"

    def get_hooks(self):
        return {
            "pre_process_game": self.before,
            "post_process_game": self.after,
        }
```

Available hooks: `pre_process_game`, `post_process_game`, `validate_package_json`, `pre_cleanup`, `file_optimization`.

### Adding Translations

1. Copy `translations/en.json` to `translations/<lang_code>.json`
2. Translate all values (keep keys unchanged)
3. Add the locale to `SUPPORTED_LOCALES` in `translations/i18n.py`
4. Test with: `python -c "from translations.i18n import I18n; i = I18n('<lang_code>'); print(i.t('welcome'))"`

## CI/CD

The project uses GitHub Actions:

- **CI Tests** (`ci.yml`): Runs the test suite on Ubuntu, Windows, and macOS with Python 3.10 and 3.12 on every push and PR
- **Build & Release** (`release.yml`): Builds standalone executables with PyInstaller for Windows x64, macOS ARM64, and Linux x64 when a version tag (`v*`) is pushed

### Creating a Release

Releases are automated. To publish:

```bash
git tag v2.x.x
git push origin v2.x.x
```

The workflow builds all platform artifacts and creates a GitHub Release automatically.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
