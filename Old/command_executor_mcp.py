#!/usr/bin/env python3
"""
Command Executor MCP Server
A dedicated MCP server for executing system commands safely
"""

from fastmcp import FastMCP
import asyncio
import os
from typing import Optional

mcp = FastMCP("Command_Executor")

# ============================================================================
# COMMAND EXECUTION TOOLS
# ============================================================================

@mcp.tool()
async def run_command(command: str, working_directory: Optional[str] = None, timeout: int = 300):
    """
    Execute system commands asynchronously (pip, npm, git, python, etc.).
    
    Args:
        command: Command string to execute
        working_directory: Directory to run command in (optional)
        timeout: Command timeout in seconds (default: 300)
    
    Returns:
        Formatted output with stdout, stderr, and return code
    
    Examples:
        run_command("pip install requests")
        run_command("python script.py")
        run_command("git status")
        run_command("npm install", working_directory="D:/myproject")
    """
    try:
        # Change to working directory if specified
        original_dir = None
        if working_directory:
            original_dir = os.getcwd()
            os.chdir(working_directory)
        
        # Execute command with timeout
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return f"❌ Command timed out after {timeout} seconds\nCommand: {command}"
        
        # Restore original directory
        if original_dir:
            os.chdir(original_dir)
        
        # Decode output (Windows often uses cp1252 or utf-8)
        stdout_text = stdout.decode('utf-8', errors='ignore').strip() if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore').strip() if stderr else ""
        
        # Format output
        output = f"Command: {command}\n"
        if working_directory:
            output += f"Working Directory: {working_directory}\n"
        output += f"Return Code: {process.returncode}\n"
        output += f"Success: {process.returncode == 0}\n"
        output += "=" * 60 + "\n\n"
        
        if stdout_text:
            output += f"Output:\n{stdout_text}\n\n"
        
        if stderr_text:
            output += f"Errors/Warnings:\n{stderr_text}\n"
        
        return output
        
    except Exception as e:
        if original_dir:
            os.chdir(original_dir)
        return f"❌ Error executing command: {str(e)}\nCommand: {command}"


@mcp.tool()
async def run_python_script(script_path: str, args: str = "", working_directory: Optional[str] = None):
    """
    Execute a Python script with arguments.
    
    Args:
        script_path: Path to Python script
        args: Command line arguments for the script
        working_directory: Directory to run script from (optional)
    
    Returns:
        Script output
    
    Examples:
        run_python_script("D:/scripts/test.py")
        run_python_script("script.py", "--verbose --output results.txt")
    """
    command = f"python {script_path} {args}".strip()
    return await run_command(command, working_directory=working_directory)


@mcp.tool()
async def install_package(package_name: str, upgrade: bool = False):
    """
    Install Python package using pip.
    
    Args:
        package_name: Package name to install (e.g., "requests", "numpy==1.24.0")
        upgrade: Upgrade if already installed (default: False)
    
    Returns:
        Installation output
    
    Examples:
        install_package("requests")
        install_package("numpy", upgrade=True)
    """
    command = f"pip install {package_name}"
    if upgrade:
        command += " --upgrade"
    
    return await run_command(command)


@mcp.tool()
async def uninstall_package(package_name: str):
    """
    Uninstall Python package using pip.
    
    Args:
        package_name: Package name to uninstall
    
    Returns:
        Uninstallation output
    
    Examples:
        uninstall_package("requests")
    """
    command = f"pip uninstall {package_name} -y"
    return await run_command(command)


@mcp.tool()
async def list_installed_packages():
    """
    List all installed Python packages.
    
    Returns:
        List of installed packages with versions
    """
    return await run_command("pip list")


@mcp.tool()
async def check_python_version():
    """
    Check Python version.
    
    Returns:
        Python version information
    """
    return await run_command("python --version")


@mcp.tool()
async def git_status(repository_path: Optional[str] = None):
    """
    Check git repository status.
    
    Args:
        repository_path: Path to git repository (optional, uses current directory)
    
    Returns:
        Git status output
    """
    return await run_command("git status", working_directory=repository_path)


@mcp.tool()
async def git_clone(repository_url: str, target_directory: Optional[str] = None):
    """
    Clone a git repository.
    
    Args:
        repository_url: Git repository URL
        target_directory: Directory to clone into (optional)
    
    Returns:
        Clone output
    
    Examples:
        git_clone("https://github.com/user/repo.git")
        git_clone("https://github.com/user/repo.git", "D:/projects/myrepo")
    """
    command = f"git clone {repository_url}"
    if target_directory:
        command += f" {target_directory}"
    
    return await run_command(command)


@mcp.tool()
async def npm_install(package_name: Optional[str] = None, working_directory: Optional[str] = None):
    """
    Install npm packages.
    
    Args:
        package_name: Package name (optional, installs from package.json if not provided)
        working_directory: Project directory (optional)
    
    Returns:
        Installation output
    
    Examples:
        npm_install()  # Install from package.json
        npm_install("express")
        npm_install("react", "D:/myproject")
    """
    command = f"npm install {package_name}" if package_name else "npm install"
    return await run_command(command, working_directory=working_directory)


@mcp.tool()
async def create_virtual_environment(env_name: str = "venv", location: Optional[str] = None):
    """
    Create Python virtual environment.
    
    Args:
        env_name: Name of virtual environment (default: "venv")
        location: Directory to create venv in (optional)
    
    Returns:
        Creation output
    
    Examples:
        create_virtual_environment()
        create_virtual_environment("myenv", "D:/projects/myproject")
    """
    command = f"python -m venv {env_name}"
    return await run_command(command, working_directory=location)


@mcp.tool()
async def run_batch_commands(commands: list[str], working_directory: Optional[str] = None):
    """
    Run multiple commands in sequence.
    
    Args:
        commands: List of commands to execute
        working_directory: Directory to run commands in (optional)
    
    Returns:
        Combined output from all commands
    
    Examples:
        run_batch_commands(["echo Starting...", "python script.py", "echo Done!"])
    """
    results = []
    
    for i, cmd in enumerate(commands, 1):
        result = await run_command(cmd, working_directory=working_directory)
        results.append(f"Command {i}/{len(commands)}:\n{result}\n{'='*60}\n")
    
    return "\n".join(results)


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
