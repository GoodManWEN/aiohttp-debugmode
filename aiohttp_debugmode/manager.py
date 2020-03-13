import sys
import os
from watchdog.observers import Observer
from io import StringIO 
from .pseudopty import Ppty
from .observe_stdout import spying
from .handler import AIOEventHandler

class ObserverManager:

    def __init__(self , loop ,dbgclass):
        self._loop = loop
        self._dbgclass = dbgclass
    
    def new_observe(self):
        self._observer = Observer()
        event_handler = AIOEventHandler(self._loop , self._dbgclass)
        self._observer.schedule(event_handler, '.', recursive=True)

    def subprocess(self):
        args = [sys.executable] + sys.argv
        new_environ = os.environ.copy()
        new_environ['AIOHTTPDEBUG_SUBPROC'] = 'true'
        proc = Ppty(args , env = new_environ).spawn()
        proc.set_event_loop(self._loop)
        return proc

    def start(self):
        self._observer.start()
        self._subp = self.subprocess()
        self._running_subp_pty = self._loop.create_task(spying(self._subp))
        try:
            print(f"======== MainEventLoop Started{' '*10}========")
            print(f"======== Waiting for service ready{' '*6}========")
            self._loop.run_forever()
        except KeyboardInterrupt:
            print('KeyboardInterrupt detected.')
            print('Gracegul shutdown.')
        finally:
            outerspace = StringIO()
            sys.stdout = sys.stderr = outerspace
            self.stop()
            self._loop.close()

    def restart(self):
        self.stop()
        self.new_observe()
        self._subp = self.subprocess()
        self._running_subp_pty = self._loop.create_task(spying(self._subp))
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()
        self._subp.kill()
        self._running_subp_pty.cancel()
        del self._observer
        del self._subp
        del self._running_subp_pty