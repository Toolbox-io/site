import asyncio
import logging
import os
import threading
from pathlib import Path
from typing import Set, Callable
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from fastapi import WebSocket, Response, Request, WebSocketDisconnect, APIRouter
from starlette.websockets import WebSocketState
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

logger = logging.getLogger(__name__)

class LiveReloadManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.observer = None
        self.watch_paths = []
        self._main_loop = None
        self._pending_reloads = []
        self._lock = threading.Lock()
        
    def set_main_loop(self, loop):
        """Set the main asyncio event loop"""
        self._main_loop = loop
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        
    def queue_reload(self, file_path: str):
        """Queue a reload event from the file watcher thread"""
        with self._lock:
            self._pending_reloads.append(file_path)
        
        # Schedule processing in the main event loop
        if self._main_loop and self._main_loop.is_running():
            self._main_loop.call_soon_threadsafe(self._schedule_process_pending)
        
    def _schedule_process_pending(self):
        """Schedule the async processing function"""
        if self._main_loop and self._main_loop.is_running():
            asyncio.create_task(self._process_pending_reloads())
        
    async def _process_pending_reloads(self):
        """Process pending reload events in the main event loop"""
        with self._lock:
            pending = self._pending_reloads.copy()
            self._pending_reloads.clear()
        
        for file_path in pending:
            await self.broadcast_reload(file_path)
        
    async def broadcast_reload(self, file_path: str):
        """Broadcast reload message to all connected clients"""
        if not self.active_connections:
            return
            
        message = {
            "type": "reload",
            "file": file_path,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_json(message)
                else:
                    disconnected.add(connection)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)
                
        # Clean up disconnected websockets
        for connection in disconnected:
            self.disconnect(connection)
            
        if self.active_connections:
            logger.info(f"Reloaded {file_path} for {len(self.active_connections)} client(s)")

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, manager: LiveReloadManager, watch_paths: list[Path]):
        self.manager = manager
        self.watch_paths = watch_paths
        self.ignored_extensions = {'.pyc', '.pyo', '.pyd', '.git', '.DS_Store', '.swp', '.tmp'}
        self.ignored_dirs = {'.git', '__pycache__', 'node_modules', '.vscode', '.idea'}
        
    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored"""
        # Check file extension
        if path.suffix in self.ignored_extensions:
            return True
            
        # Check if any parent directory should be ignored
        for parent in path.parents:
            if parent.name in self.ignored_dirs:
                return True
                
        return False
        
    def _is_watched_path(self, path: Path) -> bool:
        """Check if the file is in one of our watched paths"""
        for watch_path in self.watch_paths:
            try:
                path.relative_to(watch_path)
                return True
            except ValueError:
                continue
        return False
        
    def _handle_file_change(self, event_path: str):
        """Handle file change event"""
        path = Path(event_path)
        
        if self._should_ignore(path):
            return
            
        if not self._is_watched_path(path):
            return
            
        # Convert to relative path for client
        try:
            for watch_path in self.watch_paths:
                try:
                    relative_path = path.relative_to(watch_path)
                    logger.info(f"File changed: {relative_path}")
                    
                    # Queue the reload event for processing in the main event loop
                    self.manager.queue_reload(str(relative_path))
                    break
                except ValueError:
                    continue
        except Exception as e:
            logger.error(f"Error handling file change: {e}")
    
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path)
            
    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path)
            
    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path)

class HTMLInjectorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, live_reload_script_path: str = "/js/live-reload.js"):
        super().__init__(app)
        self.live_reload_script_path = live_reload_script_path
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        try:
            # Only inject in development mode
            if (
                os.getenv("DEBUG", "false").lower() != "true" or 
                "text/html" not in response.headers.get("content-type", "") or
                isinstance(response, StreamingResponse)
            ): return response
                
            # Get the response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
                
            # Convert to string for processing
            try:
                html_content = body.decode("utf-8")
            except UnicodeDecodeError as e:
                logger.warning(f"Failed to decode HTML content: {e}")
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
            
            # Check if live reload script is already present
            if self.live_reload_script_path in html_content:
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
            
            # Inject the live reload script before closing </head> tag
            script_tag = f'<script type="module" src="{self.live_reload_script_path}"></script>'
            
            # Find the closing </head> tag
            head_end_index = html_content.find("</head>")
            if head_end_index != -1:
                # Insert script before </head>
                modified_html = (
                    html_content[:head_end_index] + 
                    script_tag + 
                    html_content[head_end_index:]
                )
                
                # Create new response with modified content
                new_response = Response(
                    content=modified_html.encode("utf-8"),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
                
                # Remove content-length header to let FastAPI recalculate it
                if "content-length" in new_response.headers:
                    del new_response.headers["content-length"]
                    
                return new_response
            
            # If no </head> tag found, return original response
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
        except Exception as e:
            logger.error(f"Error in HTML injection: {e}")
            # Return the original response if there's an error
            return response

# Global manager instance
live_reload_manager = LiveReloadManager()

# Create router for live reload routes
router = APIRouter()

@router.websocket("/ws/live-reload")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live reload functionality"""
    await live_reload_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        live_reload_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        live_reload_manager.disconnect(websocket)

def start_file_watcher(watch_paths: list[Path]):
    """Start watching files for changes"""
    if live_reload_manager.observer is not None:
        return  # Already started
        
    event_handler = FileChangeHandler(live_reload_manager, watch_paths)
    observer = Observer()
    
    for path in watch_paths:
        if path.exists():
            observer.schedule(event_handler, str(path), recursive=True)
        else:
            logger.warning(f"Watch path does not exist: {path}")
    
    observer.start()
    live_reload_manager.observer = observer
    live_reload_manager.watch_paths = watch_paths
    
    # Set the main event loop for thread-safe communication
    try:
        live_reload_manager.set_main_loop(asyncio.get_event_loop())
    except RuntimeError:
        # No event loop in current thread, will be set later
        pass

def stop_file_watcher():
    """Stop the file watcher"""
    if live_reload_manager.observer:
        live_reload_manager.observer.stop()
        live_reload_manager.observer.join()
        live_reload_manager.observer = None
        logger.info("Live reload: Stopped") 