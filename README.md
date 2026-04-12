# RPG Maker MV NW.js Automation Script v2.1.1

A Python script that completely automates the process of replacing RPG Maker MV/MZ game runtime with a modern NW.js installation, providing better performance, space savings, and developer tools access.

## 🎯 What This Script Does

This script transforms your RPG Maker games by replacing their outdated runtime with modern NW.js versions.

### ✨ Key Benefits (v2.1 Enhanced)

- **💾 Massive Space Savings**: Save 100-120MB per game (one NW.js serves all games)
- **🛠️ Developer Tools**: Press F12 for debugging, modding, and game analysis
- **⚡ Better Performance**: Modern NW.js with latest bug fixes and optimizations
- **🎮 Custom Game Names**: Create personalized executable names
- **🤖 Zero Manual Work**: Fully automated with intelligent error handling
- **🔒 100% Safe**: Creates backups and validates everything before changes
- **🌍 Cross-Platform**: Works on Windows, macOS, and Linux
- **🔄 Automatic Rollback**: Self-healing system restores game if errors occur
- **📋 Configuration Profiles**: Predefined settings for different use cases
- **📊 Execution Reports**: Detailed logs of all operations performed
- **💡 Contextual Help**: Integrated documentation and guidance

### 🆕 New in v2.1.1 - Advanced Features

#### 🔍 Advanced package.json Validation
- **Comprehensive Field Validation**: Validates all NW.js critical fields
- **Automatic Correction**: Fixes invalid formats and missing fields
- **Smart Defaults**: Adds recommended configurations automatically
- **Format Support**: Supports official KADOKAWA/RPGMV format

#### 🎯 Intelligent Version Management
- **Compatibility Database**: Validates versions against known compatible NW.js releases
- **Platform-Specific Recommendations**: Suggests optimal versions for each OS
- **Fallback Mechanism**: Automatic fallback to tested versions if needed
- **Version Validation**: Checks version format validity before processing

#### 🗑️ Smart Cleanup System
- **Context-Aware Cleanup**: Analyzes files before removal
- **Critical File Protection**: Whitelist system prevents accidental deletion
- **Debug Mode**: Option to preserve debug files
- **Locale Management**: Intelligent handling of localization files
- **Post-Cleanup Analysis**: Provides optimization suggestions

#### 💾 Robust Backup System
- **Incremental Backups**: Timestamped backups with rotation
- **Integrity Verification**: Checksum validation of backup contents
- **Backup Manifest**: Detailed inventory of all backed-up files
- **Automatic Cleanup**: Removes old backups (keeps last 3)
- **Restoration Verification**: Validates restored files

#### 🔄 Automatic Rollback System (Phase 3)
- **Operation Monitoring**: Tracks all critical operations during processing
- **Self-Healing**: Automatically restores game to original state on failure
- **Detailed Error Reporting**: Provides comprehensive error information
- **Backup Integrity Preservation**: Ensures backups remain valid for restoration
- **Status Tracking**: Monitors rollback success/failure with detailed logs

#### 📋 Configuration Management (Phase 3)
- **Predefined Profiles**: 5 optimized configuration sets for different scenarios
- **Configuration Templates**: 3 reusable patterns for common use cases
- **Export/Import**: Save and load custom configurations
- **Profile Customization**: Create and save custom configuration profiles
- **Template Application**: Apply templates to quickly configure common settings

#### 📊 Execution Reporting (Phase 3)
- **Automatic Report Generation**: Creates detailed execution reports
- **Operation Tracking**: Records all operations performed during execution
- **File Modification Log**: Documents all files modified during processing
- **Error Documentation**: Captures detailed error information for troubleshooting
- **Configuration Snapshot**: Saves complete configuration used for the operation

#### 💡 Integrated Documentation (Phase 3)
- **Contextual Help System**: Topic-based help accessible via command line
- **Configuration Guidance**: Detailed information on profiles and templates
- **Feature Documentation**: Comprehensive explanations of all capabilities
- **Usage Examples**: Practical examples for common scenarios
- **Troubleshooting Guide**: Integrated troubleshooting information
=======
### 🆕 New in v2.1 - Advanced Features

#### 🔍 Advanced package.json Validation
- **Comprehensive Field Validation**: Validates all NW.js critical fields
- **Automatic Correction**: Fixes invalid formats and missing fields
- **Smart Defaults**: Adds recommended configurations automatically
- **Format Support**: Supports official KADOKAWA/RPGMV format

#### 🎯 Intelligent Version Management
- **Compatibility Database**: Validates versions against known compatible NW.js releases
- **Platform-Specific Recommendations**: Suggests optimal versions for each OS
- **Fallback Mechanism**: Automatic fallback to tested versions if needed
- **Version Validation**: Checks version format validity before processing

#### 🗑️ Smart Cleanup System
- **Context-Aware Cleanup**: Analyzes files before removal
- **Critical File Protection**: Whitelist system prevents accidental deletion
- **Debug Mode**: Option to preserve debug files
- **Locale Management**: Intelligent handling of localization files
- **Post-Cleanup Analysis**: Provides optimization suggestions

#### 💾 Robust Backup System
- **Incremental Backups**: Timestamped backups with rotation
- **Integrity Verification**: Checksum validation of backup contents
- **Backup Manifest**: Detailed inventory of all backed-up files
- **Automatic Cleanup**: Removes old backups (keeps last 3)
- **Restoration Verification**: Validates restored files

#### 🛠️ Advanced SDK Support (Phase 2)
- **SDK Compatibility Database**: Tracks version stability and testing status
- **Automatic Version Validation**: Validates NW.js versions with fallback suggestions
- **Developer Tools Support**: Enable F12 access with `--devtools` flag
- **SDK Feature Configuration**: Automatic cleanup list adjustment based on SDK usage

#### 🌍 Platform-Specific Management (Phase 2)
- **Platform Detection**: Automatic detection of Windows/macOS/Linux with architecture info
- **ARM64 Support**: Special handling for Apple Silicon (M1/M2) Macs
- **Platform Optimizations**: Recommended versions and path handling per OS
- **Platform-Specific Cleanup**: Intelligent file preservation based on platform

#### 📊 Enhanced Logging & Debugging (Phase 2)
- **Configurable Logging Levels**: DEBUG/INFO/WARNING/ERROR/CRITICAL
- **File Logging with Rotation**: 1MB max size, 3 backup files
- **Timestamped Logs**: Detailed timestamps for all log entries
- **Command-Line Control**: `--log-level` parameter for precise control

#### 🎯 Improved User Interface (Phase 2)
- **Enhanced CLI**: New `--devtools`, `--platform-optimized`, `--log-level` options
- **Interactive Mode Updates**: Additional configuration options in interactive setup
- **Configuration Summary**: Shows all new options in pre-execution summary
- **Better Feedback**: More detailed status messages and warnings

#### 🎯 Intelligent Version Management
- **Compatibility Database**: Validates versions against known compatible NW.js releases
- **Platform-Specific Recommendations**: Suggests optimal versions for each OS
- **Fallback Mechanism**: Automatic fallback to tested versions if needed
- **Version Validation**: Checks version format validity before processing

#### 🗑️ Smart Cleanup System
- **Context-Aware Cleanup**: Analyzes files before removal
- **Critical File Protection**: Whitelist system prevents accidental deletion
- **Debug Mode**: Option to preserve debug files
- **Locale Management**: Intelligent handling of localization files
- **Post-Cleanup Analysis**: Provides optimization suggestions

#### 💾 Robust Backup System
- **Incremental Backups**: Timestamped backups with rotation
- **Integrity Verification**: Checksum validation of backup contents
- **Backup Manifest**: Detailed inventory of all backed-up files
- **Automatic Cleanup**: Removes old backups (keeps last 3)
- **Restoration Verification**: Validates restored files

### Automatic Processing (Enhanced)
- **Game Validation**: Verifies the directory contains a valid RPG Maker MV/MZ game
- **NW.js Download**: Automatically downloads the specified NW.js version if not provided
- **Runtime Cleanup**: **Intelligently** removes NW.js runtime files while preserving game assets
- **Configuration Updates**: **Advanced** modification of `package.json` with comprehensive validation
- **Launch Script Creation**: Creates platform-specific launch scripts (.bat for Windows, .sh for Unix)

### One-Click Solutions (Improved)
- **Intelligent Setup**: Launch scripts automatically check and install dependencies
- **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- **Desktop Integration**: Optional desktop shortcuts for instant access
- **Zero Configuration**: Works out-of-the-box with sensible defaults
- **Visual Feedback**: Colored terminal output with clear progress indicators
- **Error Recovery**: Automatic fallback mechanisms for common issues

### Safety Features (Enhanced)
- **Automatic Backup**: Creates **verified** backups of the original game before modifications
- **File Preservation**: **Intelligently** preserves game assets, README files, and custom directories
- **Error Handling**: **Comprehensive** error handling with informative messages
- **Validation**: **Multiple** validation steps to ensure safe processing
- **Integrity Checks**: **Checksum verification** for all critical operations
- **Rollback Capability**: Ability to restore from backup if issues occur

## 💻 Ultra-Quick Setup (30 Seconds!)

### 🖱️ Method 1: One-Click Launch (Recommended)

1. **Download** the latest release from [GitHub Releases](https://github.com/aeagisdev/rpgm-nwjs-automator/releases)
2. **Extract** anywhere convenient (Desktop, Tools folder, etc.)
3. **Double-click** the launcher for your system:
   - **Windows**: `run_nwjs_automator_win.bat`
   - **Mac/Linux**: `run_nwjs_automator_unix_mac.sh`

**That's it!** The launcher will:
- ✅ Check if Python is installed (with install guidance if needed)
- ✅ Automatically install required dependencies
- ✅ Offer to create desktop shortcuts
- ✅ Launch the automation tool
- ✅ Keep the terminal open to show results

### Method 2: Interactive Mode (Recommended)
```bash
python nwjs_automator.py
```
The script will guide you through everything with a user-friendly interface!

### Method 2: Command Line (For Advanced Users)
```bash
python nwjs_automator.py --game-path "C:\Path\To\Your\Game"
```

## 📋 Requirements

- **Python 3.6+** (script will check and guide you if needed)
- **Internet connection** (to download NW.js if not provided)
- **Required packages** (automatically installed): `requests`

## 💻 Installation

### Step 1: Install Python (if needed)
- **Windows**: Download from [python.org](https://python.org) and check "Add to PATH"
- **Mac**: `brew install python3` or download from python.org
- **Linux**: Usually pre-installed, or `sudo apt install python3 python3-pip`

### Step 2: Install Dependencies
```bash
pip install requests
```

### Step 3: Download Script
Download `nwjs_automator.py` from the [releases page](https://github.com/aeagisdev/rpgm-nwjs-automator/releases)

## 🎮 How to Use

### 🌟 Interactive Mode (Easiest)

1. **Run the script**:
   ```bash
   python nwjs_automator.py
   ```

2. **Follow the colorful prompts**:
   - 📁 **Game Path**: Enter your RPG Maker game folder
   - 🎯 **Game Name**: Choose your custom executable name (e.g., "MyAwesomeGame")
   - 🔧 **NW.js Version**: Pick from optimized presets or go custom
   - 🛠️ **Build Type**: SDK (recommended) or Normal
   - 💾 **Backup**: Yes (recommended) or No
   - 📋 **Configuration Profile**: Choose from predefined profiles (optional)
   - 📋 **Configuration Template**: Apply templates for common scenarios (optional)

3. **Sit back and watch**: The script handles everything automatically!

### 🎯 Using Configuration Profiles

The script includes 5 predefined configuration profiles:

| Profile | Description | Best For |
|---------|-------------|----------|
| **default** | Balanced settings | Most RPG Maker MV games |
| **development** | Debugging enabled | Game development & testing |
| **production** | Minimal size | Final game distribution |
| **compatibility** | Older NW.js version | Maximum compatibility |
| **modern** | Latest features | Windows 10+ systems |

**Usage**:
```bash
python nwjs_automator.py --config-profile development --game-path "C:/Games/MyGame"
```

### 📋 Using Configuration Templates

Apply templates for common scenarios:

| Template | Description | Use Case |
|----------|-------------|----------|
| **minimal** | Smallest possible size | Distribution builds |
| **debug** | Full debugging support | Development & testing |
| **multilingual** | Preserves language files | International games |

**Usage**:
```bash
python nwjs_automator.py --config-template debug --game-path "C:/Games/MyGame"
```

### 💾 Configuration Management

**Export current configuration**:
```bash
python nwjs_automator.py --export-config my_config.json --game-path "C:/Games/MyGame"
```

**Import configuration**:
```bash
python nwjs_automator.py --import-config my_config.json --game-path "C:/Games/MyGame"
```

### 💡 Contextual Help System

Get detailed help on specific topics:

```bash
# General help
python nwjs_automator.py --help-topic general

# Configuration profiles help
python nwjs_automator.py --help-topic profiles

# Configuration templates help
python nwjs_automator.py --help-topic templates

# Rollback system help
python nwjs_automator.py --help-topic rollback

# Configuration management help
python nwjs_automator.py --help-topic config_management
```

### 🎯 NW.js Version Guide

The script offers smart version presets:

| Option | Version | Best For | Windows Support |
|--------|---------|----------|----------------|
| **1** | v0.29.4 | Maximum compatibility (RPG Maker MV era) | Windows 7+ |
| **2** | v0.49.2 | **Balanced default** - best overall choice | Windows 7+ |
| **3** | v0.72.0 | Modern stable (last Win7 support) | Windows 7+ |
| **4** | v0.90.0+ | Latest features, best performance | Windows 10+ |
| **5** | Custom | Specific version needs | Varies |

**💡 Recommendation**: Use option 2 (v0.49.2) for the best balance of compatibility and performance.

### 🛠️ Build Types Explained

- **SDK Build (Recommended)**: 
  - ✅ Includes F12 Developer Tools
  - ✅ Perfect for modding and debugging
  - ✅ Only 5-10MB larger
  
- **Normal Build**: 
  - ✅ Slightly smaller size
  - ❌ No developer tools
  - ⚠️ Use only if you need absolute minimum size

## 🔧 Advanced Usage

### Command Line Options

```bash
# Basic usage
python nwjs_automator.py --game-path "C:\Your\Game"

# Custom executable name
python nwjs_automator.py --game-path "C:\Your\Game" --executable-name "MyGame"

# Specific NW.js version
python nwjs_automator.py --game-path "C:\Your\Game" --nwjs-version "v0.72.0"

# Use existing NW.js installation
python nwjs_automator.py --game-path "C:\Your\Game" --nwjs-path "C:\nwjs"

# Skip backup (not recommended)
python nwjs_automator.py --game-path "C:\Your\Game" --no-backup

# Normal build instead of SDK
python nwjs_automator.py --game-path "C:\Your\Game" --no-sdk

# Verbose logging
python nwjs_automator.py --game-path "C:\Your\Game" --verbose
```

### All Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--game-path` | Path to RPG Maker game directory | Required |
| `--executable-name` | Custom name for game executable | "Game" |
| `--nwjs-path` | Path to existing NW.js installation | Auto-download |
| `--nwjs-version` | NW.js version to use | "v0.49.2" |
| `--no-sdk` | Use normal build instead of SDK | SDK build |
| `--no-backup` | Skip creating backup | Create backup |
| `--verbose`, `-v` | Enable detailed logging | Normal logging |
| `--interactive`, `-i` | Force interactive mode | Auto-detect |
| `--devtools` | Enable developer tools (F12 access) | Disabled |
| `--platform-optimized` | Enable platform-specific optimizations | Disabled |
| `--log-level` | Set logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL) | INFO |
| `--config-profile` | Use a predefined configuration profile (default/development/production/compatibility/modern) | None |
| `--config-template` | Apply a configuration template (minimal/debug/multilingual) | None |
| `--export-config` | Export current configuration to a file | None |
| `--import-config` | Import configuration from a file | None |
| `--help-topic` | Display contextual help on a specific topic | None |

## 🔄 What the Script Does (Step by Step)

### 1. 🔍 Validation Phase
- ✅ Checks if directory contains valid RPG Maker MV/MZ game
- ✅ Verifies `package.json` and `www/` folder exist
- ✅ Validates and fixes `package.json` for NW.js compatibility
- ✅ Ensures all critical files are present

### 2. 💾 Safety Phase
- ✅ Creates complete backup as `GameName_backup`
- ✅ Backs up critical files (`package.json`, `www/`, `index.html`)
- ✅ Validates backup integrity before proceeding
- ✅ Initializes rollback monitoring system

### 3. 📥 NW.js Setup Phase
- ✅ Downloads specified NW.js version (if not provided)
- ✅ Extracts and prepares NW.js runtime
- ✅ Chooses correct architecture (x64, x86, ARM) automatically
- ✅ Applies configuration profile settings if specified

### 4. 🧹 Cleanup Phase
- ✅ Removes old NW.js runtime files from game
- ✅ Preserves all game assets and custom files
- ✅ Cleans up unnecessary files (chromedriver, docs, etc.)
- ✅ Keeps only essential locale files (en-US)
- ✅ Applies configuration template cleanup rules

### 5. 🔧 Integration Phase
- ✅ Copies new NW.js runtime to game directory
- ✅ Restores game files with proper structure
- ✅ Creates/fixes `index.html` if missing
- ✅ Renames executable to your custom name
- ✅ Applies platform-specific optimizations

### 6. ✨ Finishing Phase
- ✅ Removes unnecessary NW.js files
- ✅ Creates Windows shortcuts (if applicable)
- ✅ Sets proper file permissions
- ✅ Validates final game structure
- ✅ Generates comprehensive execution report
- ✅ Saves execution report with all operation details

### 7. 🔄 Rollback Phase (if needed)
- ✅ Detects processing failures automatically
- ✅ Attempts automatic restoration from backup
- ✅ Provides detailed error information
- ✅ Preserves backup integrity for manual restoration
- ✅ Documents rollback status in execution report

## 📁 Before & After

### Before Processing
```
YourGame/                          (~120MB)
├── Game.exe                       (NW.js runtime)
├── nw.dll, ffmpeg.dll, etc.       (Runtime files)
├── resources.pak                  (NW.js resources)
├── locales/                       (All languages)
├── www/                           (Your game!)
└── package.json                   (Game config)
```

### After Processing
```
YourGame/                          (~5-15MB)
├── YourCustomName.exe             (Your named executable)
├── www/                           (Your game - preserved)
├── package.json                   (Updated & optimized)
├── index.html                     (Validated/created)
└── YourCustomName.lnk             (Windows shortcut)

YourGame_backup/                   (~120MB)
└── [Complete original backup]
```

## 🛠️ Developer Tools Access

With SDK build (default), press **F12** in your game for:

### 🔧 Debugging Features
- **Console**: Execute JavaScript commands directly
- **Elements**: Inspect game DOM structure
- **Sources**: Debug game scripts with breakpoints
- **Network**: Monitor resource loading
- **Performance**: Profile game performance

### 🎮 Game Modification Examples
```javascript
// In the game console (F12):

// Check NW.js version
process.versions

// Increase save slots
DataManager.maxSavefiles = () => 99

// Modify player stats
$gamePlayer.gainGold(99999)
$gameActors.actor(1).gainExp(999999)

// Skip events or change switches
$gameSwitches.setValue(1, true)
$gameVariables.setValue(1, 100)

// Test battles
$gameParty.addActor(2)
SceneManager.push(Scene_Battle)
```

## 🔄 Automatic Rollback System

The script includes a comprehensive automatic rollback system that protects your games:

### ✨ Key Features

- **Operation Monitoring**: Tracks every critical operation during processing
- **Failure Detection**: Automatically detects when something goes wrong
- **Self-Healing**: Attempts to restore the game to its original state
- **Detailed Reporting**: Provides comprehensive error information
- **Backup Preservation**: Ensures backups remain intact for manual restoration

### 🎯 How It Works

1. **Monitoring**: All critical operations are tracked and logged
2. **Validation**: Each step is validated before proceeding
3. **Error Detection**: Failures are caught immediately
4. **Automatic Restoration**: The system attempts to restore from the most recent backup
5. **Status Reporting**: Detailed information about what happened and what was restored

### 📋 Rollback Scenarios

| Scenario | Trigger | Action |
|----------|---------|--------|
| **File Validation Failure** | Invalid game directory structure | Restore from backup |
| **Download Failure** | Cannot download NW.js | Restore from backup |
| **Extraction Failure** | Cannot extract NW.js archive | Restore from backup |
| **File Operation Failure** | Cannot copy/rename files | Restore from backup |
| **Integrity Check Failure** | Final validation fails | Restore from backup |

### 💡 Rollback Status Messages

- **✅ Success**: Operation completed successfully
- **⚠️ Rollback Successful**: Automatic restoration completed
- **❌ Rollback Failed**: Manual restoration needed
- **ℹ️ Not Attempted**: No backup available or error occurred before backup

### 🔧 Manual Restoration

If automatic rollback fails, you can manually restore:

```bash
# Manual restoration from backup
python nwjs_automator.py --game-path "C:/Games/MyGame" --no-backup
# Then manually copy files from the backup directory
```

## 📊 Execution Reports

Every execution generates a detailed report with comprehensive information:

### 📋 Report Contents

- **Execution Timestamp**: When the operation was performed
- **Script Version**: Version of the automation script
- **Game Path**: Full path to the processed game
- **Configuration**: Complete configuration used
- **Operations Performed**: List of all operations completed
- **Files Modified**: Detailed list of modified files
- **Warnings**: Any warnings encountered
- **Success Status**: Whether operation succeeded
- **Error Details**: Comprehensive error information (if applicable)
- **Rollback Data**: Rollback status and details (if applicable)

### 💾 Report Location

Reports are saved in the `execution_reports/` directory with timestamped filenames:

```
execution_reports/
└── report_20260412_143022.json
```

### 📊 Report Structure Example

```json
{
  "execution_timestamp": "2026-04-12 14:30:22",
  "script_version": "2.1.0",
  "game_path": "C:/Games/MyGame",
  "configuration": {
    "nwjs_version": "v0.49.2",
    "use_sdk": true,
    "enable_devtools": false,
    "platform_optimized": true,
    "executable_name": "MyGame",
    "platform": "windows",
    "architecture": "AMD64"
  },
  "operations_performed": [
    "game_directory_validation",
    "backup_creation",
    "nwjs_setup",
    "file_preservation",
    "runtime_integration",
    "executable_renaming",
    "cleanup",
    "shortcut_creation"
  ],
  "files_modified": [
    "package.json",
    "index.html",
    "MyGame.exe",
    "nwjs_automator.log"
  ],
  "warnings": [],
  "success": true,
  "error": null
}
```

### 💡 Using Execution Reports

- **Troubleshooting**: Identify exactly what happened during processing
- **Reproduction**: Recreate the same configuration for consistent results
- **Debugging**: Understand error conditions and rollback status
- **Documentation**: Keep records of all processing operations
- **Support**: Provide detailed information when requesting help

## 🌟 Special Features

### 🔄 Automatic `index.html` Handling
- **Smart Detection**: Finds and preserves existing `index.html`
- **Intelligent Creation**: Creates optimized `index.html` if missing
- **Script Auto-Discovery**: Automatically includes all game scripts in correct order
- **Library Order**: Maintains proper RPG Maker MV library loading sequence

### 📦 Smart `package.json` Fixes
- **Name Field**: Adds required `name` field for newer NW.js versions
- **UTF-8 Encoding**: Ensures proper character encoding
- **Validation**: Checks JSON syntax and structure
- **Backup**: Preserves original configuration while adding required fields

### 🗂️ Intelligent File Preservation
The script carefully preserves:
- ✅ All game assets (`www/` folder)
- ✅ Custom README files (`.txt`, `.md`, `.pdf`)
- ✅ User-created directories
- ✅ Save files and configuration
- ✅ Plugin data and custom resources

### 🧹 Smart Cleanup
Removes only unnecessary files:
- ❌ `chromedriver.exe` (development tool)
- ❌ Documentation files (`AUTHORS`, `CHANGELOG.md`, etc.)
- ❌ Unused PAK files (`nw_100_percent.pak`, etc.)
- ❌ Extra locale files (keeps only `en-US`)
- ❌ SDK-specific files (if using normal build)

## ⚠️ Important Notes

### 🎮 Game Compatibility
- **RPG Maker MV**: Works with all versions (use v0.29.4 for maximum compatibility)
- **RPG Maker MZ**: Use v0.49.2 or newer
- **Encrypted Games**: May not work with DRM-protected games
- **Custom Plugins**: Most work fine, some may need specific NW.js versions

### 💾 File Organization Tips
```
📁 C:\RPG Games\
├── 📁 Game1\                    # Processed (5MB)
├── 📁 Game1_backup\             # Original backup (120MB)
├── 📁 Game2\                    # Processed (8MB)
├── 📁 Game2_backup\             # Original backup (135MB)
└── ...

📁 C:\Tools\
└── 📁 nwjs_automator\           # Keep script here
    ├── nwjs_automator.py
    └── temp_nwjs\               # Auto-created temp folder
```

### 🔒 Safety Reminders
- **Always backup**: Script creates backups automatically, but keep your own too
- **Test games**: Launch processed games once to ensure they work
- **Save early saves**: Keep save files from before processing
- **Document versions**: Note which NW.js version works best for each game

## 🐛 Troubleshooting

### Common Issues & Solutions

**❌ "package.json not found"**
- ✅ Make sure you're pointing to the game's root directory
- ✅ Directory should contain both `package.json` and `www/` folder

**❌ "Python not found"**
- ✅ Install Python 3.6+ from python.org
- ✅ On Windows, check "Add to PATH" during installation
- ✅ Restart command prompt after installation

**❌ "Failed to download NW.js"**
- ✅ Check internet connection
- ✅ Try a different NW.js version
- ✅ Use `--nwjs-path` to point to existing NW.js installation

**❌ "Game won't start after processing"**
- ✅ Try older NW.js version (v0.29.4 for maximum compatibility)
- ✅ Restore from backup and try with `--no-sdk` flag
- ✅ Check if game has custom plugins requiring specific versions

**❌ "Permission denied" (Linux/Mac)**
- ✅ Run with `sudo` if needed
- ✅ Make sure you have write permissions to game directory
- ✅ Check file ownership with `ls -la`

**❌ "Missing dependencies"**
- ✅ Install with: `pip install requests`
- ✅ On some systems: `pip3 install requests`
- ✅ Try: `python -m pip install requests`

### 🔧 Debug Mode
For detailed troubleshooting, use verbose mode:
```bash
python nwjs_automator.py --verbose --game-path "C:\Your\Game"
```

This shows detailed logs of every operation, perfect for diagnosing issues.

### 🆘 Getting Help
If you're still having issues:
1. **Check the backup**: You can always restore from `GameName_backup`
2. **Try interactive mode**: More user-friendly than command line
3. **Use verbose logging**: `--verbose` shows detailed error information
4. **Test with different versions**: Some games work better with specific NW.js versions
5. **Check GitHub Issues**: Someone might have had the same problem

## 🎯 Pro Tips

### 🚀 Performance Optimization
- **Use SDK build** unless you absolutely need smaller size
- **Choose v0.49.2** for best balance of features and compatibility
- **Process multiple games** - they'll all share the same NW.js runtime
- **Keep backups** - you can always try different NW.js versions

### 🎮 Game Development Tips
- **Use F12 tools** to debug and test your games
- **Test save/load** functionality after processing
- **Check plugin compatibility** with your chosen NW.js version
- **Document your settings** - note what works for each game

### 💾 Storage Management
- **One NW.js for all**: All processed games share the same runtime
- **Clean up temp files**: Script does this automatically
- **Organize backups**: Keep original backups for safety
- **Monitor space savings**: You'll save 100MB+ per game processed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**What this means:**
- ✅ Free to use for personal and commercial projects
- ✅ Modify and redistribute as needed
- ✅ Include in your own tools without restrictions
- ⚠️ Attribution required (keep the copyright notice)

## 🙏 Credits & Acknowledgments

- **Original Guide**: Based on the excellent tutorial by [Fairy's Voice](https://fairysvoice.net/blog/How_to_replace_an_RPG_Maker_MV_game's_runtime_with_your_own_local_copy_of_NWJS/)
- **NW.js Project**: https://nwjs.io/ - The amazing runtime that makes this possible
- **RPG Maker Community**: For testing, feedback, and compatibility reports
- **Python Community**: For the incredible tools and libraries that power this script

## 🔄 Version History

### v2.1.1 - Phase 3 Implementation
**Release Date**: 12 April 2026

✨ **Phase 3 Features Implemented**:
- **Automatic Rollback System**: Self-healing mechanism that restores game to original state on failure
- **Configuration Profiles**: 5 predefined configuration sets for different use cases
- **Configuration Templates**: 3 reusable configuration patterns for common scenarios
- **Configuration Management**: Export/import configurations for reuse across projects
- **Execution Reporting**: Automatic generation of detailed execution reports
- **Contextual Help System**: Integrated documentation accessible via command line

✨ **New Advanced Features**:
- **Advanced package.json Validation**: Comprehensive validation of all NW.js critical fields with automatic correction
- **Intelligent Version Management**: Compatibility database with platform-specific recommendations and fallback mechanism
- **Smart Cleanup System**: Context-aware cleanup with critical file protection and post-cleanup analysis
- **Robust Backup System**: Incremental backups with integrity verification and automatic rotation
- **Enhanced Error Recovery**: Automatic fallback mechanisms and restoration capabilities

🔧 **Major Improvements**:
- **Validation**: Comprehensive package.json field validation with smart defaults and format support
- **Version Handling**: Version compatibility checking with platform-specific suggestions
- **Cleanup**: Enhanced cleanup with whitelist protection and intelligent file analysis
- **Backup**: Backup integrity verification with manifest generation and automatic cleanup
- **Safety**: Improved error handling with multiple validation steps and integrity checks

🐛 **Critical Bug Fixes**:
- Fixed package.json handling for missing or invalid fields
- Fixed version format validation for non-standard versions
- Fixed critical file preservation during cleanup operations
- Fixed backup verification and restoration processes

📖 **Documentation Enhancements**:
- Updated README with detailed v2.1 feature descriptions
- Added usage examples for advanced validation and version management
- Enhanced troubleshooting section with common issues and solutions

### v2.1.1 - Phase 2 Implementation
**Release Date**: 12 April 2026

✨ **Phase 2 Features Implemented**:
- **Advanced SDK Support**: SDK compatibility database with version validation and developer tools support
- **Platform-Specific Management**: Automatic platform detection with ARM64 support and optimizations
- **Enhanced Logging**: Configurable logging levels with file rotation and timestamped entries
- **Improved UI**: Enhanced CLI with new options and better interactive mode experience

🔧 **Technical Improvements**:
- **SDK Validation**: Automatic version compatibility checking with fallback mechanisms
- **Platform Detection**: Windows/macOS/Linux detection with architecture-specific optimizations
- **Logging System**: File-based logging with rotation (1MB max, 3 backups)
- **Command Line**: New `--devtools`, `--platform-optimized`, `--log-level` options

📖 **Updated Documentation**:
- Added Phase 2 features to README
- Updated command line arguments table
- Enhanced usage examples with new options

### v2.0.0 - Complete Rewrite
- ✨ **New**: Completely redesigned interactive experience
- ✨ **New**: Smart NW.js version presets with compatibility guidance
- ✨ **New**: Automatic `index.html` creation and validation
- ✨ **New**: Intelligent `package.json` fixing for newer NW.js versions
- ✨ **New**: Custom executable naming with automatic extension handling
- ✨ **New**: Cross-platform shortcut creation (Windows `.lnk` files)
- ✨ **New**: Advanced file preservation logic
- ✨ **New**: Comprehensive error handling and validation
- ✨ **New**: Detailed progress reporting with colored output
- ✨ **New**: Support for multiple NW.js architectures (x64, x86, ARM)
- 🔧 **Improved**: Much more robust file handling and safety checks
- 🔧 **Improved**: Better cleanup of unnecessary NW.js files
- 🔧 **Improved**: Enhanced backup and restore system
- 🔧 **Improved**: Smarter temporary file management
- 🔧 **Improved**: Platform-specific optimizations
- 🔧 **Improved**: More informative logging and user feedback

### v1.1.0 - One-Click Revolution
- ✨ **New**: Intelligent one-click launcher scripts
- ✨ **New**: Automatic dependency installation
- ✨ **New**: Desktop shortcut creation
- 🔧 **Improved**: Cross-platform compatibility

### v1.0.0 - Initial Release
- ✨ **New**: Full automation of NW.js replacement process
- ✨ **New**: Interactive and command-line modes
- ✨ **New**: Automatic backup system
- ✨ **New**: Cross-platform support

## 🤝 Contributing

We welcome contributions from the RPG Maker community!

### Ways to Help:
- 🐛 **Report Bugs**: Found an issue? Let us know!
- 💡 **Suggest Features**: Have ideas for improvements?
- 🔧 **Submit Code**: Pull requests are welcome
- 📖 **Improve Docs**: Help make the documentation even clearer
- 🎮 **Test Games**: Try the script with different games and report compatibility
- 🌍 **Translate**: Help translate the script for international users

### Development Setup:
```bash
git clone https://github.com/aeagisdev/rpgm-nwjs-automator.git
cd rpgm-nwjs-automator
pip install -r requirements.txt
```

## 🌟 Show Your Support

If this tool helped you, consider:
- ⭐ **Star the repository** on GitHub
- 🐦 **Share on social media** - help other RPG Maker developers discover this tool
- 💬 **Join discussions** - share your experiences and help others
- 🎮 **Report compatibility** - let us know which games work great
- 📝 **Write reviews** - help spread the word about the benefits

## 📞 Support & Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/aeagisdev/rpgm-nwjs-automator/issues)
- **Discussions**: [Ask questions and share experiences](https://github.com/aeagisdev/rpgm-nwjs-automator/discussions)
- **Wiki**: [Community compatibility database](https://github.com/aeagisdev/rpgm-nwjs-automator/wiki)

---

**Made with ❤️ by RPG Maker developers, for RPG Maker developers.**

*Transform your games. Save space. Unlock potential.*