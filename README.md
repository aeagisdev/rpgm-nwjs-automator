# RPG Maker MV NW.js Automation Script v2.2.0

A Python tool that automates replacing RPG Maker MV/MZ game runtimes with modern NW.js installations, providing better performance, space savings, developer tools access, and a full graphical interface.

## What This Script Does

This script transforms your RPG Maker games by replacing their outdated runtime with modern NW.js versions.

### Key Benefits

- **Massive Space Savings**: Save 100-120MB per game (one NW.js serves all games)
- **Developer Tools**: Press F12 for debugging, modding, and game analysis
- **Better Performance**: Modern NW.js with latest bug fixes and optimizations
- **Custom Game Names**: Create personalized executable names
- **Zero Manual Work**: Fully automated with intelligent error handling
- **100% Safe**: Creates backups and validates everything before changes
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Automatic Rollback**: Self-healing system restores game if errors occur
- **Modern GUI**: Full graphical interface with dark/light themes and drag-and-drop
- **Batch Processing**: Process multiple games simultaneously with parallel workers
- **Plugin System**: Extend functionality with third-party plugins
- **Multi-Language**: English, Japanese, Spanish, and French interfaces

## Quick Start

### Method 1: Graphical Interface (Recommended)

```bash
pip install PySide6
python gui_interface.py
```

This launches the modern GUI with dashboard, drag-and-drop game selection, batch processing, plugin management, and dark/light theme support.

### Method 2: One-Click Launch

1. **Download** the latest release from [GitHub Releases](https://github.com/aeagisdev/rpgm-nwjs-automator/releases)
2. **Extract** anywhere convenient
3. **Double-click** the launcher:
   - **Windows**: `run_nwjs_automator_win.bat`
   - **Mac/Linux**: `run_nwjs_automator_unix_mac.sh`

The launcher checks Python, installs dependencies, and starts the interactive CLI.

### Method 3: Interactive CLI

```bash
python nwjs_automator.py --interactive
```

### Method 4: Command Line

```bash
python nwjs_automator.py --game-path "C:\Path\To\Your\Game" --executable-name "MyGame"
```

## Requirements

- **Python 3.6+**
- **Internet connection** (to download NW.js if not provided)
- **Required packages**: `requests`, `psutil` (`pip install -r requirements.txt`)
- **Optional**: `PySide6` or `PyQt6` (for GUI), `pywin32` (for Windows shortcuts)

## Graphical User Interface

The GUI (`gui_interface.py`) provides a modern, full-featured interface:

### Dashboard
- Live statistics: games processed, space saved, last operation
- Centralized operation log

### Process Tab
- Browse or type game directory path
- Configure all options: NW.js version, SDK/normal build, developer tools, backup, platform optimizations
- Select configuration profiles and templates
- Real-time progress bar and operation log

### Batch Processing Tab
- **Drag-and-drop** game folders directly into the list
- Add/remove games with buttons or file browser
- Configurable parallel worker threads (1-8)
- Per-batch backup toggle
- Aggregate progress and results reporting

### Plugins Tab
- Discover plugins from `plugins/` directory
- Load/unload plugins at runtime
- View plugin details (version, author, hooks)

### Settings Tab
- Auto-update toggle
- Log persistence toggle
- Dark/light theme switch (toolbar)
- Language selector (English, Japanese, Spanish, French)

### Themes
Toggle between dark and light themes at any time from the toolbar. The theme preference is saved between sessions.

## Batch Processing

### From the GUI

Drag-and-drop game folders into the Batch Processing tab, configure options, and click **Process All Games**. Games are processed in parallel with configurable worker threads.

### From the CLI

Create a batch file with game paths (one per line):

```
C:/Games/Game1
C:/Games/Game2
D:/Projects/MyRPGGame
```

### Programmatic Usage

```python
from batch_processor import BatchProcessor

processor = BatchProcessor(max_workers=2)
processor.add_game("/path/to/game", config)
processor.start_processing()
```

## Plugin System

Extend NW.js Automator with custom plugins.

### Creating a Plugin

Create a Python file in the `plugins/` directory that subclasses `PluginInterface`:

```python
from plugin_system import PluginInterface

class MyPlugin(PluginInterface):
    def __init__(self):
        super().__init__()
        self.name = "My Plugin"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "What this plugin does"

    def get_hooks(self):
        return {
            "pre_process_game": self.before_processing,
            "post_process_game": self.after_processing,
        }

    def before_processing(self, game_path):
        # Custom logic before game processing
        return {"status": "success"}

    def after_processing(self, game_path, result):
        # Custom logic after game processing
        return {"status": "success"}
```

### Available Hooks

| Hook | Called When | Arguments |
|------|-----------|-----------|
| `pre_process_game` | Before processing starts | `game_path` |
| `post_process_game` | After processing completes | `game_path`, `result` |
| `validate_package_json` | During validation | `package_json_data` |
| `pre_cleanup` | Before file cleanup | `cleanup_files` |
| `file_optimization` | During optimization | `game_path` |

### Managing Plugins

From the GUI Plugins tab or programmatically:

```python
from plugin_system import PluginManager

mgr = PluginManager()
discovered = mgr.discover_plugins()
mgr.load_plugin("My Plugin")
mgr.call_hooks("pre_process_game", "/path/to/game")
```

## Multi-Language Support

The application supports 4 languages with automatic system locale detection and English fallback.

| Language | Code | File |
|----------|------|------|
| English | `en` | `translations/en.json` |
| Japanese | `ja` | `translations/ja.json` |
| Spanish | `es` | `translations/es.json` |
| French | `fr` | `translations/fr.json` |

**In the GUI**: Select language from the toolbar dropdown. Changes apply instantly.

**Programmatic usage**:

```python
from translations.i18n import I18n

i18n = I18n()           # auto-detects system language
i18n = I18n("ja")       # force Japanese
print(i18n.t("welcome"))
i18n.set_locale("fr")   # switch at runtime
```

**Contributing translations**: Add a new `<lang_code>.json` file to `translations/` following the same key structure as `en.json`.

## Configuration Profiles and Templates

### Profiles

| Profile | Description | Best For |
|---------|-------------|----------|
| `default` | Balanced settings | Most RPG Maker MV games |
| `development` | Debugging enabled | Game development and testing |
| `production` | Minimal size | Final game distribution |
| `compatibility` | Older NW.js version | Maximum compatibility |
| `modern` | Latest features | Windows 10+ systems |

### Templates

| Template | Description | Use Case |
|----------|-------------|----------|
| `minimal` | Smallest possible size | Distribution builds |
| `debug` | Full debugging support | Development and testing |
| `multilingual` | Preserves language files | International games |

### Usage

```bash
python nwjs_automator.py --config-profile development --game-path "C:/Games/MyGame"
python nwjs_automator.py --config-template debug --game-path "C:/Games/MyGame"
python nwjs_automator.py --export-config my_config.json --game-path "C:/Games/MyGame"
python nwjs_automator.py --import-config my_config.json --game-path "C:/Games/MyGame"
```

## NW.js Version Guide

| Option | Version | Best For | Windows Support |
|--------|---------|----------|----------------|
| 1 | v0.29.4 | Maximum compatibility (RPG Maker MV era) | Windows 7+ |
| 2 | v0.49.2 | **Balanced default** - best overall choice | Windows 7+ |
| 3 | v0.72.0 | Modern stable (last Win7 support) | Windows 7+ |
| 4 | v0.90.0+ | Latest features, best performance | Windows 10+ |
| 5 | Custom | Specific version needs | Varies |

**Recommendation**: Use v0.49.2 for the best balance of compatibility and performance.

### Build Types

- **SDK Build**: Includes F12 Developer Tools (only 5-10MB larger, recommended)
- **Normal Build**: Slightly smaller, no developer tools

## Command Line Reference

| Argument | Description | Default |
|----------|-------------|---------|
| `--game-path` | Path to RPG Maker game directory | Required |
| `--executable-name` | Custom name for game executable | `Game` |
| `--nwjs-path` | Path to existing NW.js installation | Auto-download |
| `--nwjs-version` | NW.js version to use | `v0.49.2` |
| `--no-sdk` | Use normal build instead of SDK | SDK build |
| `--no-backup` | Skip creating backup | Create backup |
| `--verbose`, `-v` | Enable detailed logging | Normal logging |
| `--interactive`, `-i` | Force interactive mode | Auto-detect |
| `--devtools` | Enable developer tools (F12 access) | Disabled |
| `--platform-optimized` | Enable platform-specific optimizations | Disabled |
| `--log-level` | Set logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL) | INFO |
| `--config-profile` | Predefined profile (default/development/production/compatibility/modern) | None |
| `--config-template` | Configuration template (minimal/debug/multilingual) | None |
| `--export-config` | Export configuration to file | None |
| `--import-config` | Import configuration from file | None |
| `--help-topic` | Display contextual help on a topic | None |

## What the Script Does (Step by Step)

1. **Validation**: Checks for valid RPG Maker MV/MZ game structure (`package.json`, `www/`)
2. **Backup**: Creates timestamped backup with integrity checksums and manifest
3. **NW.js Setup**: Downloads specified version or uses local path, extracts archive
4. **Save Files**: Preserves `package.json`, `www/`, and `index.html` to temp directory
5. **Clean**: Removes old runtime from game directory
6. **Copy**: Installs new NW.js runtime
7. **Restore**: Puts game files back on top of new runtime
8. **Rename**: Renames `nw.exe` to custom executable name
9. **Cleanup**: Removes unnecessary files (chromedriver, docs, extra paks, non-en-US locales)
10. **Finish**: Creates Windows shortcut, validates structure, generates execution report
11. **Rollback** (if needed): Automatically restores from backup on failure

## Before and After

```
Before:                              After:
YourGame/          (~120MB)          YourGame/          (~5-15MB)
  Game.exe                             YourCustomName.exe
  nw.dll, ffmpeg.dll, etc.             www/
  resources.pak                        package.json
  locales/                             index.html
  www/
  package.json                       YourGame_backup/   (~120MB)
                                       [Complete original backup]
```

## Developer Tools Access

With SDK build, press **F12** in your game for:

- **Console**: Execute JavaScript commands
- **Elements**: Inspect game DOM structure
- **Sources**: Debug scripts with breakpoints
- **Network**: Monitor resource loading
- **Performance**: Profile game performance

```javascript
// In the game console (F12):
process.versions                          // Check NW.js version
$gamePlayer.gainGold(99999)               // Modify player stats
$gameSwitches.setValue(1, true)            // Toggle game switches
DataManager.maxSavefiles = () => 99       // Increase save slots
```

## Automatic Rollback System

The script tracks every critical operation. If anything fails:

1. Failure is detected immediately
2. Automatic restoration from the most recent backup
3. Detailed error information is provided
4. Backup integrity is preserved for manual restoration if needed

| Scenario | Action |
|----------|--------|
| Invalid game directory | Restore from backup |
| NW.js download failure | Restore from backup |
| Extraction failure | Restore from backup |
| File operation failure | Restore from backup |
| Final validation failure | Restore from backup |

## Execution Reports

Every execution generates a JSON report in `execution_reports/` containing:
timestamp, configuration snapshot, operations performed, files modified, warnings, success status, error details, and rollback data.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `package.json not found` | Point to the game root directory (must contain `package.json` and `www/`) |
| `Python not found` | Install Python 3.6+ and add to PATH |
| `Failed to download NW.js` | Check internet, try different version, or use `--nwjs-path` |
| Game won't start after processing | Try older version (v0.29.4), try `--no-sdk`, check plugin compatibility |
| Permission denied (Linux/Mac) | Check write permissions, try `sudo` |
| Missing dependencies | `pip install -r requirements.txt` |

For detailed troubleshooting, use verbose mode:
```bash
python nwjs_automator.py --verbose --game-path "C:\Your\Game"
```

## Testing

```bash
# Run full test suite
python -m unittest test_suite -v

# Run a single test
python -m unittest test_suite.TestNWJSAutomator.test_backup_creation -v
```

The test suite covers core automation, configuration system, platform compatibility, performance, update system, and integration workflows.

## Game Compatibility

- **RPG Maker MV**: All versions (use v0.29.4 for maximum compatibility)
- **RPG Maker MZ**: Use v0.49.2 or newer
- **Encrypted Games**: May not work with DRM-protected games
- **Custom Plugins**: Most work fine; some may need specific NW.js versions

## Version History

### v2.2.0 - Phase 5: Full GUI and Advanced Features
- **Modern GUI**: Full PySide6/PyQt6 interface with dark/light themes, dashboard, drag-and-drop
- **Batch Processing**: Multi-game processing with configurable parallel workers, integrated into GUI
- **Plugin System**: Class-based `PluginInterface` API, dynamic loading, GUI management panel
- **Multi-Language**: i18n module with auto-detection, fallback, runtime switching (en/ja/es/fr)
- **Theme Engine**: Complete QSS-based dark and light palettes with instant toggle

### v2.1.1 - Phase 3 and 4: Production Grade
- Automatic rollback system with operation monitoring
- Configuration profiles (5) and templates (3)
- Execution reporting with detailed JSON output
- Contextual help system
- Auto-update system with integrity verification
- Security hardening (input validation, path traversal protection)
- Performance optimization (caching, memory management, bottleneck analysis)

### v2.1.0 - Phase 2: Platform and SDK Enhancements
- SDK compatibility database with version validation
- Platform-specific management (ARM64, Windows/macOS/Linux)
- Enhanced logging with file rotation
- New CLI options: `--devtools`, `--platform-optimized`, `--log-level`

### v2.0.0 - Complete Rewrite
- Redesigned interactive experience with smart version presets
- Automatic `index.html` creation and `package.json` fixing
- Custom executable naming, cross-platform shortcuts
- Multi-architecture support (x64, x86, ARM)

### v1.1.0 - One-Click Launchers
### v1.0.0 - Initial Release

## Contributing

- **Report Bugs**: [GitHub Issues](https://github.com/aeagisdev/rpgm-nwjs-automator/issues)
- **Submit Code**: Pull requests welcome
- **Translate**: Add a `<lang>.json` file to `translations/`
- **Test Games**: Report compatibility with different games and NW.js versions

```bash
git clone https://github.com/aeagisdev/rpgm-nwjs-automator.git
cd rpgm-nwjs-automator
pip install -r requirements.txt
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

- **Original Guide**: Based on the tutorial by [Fairy's Voice](https://fairysvoice.net/blog/How_to_replace_an_RPG_Maker_MV_game's_runtime_with_your_own_local_copy_of_NWJS/)
- **NW.js Project**: https://nwjs.io/
- **RPG Maker Community**: Testing, feedback, and compatibility reports

---

**Made with care by RPG Maker developers, for RPG Maker developers.**
