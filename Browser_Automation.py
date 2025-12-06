"""
MCP Server for Browser Automation with Claude as the Agent

This server exposes browser control tools via the MCP protocol, allowing Claude
to act as an intelligent agent that controls a Chrome browser instance.

Architecture:
    Claude (AI Agent) → MCP Server (Browser Tools) → Browser (Chrome/Chromium)

Features:
    - Direct browser control (navigation, clicking, typing, scrolling)
    - Tab management (list, switch, close, new tabs)
    - Page state inspection (DOM elements, content, screenshots)
    - JavaScript execution
    - Session management with automatic cleanup

Benefits:
    - Claude makes all decisions (no separate AI agent needed)
    - Cost-effective (no additional API calls)
    - Full context awareness (Claude sees everything)
    - Complete control over automation
    - Fast response times

Requirements:
    - mcp (MCP SDK)
    - browser-use (Browser automation library)
    - Chrome or Chromium browser installed

Author: Enhanced for production use
Version: 2.1.0
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Optional

# Configure minimal logging to stderr
logging.basicConfig(
    stream=sys.stderr,
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logging.disable(logging.CRITICAL)

logger = logging.getLogger(__name__)

# ============================================================================
# Dependency Checks
# ============================================================================

try:
    import mcp.server.stdio
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    from mcp.server.models import InitializationOptions
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print('ERROR: MCP SDK not installed. Install with: pip install mcp', file=sys.stderr)
    sys.exit(1)

try:
    from browser_use.browser import BrowserProfile, BrowserSession
    from browser_use.tools.service import Tools
    from browser_use.filesystem.file_system import FileSystem
    from browser_use.browser.events import (
        NavigateToUrlEvent,
        ClickElementEvent,
        TypeTextEvent,
        ScrollEvent,
        GoBackEvent,
        SwitchTabEvent,
        CloseTabEvent
    )
    BROWSER_USE_AVAILABLE = True
except ImportError:
    BROWSER_USE_AVAILABLE = False
    print('ERROR: browser-use not installed. Install with: pip install browser-use', file=sys.stderr)
    sys.exit(1)


class ClaudeAgentBrowserServer:
    """MCP Server exposing browser control tools for Claude."""
    
    def __init__(self, session_timeout_minutes: int = 10):
        """Initialize the MCP server."""
        self.server = Server('browser-use-claude-agent')
        self.session_timeout_minutes = session_timeout_minutes
        
        # Session management
        self.active_sessions: dict[str, dict[str, Any]] = {}
        self.current_session: Optional[BrowserSession] = None
        self.tools: Optional[Tools] = None
        self.file_system: Optional[FileSystem] = None
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configure MCP server request handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """Return list of all available browser control tools."""
            return self._get_tool_definitions()
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str,
            arguments: Optional[dict[str, Any]]
        ) -> list[types.TextContent]:
            """Handle tool execution requests from Claude."""
            try:
                result = await self._execute_tool(name, arguments or {})
                return [types.TextContent(type='text', text=result)]
            except Exception as e:
                error_msg = f'Error executing {name}: {str(e)}'
                logger.error(error_msg, exc_info=True)
                return [types.TextContent(type='text', text=error_msg)]
    
    def _get_tool_definitions(self) -> list[types.Tool]:
        """Define all available browser control tools."""
        return [
            types.Tool(
                name='browser_start',
                description='Start a new browser session. Must be called before any other browser commands.',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'headless': {
                            'type': 'boolean',
                            'description': 'Run browser without visible window',
                            'default': False
                        }
                    }
                }
            ),
            
            types.Tool(
                name='browser_close',
                description='Close the current browser session and cleanup all resources.',
                inputSchema={'type': 'object', 'properties': {}}
            ),
            
            types.Tool(
                name='browser_navigate',
                description='Navigate to a URL. Waits for page to load before returning.',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'url': {
                            'type': 'string',
                            'description': 'Full URL including protocol (http:// or https://)'
                        },
                        'new_tab': {
                            'type': 'boolean',
                            'description': 'Open in new tab instead of current tab',
                            'default': False
                        }
                    },
                    'required': ['url']
                }
            ),
            
            types.Tool(
                name='browser_go_back',
                description='Navigate back to previous page in browser history.',
                inputSchema={'type': 'object', 'properties': {}}
            ),
            
            types.Tool(
                name='browser_get_state',
                description='Get current page state including URL, title, and ALL interactive elements with their indices. ALWAYS call this before trying to interact with elements.',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'include_screenshot': {
                            'type': 'boolean',
                            'description': 'Include base64 screenshot of current page',
                            'default': False
                        }
                    }
                }
            ),
            
            types.Tool(
                name='browser_get_content',
                description='Extract all text content from the current page. Useful for reading articles or extracting information.',
                inputSchema={'type': 'object', 'properties': {}}
            ),
            
            types.Tool(
                name='browser_screenshot',
                description='Capture a screenshot of the current page and return as base64 encoded PNG.',
                inputSchema={'type': 'object', 'properties': {}}
            ),
            
            types.Tool(
                name='browser_click',
                description='Click an element on the page by its index. Get indices from browser_get_state first.',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'index': {
                            'type': 'integer',
                            'description': 'Element index from browser_get_state'
                        }
                    },
                    'required': ['index']
                }
            ),
            
            types.Tool(
                name='browser_type',
                description='Type text into an input field. Get the input field index from browser_get_state first.',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'index': {
                            'type': 'integer',
                            'description': 'Index of input element from browser_get_state'
                        },
                        'text': {
                            'type': 'string',
                            'description': 'Text to type into the element'
                        }
                    },
                    'required': ['index', 'text']
                }
            ),
            
            types.Tool(
                name='browser_scroll',
                description='Scroll the current page up or down. Useful for viewing content not visible on initial load.',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'direction': {
                            'type': 'string',
                            'enum': ['up', 'down'],
                            'description': 'Scroll direction',
                            'default': 'down'
                        },
                        'amount': {
                            'type': 'integer',
                            'description': 'Pixels to scroll (500 = half viewport)',
                            'default': 500
                        }
                    }
                }
            ),
            
            types.Tool(
                name='browser_press_key',
                description='Press a keyboard key. Common keys: "Enter", "Tab", "Escape", "ArrowDown", "ArrowUp".',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'key': {
                            'type': 'string',
                            'description': 'Key name to press (e.g., "Enter", "Tab", "Escape")'
                        }
                    },
                    'required': ['key']
                }
            ),
            
            types.Tool(
                name='browser_wait',
                description='Wait for a specified duration. Useful after actions that need time to complete.',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'seconds': {
                            'type': 'number',
                            'description': 'Number of seconds to wait',
                            'default': 1.0
                        }
                    }
                }
            ),
            
            types.Tool(
                name='browser_list_tabs',
                description='List all open browser tabs with their IDs, URLs, and titles.',
                inputSchema={'type': 'object', 'properties': {}}
            ),
            
            types.Tool(
                name='browser_switch_tab',
                description='Switch to a different browser tab by its 4-character ID.',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'tab_id': {
                            'type': 'string',
                            'description': 'The 4-character tab ID from browser_list_tabs'
                        }
                    },
                    'required': ['tab_id']
                }
            ),
            
            types.Tool(
                name='browser_close_tab',
                description='Close a specific browser tab by its 4-character ID.',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'tab_id': {
                            'type': 'string',
                            'description': 'The 4-character tab ID to close'
                        }
                    },
                    'required': ['tab_id']
                }
            ),
            
            types.Tool(
                name='browser_execute_javascript',
                description='Execute custom JavaScript code on the current page. Returns the result of the executed code.',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'script': {
                            'type': 'string',
                            'description': 'JavaScript code to execute'
                        }
                    },
                    'required': ['script']
                }
            ),
        ]
    
    async def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Route tool execution to appropriate handler."""
        
        # Session management tools
        if tool_name == 'browser_start':
            return await self._start_browser(arguments.get('headless', False))
        elif tool_name == 'browser_close':
            return await self._close_browser()
        
        # All other tools require an active session
        if not self.current_session:
            return json.dumps({
                'error': 'No active browser session',
                'message': 'Call browser_start first'
            })
        
        # Route to handlers
        handlers = {
            'browser_navigate': lambda: self._navigate(arguments['url'], arguments.get('new_tab', False)),
            'browser_get_state': lambda: self._get_browser_state(arguments.get('include_screenshot', False)),
            'browser_get_content': lambda: self._get_page_content(),
            'browser_screenshot': lambda: self._take_screenshot(),
            'browser_click': lambda: self._click(arguments['index']),
            'browser_type': lambda: self._type_text(arguments['index'], arguments['text']),
            'browser_scroll': lambda: self._scroll(arguments.get('direction', 'down'), arguments.get('amount', 500)),
            'browser_go_back': lambda: self._go_back(),
            'browser_press_key': lambda: self._press_key(arguments['key']),
            'browser_list_tabs': lambda: self._list_tabs(),
            'browser_switch_tab': lambda: self._switch_tab(arguments['tab_id']),
            'browser_close_tab': lambda: self._close_tab(arguments['tab_id']),
            'browser_execute_javascript': lambda: self._execute_javascript(arguments['script']),
            'browser_wait': lambda: self._wait(arguments.get('seconds', 1.0)),
        }
        
        handler = handlers.get(tool_name)
        if not handler:
            return json.dumps({'error': 'Unknown tool', 'tool_name': tool_name})
        
        try:
            return await handler()
        except Exception as e:
            logger.error(f'Error in {tool_name}: {e}', exc_info=True)
            return json.dumps({'error': str(e), 'tool_name': tool_name})
    
    async def _start_browser(self, headless: bool = False) -> str:
        """Start a new browser session."""
        if self.current_session:
            return json.dumps({'error': 'Browser session already active'})
        
        try:
            profile = BrowserProfile(
                downloads_path=str(Path.home() / 'Downloads' / 'browser-use-mcp'),
                wait_between_actions=0.5,
                keep_alive=True,
                headless=headless,
                disable_security=False
            )
            
            self.current_session = BrowserSession(browser_profile=profile)
            await self.current_session.start()
            self._track_session(self.current_session)
            
            self.tools = Tools()
            self.file_system = FileSystem(base_dir=Path.home() / '.browser-use-mcp')
            
            return json.dumps({
                'success': True,
                'message': 'Browser started successfully',
                'headless': headless,
                'next_step': 'Use browser_navigate to go to a URL'
            })
        except Exception as e:
            return json.dumps({'error': 'Failed to start browser', 'details': str(e)})
    
    async def _close_browser(self) -> str:
        """Close the current browser session."""
        if not self.current_session:
            return json.dumps({'message': 'No active browser session'})
        
        try:
            session_id = self.current_session.id
            
            if hasattr(self.current_session, 'kill'):
                await self.current_session.kill()
            elif hasattr(self.current_session, 'close'):
                await self.current_session.close()
            
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            self.current_session = None
            self.tools = None
            self.file_system = None
            
            return json.dumps({'success': True, 'message': 'Browser closed successfully'})
        except Exception as e:
            return json.dumps({'error': 'Failed to close browser', 'details': str(e)})
    
    async def _navigate(self, url: str, new_tab: bool = False) -> str:
        """Navigate to a URL."""
        self._update_session_activity(self.current_session.id)
        
        try:
            event = self.current_session.event_bus.dispatch(NavigateToUrlEvent(url=url, new_tab=new_tab))
            await event
            await asyncio.sleep(1.5)
            
            return json.dumps({
                'success': True,
                'url': url,
                'new_tab': new_tab,
                'message': f'{"Opened new tab and navigated" if new_tab else "Navigated"} to {url}'
            })
        except Exception as e:
            return json.dumps({'error': 'Navigation failed', 'details': str(e)})
    
    async def _go_back(self) -> str:
        """Navigate back in browser history."""
        self._update_session_activity(self.current_session.id)
        
        try:
            event = self.current_session.event_bus.dispatch(GoBackEvent())
            await event
            await asyncio.sleep(1)
            
            current_url = await self.current_session.get_current_page_url()
            return json.dumps({'success': True, 'message': 'Navigated back', 'current_url': current_url})
        except Exception as e:
            return json.dumps({'error': 'Failed to go back', 'details': str(e)})
    
    async def _get_browser_state(self, include_screenshot: bool = False) -> str:
        """Get comprehensive current page state."""
        self._update_session_activity(self.current_session.id)
        
        try:
            state = await self.current_session.get_browser_state_summary()
            
            result = {
                'url': state.url,
                'title': state.title,
                'tabs': [{'url': tab.url, 'title': tab.title} for tab in state.tabs],
                'interactive_elements': []
            }
            
            for index, element in state.dom_state.selector_map.items():
                elem_info = {
                    'index': index,
                    'tag': element.tag_name,
                    'text': element.get_all_children_text(max_depth=2)[:100]
                }
                
                for attr in ['placeholder', 'href', 'type', 'value', 'name', 'id']:
                    if value := element.attributes.get(attr):
                        elem_info[attr] = value
                
                result['interactive_elements'].append(elem_info)
            
            if include_screenshot and state.screenshot:
                result['screenshot'] = state.screenshot
            
            result['element_count'] = len(result['interactive_elements'])
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({'error': 'Failed to get browser state', 'details': str(e)})
    
    async def _get_page_content(self) -> str:
        """Extract text content from current page."""
        self._update_session_activity(self.current_session.id)
        
        try:
            state = await self.current_session.get_browser_state_summary()
            text_content = state.dom_state.get_text_content()
            
            max_length = 10000
            truncated = len(text_content) > max_length
            
            return json.dumps({
                'url': state.url,
                'title': state.title,
                'text_content': text_content[:max_length],
                'truncated': truncated,
                'full_length': len(text_content)
            }, indent=2)
        except Exception as e:
            return json.dumps({'error': 'Failed to get page content', 'details': str(e)})
    
    async def _take_screenshot(self) -> str:
        """Capture screenshot of current page."""
        self._update_session_activity(self.current_session.id)
        
        try:
            state = await self.current_session.get_browser_state_summary()
            
            if not state.screenshot:
                return json.dumps({'error': 'Screenshot unavailable'})
            
            return json.dumps({
                'success': True,
                'url': state.url,
                'screenshot': state.screenshot,
                'format': 'base64_png'
            })
        except Exception as e:
            return json.dumps({'error': 'Failed to take screenshot', 'details': str(e)})
    
    async def _click(self, index: int) -> str:
        """Click an element by its index."""
        self._update_session_activity(self.current_session.id)
        
        try:
            element = await self.current_session.get_dom_element_by_index(index)
            
            if not element:
                return json.dumps({'error': 'Element not found', 'index': index})
            
            event = self.current_session.event_bus.dispatch(ClickElementEvent(node=element))
            await event
            await asyncio.sleep(0.5)
            
            return json.dumps({
                'success': True,
                'index': index,
                'element': {'tag': element.tag_name, 'text': element.get_all_children_text(max_depth=1)[:50]}
            })
        except Exception as e:
            return json.dumps({'error': 'Click failed', 'details': str(e)})
    
    async def _type_text(self, index: int, text: str) -> str:
        """Type text into an element."""
        self._update_session_activity(self.current_session.id)
        
        try:
            element = await self.current_session.get_dom_element_by_index(index)
            
            if not element:
                return json.dumps({'error': 'Element not found', 'index': index})
            
            event = self.current_session.event_bus.dispatch(TypeTextEvent(node=element, text=text))
            await event
            
            return json.dumps({'success': True, 'index': index, 'text': text})
        except Exception as e:
            return json.dumps({'error': 'Type failed', 'details': str(e)})
    
    async def _scroll(self, direction: str = 'down', amount: int = 500) -> str:
        """Scroll the page."""
        self._update_session_activity(self.current_session.id)
        
        try:
            event = self.current_session.event_bus.dispatch(ScrollEvent(direction=direction, amount=amount))  # type: ignore
            await event
            
            return json.dumps({'success': True, 'direction': direction, 'amount': amount})
        except Exception as e:
            return json.dumps({'error': 'Scroll failed', 'details': str(e)})
    
    async def _press_key(self, key: str) -> str:
        """Press a keyboard key."""
        self._update_session_activity(self.current_session.id)
        
        try:
            page = await self.current_session.get_current_page()
            
            if not page:
                return json.dumps({'error': 'No active page'})
            
            await page.keyboard.press(key)
            await asyncio.sleep(0.5)
            
            return json.dumps({'success': True, 'key': key})
        except Exception as e:
            return json.dumps({'error': 'Key press failed', 'details': str(e)})
    
    async def _list_tabs(self) -> str:
        """List all open tabs."""
        self._update_session_activity(self.current_session.id)
        
        try:
            tabs_info = await self.current_session.get_tabs()
            tabs = [
                {
                    'tab_id': tab.target_id[-4:],
                    'url': tab.url,
                    'title': tab.title or ''
                }
                for tab in tabs_info
            ]
            
            return json.dumps(tabs, indent=2)
        except Exception as e:
            return json.dumps({'error': 'Failed to list tabs', 'details': str(e)})
    
    async def _switch_tab(self, tab_id: str) -> str:
        """Switch to a different tab."""
        self._update_session_activity(self.current_session.id)
        
        try:
            target_id = await self.current_session.get_target_id_from_tab_id(tab_id)
            event = self.current_session.event_bus.dispatch(SwitchTabEvent(target_id=target_id))
            await event
            await asyncio.sleep(1)
            
            state = await self.current_session.get_browser_state_summary()
            return json.dumps({'success': True, 'tab_id': tab_id, 'url': state.url})
        except Exception as e:
            return json.dumps({'error': 'Failed to switch tab', 'details': str(e)})
    
    async def _close_tab(self, tab_id: str) -> str:
        """Close a specific tab."""
        self._update_session_activity(self.current_session.id)
        
        try:
            target_id = await self.current_session.get_target_id_from_tab_id(tab_id)
            event = self.current_session.event_bus.dispatch(CloseTabEvent(target_id=target_id))
            await event
            
            current_url = await self.current_session.get_current_page_url()
            return json.dumps({'success': True, 'closed_tab': tab_id, 'current_url': current_url})
        except Exception as e:
            return json.dumps({'error': 'Failed to close tab', 'details': str(e)})
    
    async def _execute_javascript(self, script: str) -> str:
        """Execute JavaScript on the current page."""
        self._update_session_activity(self.current_session.id)
        
        try:
            page = await self.current_session.get_current_page()
            
            if not page:
                return json.dumps({'error': 'No active page'})
            
            result = await page.evaluate(script)
            return json.dumps({'success': True, 'result': result})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    async def _wait(self, seconds: float) -> str:
        """Wait for a specified duration."""
        await asyncio.sleep(seconds)
        return json.dumps({'success': True, 'waited': seconds})
    
    def _track_session(self, session: BrowserSession):
        """Track a browser session."""
        self.active_sessions[session.id] = {
            'session': session,
            'created_at': time.time(),
            'last_activity': time.time(),
            'url': getattr(session, 'current_url', None)
        }
    
    def _update_session_activity(self, session_id: str):
        """Update session activity timestamp."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['last_activity'] = time.time()
    
    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name='browser-use-claude-agent',
                    server_version='2.1.0',
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point for the MCP server."""
    if not MCP_AVAILABLE:
        print('ERROR: MCP SDK is required. Install with: pip install mcp', file=sys.stderr)
        sys.exit(1)
    
    server = ClaudeAgentBrowserServer(session_timeout_minutes=10)
    
    try:
        await server.run()
    except KeyboardInterrupt:
        print('\nShutting down server...', file=sys.stderr)
    finally:
        if server.current_session:
            await server._close_browser()


if __name__ == '__main__':
    asyncio.run(main())
