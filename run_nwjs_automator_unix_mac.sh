#!/bin/bash

# RPG Maker MV NW.js Automator - Unix/Linux/Mac Launch Script
# This script provides a one-click solution for running the NW.js automator

# Set terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Get script directory for reliable path resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Function to print colored output
print_header() {
    echo -e "${CYAN}"
    echo "=========================================="  
    echo "  RPG Maker MV NW.js Automation Tool"
    echo "=========================================="
    echo -e "${NC}"
    echo
    echo -e "${GREEN}This tool will help you optimize your RPG Maker games"
    echo "by replacing the built-in runtime with NW.js"
    echo
    echo "Benefits:"
    echo "  * Save 120MB+ per game"
    echo "  * Enable Developer Tools (F12)"
    echo "  * Better performance and compatibility"
    echo -e "${NC}"
    echo
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect desktop environment
detect_desktop_environment() {
    if [[ "$DESKTOP_SESSION" =~ "gnome" ]] || command_exists gnome-terminal; then
        echo "gnome"
    elif [[ "$DESKTOP_SESSION" =~ "kde" ]] || command_exists konsole; then
        echo "kde"
    elif [[ "$DESKTOP_SESSION" =~ "xfce" ]] || command_exists xfce4-terminal; then
        echo "xfce"
    elif [[ "$DESKTOP_SESSION" =~ "mate" ]] || command_exists mate-terminal; then
        echo "mate"
    elif command_exists xterm; then
        echo "xterm"
    else
        echo "generic"
    fi
}

# Function to get appropriate terminal command
get_terminal_command() {
    local de="$1"
    case "$de" in
        "gnome")
            echo "gnome-terminal --"
            ;;
        "kde")
            echo "konsole -e"
            ;;
        "xfce")
            echo "xfce4-terminal -e"
            ;;
        "mate")
            echo "mate-terminal -e"
            ;;
        "xterm")
            echo "xterm -e"
            ;;
        *)
            # Try to find any available terminal
            if command_exists gnome-terminal; then
                echo "gnome-terminal --"
            elif command_exists konsole; then
                echo "konsole -e"
            elif command_exists xfce4-terminal; then
                echo "xfce4-terminal -e"
            elif command_exists mate-terminal; then
                echo "mate-terminal -e"
            elif command_exists xterm; then
                echo "xterm -e"
            else
                echo "bash -c"
            fi
            ;;
    esac
}

# Function to detect Python command
detect_python() {
    if command_exists python3; then
        echo "python3"
    elif command_exists python; then
        # Check if it's Python 3
        if python -c "import sys; exit(0 if sys.version_info[0] == 3 else 1)" 2>/dev/null; then
            echo "python"
        else
            echo ""
        fi
    else
        echo ""
    fi
}

# Function to detect pip command
detect_pip() {
    local python_cmd="$1"
    if command_exists pip3; then
        echo "pip3"
    elif command_exists pip; then
        echo "pip"
    elif command_exists "$python_cmd" && $python_cmd -m pip --version >/dev/null 2>&1; then
        echo "$python_cmd -m pip"
    else
        echo ""
    fi
}

# Function to install Python on different systems
suggest_python_install() {
    echo -e "${YELLOW}Python 3 installation suggestions:${NC}"
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "  • Install via Homebrew: ${CYAN}brew install python3${NC}"
        echo "  • Download from: ${CYAN}https://python.org${NC}"
        echo "  • Install via Xcode Command Line Tools: ${CYAN}xcode-select --install${NC}"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - detect distribution
        if command_exists apt-get; then
            echo "  • Ubuntu/Debian: ${CYAN}sudo apt update && sudo apt install python3 python3-pip${NC}"
        elif command_exists yum; then
            echo "  • CentOS/RHEL: ${CYAN}sudo yum install python3 python3-pip${NC}"
        elif command_exists dnf; then
            echo "  • Fedora: ${CYAN}sudo dnf install python3 python3-pip${NC}"
        elif command_exists pacman; then
            echo "  • Arch Linux: ${CYAN}sudo pacman -S python python-pip${NC}"
        elif command_exists zypper; then
            echo "  • openSUSE: ${CYAN}sudo zypper install python3 python3-pip${NC}"
        elif command_exists apk; then
            echo "  • Alpine Linux: ${CYAN}sudo apk add python3 py3-pip${NC}"
        else
            echo "  • Use your distribution's package manager to install python3"
        fi
        echo "  • Or download from: ${CYAN}https://python.org${NC}"
    else
        echo "  • Download from: ${CYAN}https://python.org${NC}"
    fi
}

# Function to make script executable (for first-time setup)
setup_executable() {
    if [[ ! -x "$SCRIPT_DIR/$SCRIPT_NAME" ]]; then
        echo -e "${YELLOW}Making script executable...${NC}"
        chmod +x "$SCRIPT_DIR/$SCRIPT_NAME"
        echo -e "${GREEN}✓ Script is now executable${NC}"
        echo
    fi
}

# Function to create optimized desktop shortcuts
create_desktop_shortcut() {
    local shortcut_created=false
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - Create .command file for Finder double-click
        local shortcut_path="$SCRIPT_DIR/NW.js Automator.command"
        cat > "$shortcut_path" << EOF
#!/bin/bash
cd "$(dirname "\$0")"
./$SCRIPT_NAME
EOF
        chmod +x "$shortcut_path"
        echo -e "${GREEN}✓ Created macOS shortcut: ${CYAN}NW.js Automator.command${NC}"
        echo "  ${BLUE}Double-click 'NW.js Automator.command' in Finder to run${NC}"
        shortcut_created=true
    else
        # Linux - Create comprehensive .desktop file
        local desktop_dirs=("$HOME/Desktop" "$HOME/.local/share/applications")
        local de=$(detect_desktop_environment)
        local terminal_cmd=$(get_terminal_command "$de")
        
        # Try to create desktop shortcut
        for desktop_dir in "${desktop_dirs[@]}"; do
            if [[ -d "$desktop_dir" ]] || mkdir -p "$desktop_dir" 2>/dev/null; then
                local shortcut_path="$desktop_dir/RPG-Maker-NWjs-Automator.desktop"
                
                # Create comprehensive .desktop file
                cat > "$shortcut_path" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=RPG Maker NW.js Automator
GenericName=Game Runtime Optimizer
Comment=Automate NW.js implementation for RPG Maker MV/MZ games - Save space and enable developer tools
Exec=$terminal_cmd bash -c 'cd "'"$SCRIPT_DIR"'" && ./'"'$SCRIPT_NAME'"'; echo; echo "Press Enter to close..."; read'
Icon=applications-games
Path=$SCRIPT_DIR
Terminal=true
Categories=Game;Development;Utility;System;
Keywords=RPG;Maker;NW.js;Game;Automation;Optimizer;Developer;Tools;
StartupNotify=true
MimeType=application/x-executable;
Actions=OpenFolder;ShowHelp;

[Desktop Action OpenFolder]
Name=Open Script Folder
Exec=xdg-open "$SCRIPT_DIR"

[Desktop Action ShowHelp]
Name=View Documentation
Exec=xdg-open "$SCRIPT_DIR/README.md"
EOF
                chmod +x "$shortcut_path"
                
                if [[ "$desktop_dir" == "$HOME/Desktop" ]]; then
                    echo -e "${GREEN}✓ Created desktop shortcut: ${CYAN}RPG-Maker-NWjs-Automator.desktop${NC}"
                    echo "  ${BLUE}Double-click the shortcut on your desktop to run${NC}"
                else
                    echo -e "${GREEN}✓ Added to applications menu: ${CYAN}RPG Maker NW.js Automator${NC}"
                    echo "  ${BLUE}Find it in your applications menu under Games/Development${NC}"
                fi
                shortcut_created=true
            fi
        done
        
        # Also create a simple launcher script for manual execution
        local launcher_path="$SCRIPT_DIR/nwjs-automator-launcher.sh"
        cat > "$launcher_path" << EOF
#!/bin/bash
# Simple launcher that can be executed from anywhere
cd "$SCRIPT_DIR"
./$SCRIPT_NAME
EOF
        chmod +x "$launcher_path"
        echo -e "${GREEN}✓ Created portable launcher: ${CYAN}nwjs-automator-launcher.sh${NC}"
        echo "  ${BLUE}Can be executed from anywhere: $launcher_path${NC}"
    fi
    
    if [[ "$shortcut_created" == true ]]; then
        echo
        echo -e "${PURPLE}Shortcut Benefits:${NC}"
        echo "  • ${GREEN}One-click access${NC} from desktop or applications menu"
        echo "  • ${GREEN}Automatic terminal handling${NC} - no command line needed"
        echo "  • ${GREEN}Path resolution${NC} - works from anywhere"
        echo "  • ${GREEN}Context menu actions${NC} - open folder, view help"
    fi
}

# Function to check and fix desktop file associations
ensure_desktop_integration() {
    if [[ "$OSTYPE" != "darwin"* ]] && command_exists update-desktop-database; then
        echo -e "${BLUE}Updating desktop database...${NC}"
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
        echo -e "${GREEN}✓ Desktop integration updated${NC}"
    fi
}

# Main function
main() {
    # Setup executable permissions
    setup_executable
    
    # Print header
    print_header
    
    # Change to script directory
    cd "$SCRIPT_DIR" || exit 1
    
    # Detect Python
    echo -e "${BLUE}Checking Python installation...${NC}"
    PYTHON_CMD=$(detect_python)
    
    if [[ -z "$PYTHON_CMD" ]]; then
        echo -e "${RED}✗ ERROR: Python 3 is not installed or not found in PATH${NC}"
        echo
        suggest_python_install
        echo
        echo -e "${YELLOW}After installing Python, restart this script.${NC}"
        read -p "Press Enter to exit..."
        exit 1
    fi
    
    echo -e "${GREEN}✓ Python found: ${CYAN}$PYTHON_CMD${NC}"
    
    # Show Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    echo -e "${BLUE}  Version: $PYTHON_VERSION${NC}"
    echo
    
    # Detect pip
    echo -e "${BLUE}Checking pip installation...${NC}"
    PIP_CMD=$(detect_pip "$PYTHON_CMD")
    
    if [[ -z "$PIP_CMD" ]]; then
        echo -e "${RED}✗ ERROR: pip is not installed${NC}"
        echo -e "${YELLOW}Please install pip using your system's package manager${NC}"
        echo
        read -p "Press Enter to exit..."
        exit 1
    fi
    
    echo -e "${GREEN}✓ pip found: ${CYAN}$PIP_CMD${NC}"
    echo
    
    # Check if requests module is installed
    echo -e "${BLUE}Checking required dependencies...${NC}"
    if ! $PYTHON_CMD -c "import requests" >/dev/null 2>&1; then
        echo -e "${YELLOW}Installing required dependencies...${NC}"
        if $PIP_CMD install requests --user; then
            echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
        else
            echo -e "${RED}✗ ERROR: Failed to install dependencies${NC}"
            echo "Please run '${CYAN}$PIP_CMD install requests --user${NC}' manually"
            echo
            read -p "Press Enter to exit..."
            exit 1
        fi
    else
        echo -e "${GREEN}✓ All dependencies are installed${NC}"
    fi
    echo
    
    # Ask about desktop shortcut creation (smarter detection)
    local shortcuts_exist=false
    [[ -f "$SCRIPT_DIR/NW.js Automator.command" ]] && shortcuts_exist=true
    [[ -f "$HOME/Desktop/RPG-Maker-NWjs-Automator.desktop" ]] && shortcuts_exist=true
    [[ -f "$HOME/.local/share/applications/RPG-Maker-NWjs-Automator.desktop" ]] && shortcuts_exist=true
    
    if [[ "$shortcuts_exist" == false ]]; then
        echo -e "${CYAN}Would you like to create desktop shortcuts for easy access? ${GREEN}(Recommended)${NC}"
        echo -e "${BLUE}This will create shortcuts on your desktop and in the applications menu${NC}"
        echo -n -e "${CYAN}Create shortcuts? (Y/n): ${NC}"
        read -r create_shortcut
        if [[ "$create_shortcut" != "n" ]] && [[ "$create_shortcut" != "N" ]]; then
            create_desktop_shortcut
            ensure_desktop_integration
            echo
        fi
    else
        echo -e "${GREEN}✓ Desktop shortcuts already exist${NC}"
        echo
    fi
    
    # Run the Python script
    echo -e "${GREEN}Starting NW.js Automator...${NC}"
    echo -e "${BLUE}─────────────────────────────────────────${NC}"
    echo
    
    if [[ -f "$SCRIPT_DIR/nwjs_automator.py" ]]; then
        $PYTHON_CMD "$SCRIPT_DIR/nwjs_automator.py"
        exit_code=$?
    else
        echo -e "${RED}✗ ERROR: nwjs_automator.py not found${NC}"
        echo "Please ensure this script is in the same folder as nwjs_automator.py"
        echo "Current directory: $SCRIPT_DIR"
        exit_code=1
    fi
    
    echo
    echo -e "${BLUE}─────────────────────────────────────────${NC}"
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✓ Script completed successfully!${NC}"
        echo -e "${BLUE}Your RPG Maker games are now optimized and ready to play.${NC}"
    else
        echo -e "${YELLOW}⚠ Script completed with some issues.${NC}"
        echo -e "${BLUE}Check the messages above for details.${NC}"
    fi
    
    # Keep terminal open with helpful message
    echo
    echo -e "${CYAN}Next time, you can run this tool by:${NC}"
    echo -e "  • ${GREEN}Double-clicking the desktop shortcut${NC}"
    echo -e "  • ${GREEN}Finding it in your applications menu${NC}"
    echo -e "  • ${GREEN}Running: $SCRIPT_DIR/$SCRIPT_NAME${NC}"
    echo
    read -p "Press Enter to exit..."
}

# Trap to handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}⚠ Operation cancelled by user.${NC}"; echo "No changes were made."; exit 1' INT

# Run main function
main "$@"