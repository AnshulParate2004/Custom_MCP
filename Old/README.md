# 🤖 Multimodular Agentic AI

A comprehensive collection of MCP (Model Context Protocol) servers that empower Claude AI with advanced capabilities for browser automation, file management, and command execution. Transform Claude into a powerful agentic AI system that can interact with your computer, manage files, and control browsers.

## 🌟 Features

### 🌐 Browser Automation
- **Full Browser Control**: Navigate, click, type, scroll, and interact with web pages
- **Tab Management**: Create, switch, and close browser tabs
- **DOM Inspection**: Access page elements, extract content, and capture screenshots
- **JavaScript Execution**: Run custom JavaScript on any webpage
- **Screenshot Capture**: Take screenshots for visual analysis

### 📁 Secure File Management
- **Path Validation**: Built-in security with configurable allowed directories
- **CRUD Operations**: Create, read, update, and delete files safely
- **Advanced Editing**: Precise text insertion, find & replace, line-based editing
- **Directory Operations**: List, search, and manage directories
- **File Metadata**: Get detailed file information and statistics

### ⚡ Command Execution
- **System Commands**: Execute any system command (pip, npm, git, etc.)
- **Python Scripts**: Run Python scripts with arguments
- **Package Management**: Install and uninstall Python packages
- **Git Operations**: Clone repositories, check status
- **Virtual Environments**: Create and manage Python venvs
- **Batch Commands**: Execute multiple commands in sequence

## 🏗️ Architecture

```
Claude AI (Agent)
    ↓
MCP Protocol
    ↓
┌─────────────────────────────────────┐
│   MCP Servers (This Repository)    │
├─────────────────────────────────────┤
│  • Browser Automation Server        │
│  • Secure File Manager Server       │
│  • Command Executor Server          │
└─────────────────────────────────────┘
    ↓
System Resources (Browser, Files, Terminal)
```

## 🔒 Security Features

### File Manager Security
- **Path Validation**: Only allows access to pre-configured directories
- **Symlink Protection**: Prevents following symlinks outside allowed directories
- **Directory Traversal Prevention**: Blocks `../` and other traversal attempts
- **Read-only Mode Option**: Can be configured to prevent modifications

### Browser Automation Security
- **Session Management**: Automatic cleanup of browser sessions
- **Timeout Protection**: Sessions automatically expire after inactivity
- **Controlled Downloads**: Downloads saved to a dedicated directory
- **No Persistent State**: Browser starts fresh each session

### Command Execution Security
- **Working Directory Control**: Commands run in specified directories
- **Timeout Protection**: Commands automatically killed after timeout
- **Output Sanitization**: Safe handling of command output
- **Error Isolation**: Errors don't crash the server

## 📚 Available Tools

### Browser Automation (17 tools)
- `browser_start`, `browser_close`, `browser_navigate`
- `browser_get_state`, `browser_get_content`, `browser_screenshot`
- `browser_click`, `browser_type`, `browser_scroll`
- `browser_go_back`, `browser_press_key`, `browser_wait`
- `browser_list_tabs`, `browser_switch_tab`, `browser_close_tab`
- `browser_execute_javascript`

### File Manager (16 tools)
- `write_file`, `read_file`, `append_to_file`
- `list_files`, `list_directory_with_sizes`, `search_files`
- `get_file_info`, `move_file`, `create_directory`
- `edit_file_at_position`, `find_and_replace`, `insert_at_line`
- `delete_text_from_file`, `open_in_vscode`, `list_allowed_directories`

### Command Executor (11 tools)
- `run_command`, `run_python_script`, `run_batch_commands`
- `install_package`, `uninstall_package`, `list_installed_packages`
- `check_python_version`, `git_status`, `git_clone`
- `npm_install`, `create_virtual_environment`

## 🤝 Contributing

Contributions are welcome! Clone the repository, create a virtual environment, install dependencies, and start contributing.

## 📝 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Browser won't start
- Ensure Chrome/Chromium is installed
- Check if port 9222 is already in use
- Try running in headless mode: `browser_start(headless=True)`

### File access denied
- Check `ALLOWED_DIRECTORIES` in `Fast_Secured_MCP_File_Manager.py`
- Ensure paths use raw strings (e.g., `r"D:\Projects"`)
- Verify directory permissions

### Commands fail to execute
- Check command syntax for your OS (Windows vs Unix)
- Verify working directory exists
- Ensure required programs (pip, git, npm) are in PATH

### Claude doesn't see the tools
- Restart Claude Desktop after configuration changes
- Verify `claude_desktop_config.json` syntax
- Check server paths are correct
- Look for errors in Claude Desktop logs


## 📧 Contact

For questions, suggestions, or issues, please:
- Open an issue on GitHub
- Contact the maintainer
- Join our community discussions

## 💖 Acknowledgments

Special thanks to:
- Anthropic for Claude AI and MCP Protocol
- The FastMCP community
- Browser Use library contributors
- All open-source contributors

---

**Made with ❤️ by [AnshulParate](https://github.com/AnshulParate2004)**
