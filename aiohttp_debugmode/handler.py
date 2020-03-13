from watchdog.events import LoggingEventHandler

class AIOEventHandler(LoggingEventHandler):

    def __init__(self , loop , debugmode):
        self._lock = None
        self._loop = loop
        self._debugmodeclass = debugmode

    def dispatch(self, event):

        def anyevent():
            self._debugmodeclass._obv_mgr.restart()

        print(f"({event.__class__.__name__} , src_path = {event.src_path})")
        self._lock = event 
        self._loop.call_soon_threadsafe(anyevent)