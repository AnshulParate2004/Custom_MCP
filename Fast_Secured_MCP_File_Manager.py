#!/usr/bin/env python3
"""
Fast & Secure MCP File Manager
Combines FastMCP framework speed with security validation
"""

from fastmcp import FastMCP
from dotenv import load_dotenv
import os
import asyncio
import pathlib
import fnmatch
import shutil
import json
from typing import Optional, List
from datetime import datetime

load_dotenv()

mcp = FastMCP("MCP_File_Manager_Secure")

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

# Define allowed directories - CONFIGURE THIS FOR YOUR SECURITY NEEDS
ALLOWED_DIRECTORIES = [
    r"D:\MCP_Server",
    r"D:\Projects",
    os.path.expanduser("~"),  # User home directory
]

def normalize_path(path: str) -> str:
    """Normalize and resolve a path"""
    expanded = os.path.expanduser(path)
    absolute = os.path.abspath(expanded)
    try:
        resolved = os.path.realpath(absolute)
        return os.path.normpath(resolved)
    except Exception:
        return os.path.normpath(absolute)

def is_path_allowed(path: str) -> bool:
    """Check if a path is within allowed directories"""
    normalized_path = normalize_path(path)
    
    for allowed_dir in ALLOWED_DIRECTORIES:
        try:
            allowed_normalized = normalize_path(allowed_dir)
            relative = os.path.relpath(normalized_path, allowed_normalized)
            if not relative.startswith('..'):
                return True
        except ValueError:
            continue
    return False

def validate_path(path: str) -> str:
    """Validate and return the real path if allowed"""
    absolute = normalize_path(path)
    
    if not is_path_allowed(absolute):
        raise PermissionError(
            f"🚫 Access denied - path outside allowed directories: {absolute}\n"
            f"Allowed directories: {ALLOWED_DIRECTORIES}"
        )
    
    # Handle symlinks
    if os.path.exists(absolute):
        real_path = os.path.realpath(absolute)
        if not is_path_allowed(real_path):
            raise PermissionError(
                f"🚫 Access denied - symlink target outside allowed directories: {real_path}"
            )
        return real_path
    else:
        # For new files, verify parent directory
        parent_dir = os.path.dirname(absolute)
        if os.path.exists(parent_dir):
            real_parent = os.path.realpath(parent_dir)
            if not is_path_allowed(real_parent):
                raise PermissionError(
                    f"🚫 Access denied - parent directory outside allowed directories: {real_parent}"
                )
        return absolute

def format_size(bytes: int) -> str:
    """Format file size in human-readable format"""
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    if bytes == 0:
        return '0 B'
    
    import math
    i = min(int(math.log(bytes) / math.log(1024)), len(units) - 1)
    size = bytes / (1024 ** i)
    return f"{size:.2f} {units[i]}"

# ============================================================================
# FILE OPERATIONS
# ============================================================================

@mcp.tool()
async def write_file(filepath: str, content: str, mode: str = "w"):
    """
    Create new file or overwrite/append to existing file (SECURE).
    Auto-creates parent directories if missing.
    
    Args:
        filepath: Absolute or relative file path
        content: Text content to write
        mode: "w" to overwrite (default), "a" to append
    
    Returns:
        Success message with file path and size
    
    Examples:
        write_file("./app.py", "print('Hello')")
        write_file("D:/notes.txt", "New line", mode="a")
    """
    try:
        valid_path = validate_path(filepath)
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(valid_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Write the file
        with open(valid_path, mode, encoding='utf-8') as f:
            f.write(content)
        
        file_size = os.path.getsize(valid_path)
        
        action = "Appended to" if mode == "a" else "Created/Overwritten"
        result = f"✅ {action} file successfully!\n"
        result += f"Path: {valid_path}\n"
        result += f"Size: {format_size(file_size)}\n"
        result += f"Content length: {len(content)} characters"
        
        return result
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def read_file(filepath: str):
    """
    Read complete file content with metadata (SECURE).
    
    Args:
        filepath: Path to file (absolute or relative)
    
    Returns:
        File content with path and size information
    
    Examples:
        read_file("./config.json")
        read_file("D:/projects/app.py")
    """
    try:
        valid_path = validate_path(filepath)
        
        with open(valid_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_size = os.path.getsize(valid_path)
        
        result = f"File: {valid_path}\n"
        result += f"Size: {format_size(file_size)}\n"
        result += f"{'='*50}\n"
        result += content
        
        return result
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def append_to_file(filepath: str, content: str, position: str = "end", marker: str = ""):
    """
    Add content at semantic positions using text markers (SECURE).
    
    Args:
        filepath: Path to existing file
        content: Text to insert
        position: "end", "before_marker", "after_marker", "before_last_line"
        marker: Search text (required for marker-based positions)
    
    Returns:
        Success message with insertion details
    
    Examples:
        append_to_file("app.py", "def new():\\n    pass")
        append_to_file("app.py", "import os\\n", "before_marker", "if __name__")
    """
    try:
        valid_path = validate_path(filepath)
        
        if not os.path.exists(valid_path):
            return f"❌ Error: File does not exist: {valid_path}"
        
        with open(valid_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        if position == "end":
            new_content = existing_content + content
        
        elif position == "before_last_line":
            lines = existing_content.split('\n')
            if len(lines) > 0:
                lines.insert(-1, content.strip())
                new_content = '\n'.join(lines)
            else:
                new_content = content
        
        elif position == "before_marker":
            if not marker:
                return "❌ Error: marker is required for 'before_marker' position"
            if marker in existing_content:
                new_content = existing_content.replace(marker, f"{content}\n{marker}", 1)
            else:
                return f"❌ Error: Marker '{marker}' not found in file"
        
        elif position == "after_marker":
            if not marker:
                return "❌ Error: marker is required for 'after_marker' position"
            if marker in existing_content:
                parts = existing_content.split(marker, 1)
                new_content = f"{parts[0]}{marker}\n{content}{parts[1]}"
            else:
                return f"❌ Error: Marker '{marker}' not found in file"
        else:
            return f"❌ Error: Unknown position '{position}'"
        
        with open(valid_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        new_size = os.path.getsize(valid_path)
        
        result = f"✅ Successfully appended to file!\n"
        result += f"Path: {valid_path}\n"
        result += f"Position: {position}\n"
        if marker:
            result += f"Marker: {marker}\n"
        result += f"New file size: {format_size(new_size)}"
        
        return result
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def list_files(directory: str = ".", pattern: str = "*"):
    """
    List files/directories with optional glob pattern filtering (SECURE).
    
    Args:
        directory: Directory path (default: current)
        pattern: Glob pattern like "*.py", "test_*", "*" (default: all)
    
    Returns:
        Formatted list with file types and sizes
    
    Examples:
        list_files("./src")
        list_files("D:/projects", "*.json")
    """
    try:
        valid_dir = validate_path(directory)
        
        import glob
        search_pattern = os.path.join(valid_dir, pattern)
        files = glob.glob(search_pattern)
        
        result = f"Directory: {valid_dir}\n"
        result += f"Pattern: {pattern}\n"
        result += f"Found {len(files)} file(s)\n"
        result += f"{'='*50}\n"
        
        for file in sorted(files):
            size = os.path.getsize(file) if os.path.isfile(file) else 0
            file_type = "DIR" if os.path.isdir(file) else "FILE"
            result += f"[{file_type}] {os.path.basename(file)} ({format_size(size)})\n"
        
        return result
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def list_directory_with_sizes(directory: str = ".", sort_by: str = "name"):
    """
    List directory contents with file sizes and totals (SECURE).
    
    Args:
        directory: Directory path
        sort_by: "name" or "size"
    
    Returns:
        Formatted list with statistics
    """
    try:
        valid_path = validate_path(directory)
        entries = []
        
        for entry in os.listdir(valid_path):
            entry_path = os.path.join(valid_path, entry)
            is_dir = os.path.isdir(entry_path)
            size = 0 if is_dir else os.path.getsize(entry_path)
            
            entries.append({
                "name": entry,
                "is_directory": is_dir,
                "size": size
            })
        
        if sort_by == "size":
            entries.sort(key=lambda x: x["size"], reverse=True)
        else:
            entries.sort(key=lambda x: x["name"])
        
        formatted = []
        total_files = 0
        total_dirs = 0
        total_size = 0
        
        for entry in entries:
            prefix = "[DIR]" if entry["is_directory"] else "[FILE]"
            size_str = "" if entry["is_directory"] else format_size(entry["size"])
            formatted.append(f"{prefix} {entry['name']:<30} {size_str:>10}")
            
            if entry["is_directory"]:
                total_dirs += 1
            else:
                total_files += 1
                total_size += entry["size"]
        
        formatted.append("")
        formatted.append(f"Total: {total_files} files, {total_dirs} directories")
        formatted.append(f"Combined size: {format_size(total_size)}")
        
        return "\n".join(formatted)
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def search_files(directory: str, pattern: str, exclude_patterns: List[str] = None):
    """
    Search for files matching a pattern recursively (SECURE).
    
    Args:
        directory: Root directory to search
        pattern: Glob pattern like "*.py", "test_*"
        exclude_patterns: List of patterns to exclude
    
    Returns:
        List of matching file paths
    
    Examples:
        search_files("./src", "*.py")
        search_files("D:/projects", "test_*.js", ["node_modules/*"])
    """
    try:
        if exclude_patterns is None:
            exclude_patterns = []
        
        valid_path = validate_path(directory)
        results = []
        
        for dirpath, dirnames, filenames in os.walk(valid_path):
            # Filter directories
            dirnames[:] = [d for d in dirnames 
                          if not any(fnmatch.fnmatch(d, p) for p in exclude_patterns)]
            
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(file_path, valid_path)
                
                if any(fnmatch.fnmatch(relative_path, p) for p in exclude_patterns):
                    continue
                
                if fnmatch.fnmatch(relative_path, pattern):
                    results.append(file_path)
        
        content = "\n".join(results) if results else "No matches found"
        return f"Found {len(results)} matches:\n{content}"
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def get_file_info(filepath: str):
    """
    Get detailed file metadata (SECURE).
    
    Args:
        filepath: Path to file
    
    Returns:
        File information including size, dates, permissions
    """
    try:
        valid_path = validate_path(filepath)
        stat = os.stat(valid_path)
        
        info = {
            "Path": valid_path,
            "Size": format_size(stat.st_size),
            "Created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "Modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "Accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "Is Directory": os.path.isdir(valid_path),
            "Is File": os.path.isfile(valid_path),
            "Permissions": oct(stat.st_mode)[-3:]
        }
        
        return "\n".join(f"{key}: {value}" for key, value in info.items())
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def move_file(source: str, destination: str):
    """
    Move or rename a file (SECURE).
    
    Args:
        source: Source file path
        destination: Destination file path
    
    Returns:
        Success message
    """
    try:
        valid_source = validate_path(source)
        valid_dest = validate_path(destination)
        
        shutil.move(valid_source, valid_dest)
        return f"✅ Successfully moved {valid_source} to {valid_dest}"
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def create_directory(directory: str):
    """
    Create a directory (SECURE).
    
    Args:
        directory: Directory path to create
    
    Returns:
        Success message
    """
    try:
        valid_path = validate_path(directory)
        os.makedirs(valid_path, exist_ok=True)
        return f"✅ Successfully created directory: {valid_path}"
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================================================================
# ADVANCED EDITING TOOLS
# ============================================================================

@mcp.tool()
async def edit_file_at_position(
    filepath: str,
    text_to_insert: str,
    position_type: str = "line_column",
    line: int = None,
    column: int = None,
    byte_index: int = None,
    operation: str = "insert"
):
    """
    Surgical file editing at precise coordinates (SECURE).
    
    Args:
        filepath: Path to file
        text_to_insert: Text to insert/replace
        position_type: "line_column" or "byte_index"
        line: Line number (1-indexed)
        column: Column offset (0-indexed)
        byte_index: Byte position (0-indexed)
        operation: "insert" or "replace"
    
    Returns:
        Success message with edit details
    """
    try:
        valid_path = validate_path(filepath)
        
        if not os.path.exists(valid_path):
            return f"❌ Error: File does not exist: {valid_path}"
        
        with open(valid_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        # Calculate position
        if position_type == "line_column":
            if line is None or column is None:
                return "❌ Error: line and column are required for line_column position_type"
            
            lines = content.split('\n')
            target_line = line - 1
            
            if target_line < 0 or target_line >= len(lines):
                return f"❌ Error: Line {line} is out of range (file has {len(lines)} lines)"
            
            if column < 0 or column > len(lines[target_line]):
                return f"❌ Error: Column {column} is out of range for line {line}"
            
            position = sum(len(l) + 1 for l in lines[:target_line]) + column
            
        elif position_type == "byte_index":
            if byte_index is None:
                return "❌ Error: byte_index is required for byte_index position_type"
            
            if byte_index < 0 or byte_index > len(content):
                return f"❌ Error: Byte index {byte_index} is out of range"
            
            position = byte_index
        else:
            return f"❌ Error: Invalid position_type '{position_type}'"
        
        # Perform operation
        if operation == "insert":
            new_content = content[:position] + text_to_insert + content[position:]
        elif operation == "replace":
            replace_length = len(text_to_insert)
            new_content = content[:position] + text_to_insert + content[position + replace_length:]
        else:
            return f"❌ Error: Invalid operation '{operation}'"
        
        with open(valid_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        new_size = len(new_content)
        
        result = f"✅ File edited successfully!\n"
        result += f"Path: {valid_path}\n"
        result += f"Operation: {operation}\n"
        result += f"Original size: {original_size} bytes\n"
        result += f"New size: {new_size} bytes\n"
        result += f"Size change: {new_size - original_size:+d} bytes"
        
        return result
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def find_and_replace(
    filepath: str,
    find_text: str,
    replace_text: str,
    all_occurrences: bool = False
):
    """
    Find and replace text in a file (SECURE).
    
    Args:
        filepath: Path to file
        find_text: Text to find
        replace_text: Text to replace with
        all_occurrences: Replace all (default: False, only first)
    
    Returns:
        Success message with replacement count
    """
    try:
        valid_path = validate_path(filepath)
        
        if not os.path.exists(valid_path):
            return f"❌ Error: File does not exist: {valid_path}"
        
        with open(valid_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if find_text not in content:
            return f"❌ Error: Text '{find_text}' not found in file"
        
        occurrence_count = content.count(find_text)
        
        if all_occurrences:
            new_content = content.replace(find_text, replace_text)
            replaced_count = occurrence_count
        else:
            new_content = content.replace(find_text, replace_text, 1)
            replaced_count = 1
        
        with open(valid_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        result = f"✅ Text replaced successfully!\n"
        result += f"Path: {valid_path}\n"
        result += f"Total occurrences: {occurrence_count}\n"
        result += f"Replaced: {replaced_count} occurrence(s)"
        
        return result
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def insert_at_line(
    filepath: str,
    line_number: int,
    text: str,
    position: str = "start"
):
    """
    Insert text at the start or end of a specific line (SECURE).
    
    Args:
        filepath: Path to file
        line_number: Line number (1-indexed)
        text: Text to insert
        position: "start" or "end" of line
    
    Returns:
        Success message
    """
    try:
        valid_path = validate_path(filepath)
        
        if not os.path.exists(valid_path):
            return f"❌ Error: File does not exist: {valid_path}"
        
        with open(valid_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_number < 1 or line_number > len(lines):
            return f"❌ Error: Line {line_number} is out of range (file has {len(lines)} lines)"
        
        target_idx = line_number - 1
        
        if position == "start":
            lines[target_idx] = text + lines[target_idx]
        elif position == "end":
            lines[target_idx] = lines[target_idx].rstrip('\n') + text + '\n'
        else:
            return f"❌ Error: Invalid position '{position}'"
        
        with open(valid_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        result = f"✅ Text inserted at line {position}!\n"
        result += f"Path: {valid_path}\n"
        result += f"Line: {line_number}\n"
        result += f"New line: {lines[target_idx].rstrip()}"
        
        return result
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def delete_text_from_file(filepath: str, position: int, length: int):
    """
    Remove specific character range from file (SECURE).
    
    Args:
        filepath: Path to file
        position: Start index (0-indexed)
        length: Number of characters to delete
    
    Returns:
        Success message with deletion preview
    """
    try:
        valid_path = validate_path(filepath)
        
        if not os.path.exists(valid_path):
            return f"❌ Error: File does not exist: {valid_path}"
        
        with open(valid_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        if position < 0 or position >= original_size:
            return f"❌ Error: Position {position} is out of range"
        
        if length <= 0:
            return f"❌ Error: Length must be positive"
        
        end_position = min(position + length, original_size)
        deleted_text = content[position:end_position]
        new_content = content[:position] + content[end_position:]
        
        with open(valid_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        result = f"✅ Text deleted successfully!\n"
        result += f"Path: {valid_path}\n"
        result += f"Position: {position}\n"
        result += f"Characters deleted: {end_position - position}\n"
        result += f"Deleted text: '{deleted_text[:50]}...'" if len(deleted_text) > 50 else f"Deleted text: '{deleted_text}'"
        
        return result
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================================================================
# SYSTEM TOOLS
# ============================================================================

@mcp.tool()
async def open_in_vscode(filepath: str):
    """
    Launch file in VS Code editor.
    
    Args:
        filepath: File path (absolute or relative)
    
    Returns:
        Success confirmation
    """
    try:
        valid_path = validate_path(filepath)
        
        vscode_paths = [
            'code',
            r'C:\Users\KAIZEN\AppData\Local\Programs\Microsoft VS Code\Code.exe',
            r'C:\Program Files\Microsoft VS Code\Code.exe',
        ]
        
        for vscode_path in vscode_paths:
            try:
                process = await asyncio.create_subprocess_shell(
                    f'"{vscode_path}" "{valid_path}"',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                if process.returncode == 0:
                    return f"✅ Opened in VS Code: {valid_path}"
            except:
                continue
        
        return "❌ Could not find VS Code installation"
        
    except PermissionError as e:
        return f"🚫 {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def list_allowed_directories():
    """
    List directories that are allowed for file operations.
    
    Returns:
        List of allowed directories
    """
    result = "🔒 Allowed Directories (Security Configuration):\n"
    result += "="*60 + "\n"
    for i, directory in enumerate(ALLOWED_DIRECTORIES, 1):
        result += f"{i}. {directory}\n"
    result += "\n💡 Only files within these directories can be accessed."
    return result

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":

    mcp.run(transport="stdio")
