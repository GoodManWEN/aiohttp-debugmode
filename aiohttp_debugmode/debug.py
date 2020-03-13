import logging
import sys
import os
import asyncio
import aiohttp_debugtoolbar
from io import StringIO
from aiohttp import web
from .observe_stdout import flusher
from .manager import ObserverManager
from .hlp import Helper

class Debugmode:

    _obv_list = ['templates' , 'static']
    _obv_mgr = None
    _startup = None
    logger = None

    def run_app(app , *args , **kwargs):
        # logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        mystdout = StringIO()
        streamh = logging.StreamHandler(stream=sys.stdout)
        format_ = logging.Formatter()
        streamh.setFormatter(format_)
        logger.addHandler(streamh)
        Debugmode.logger = logger

        # env check part.
        subprocflag = False
        current_env = os.environ
        if 'AIOHTTPDEBUG_SUBPROC' in current_env:
            if current_env['AIOHTTPDEBUG_SUBPROC'] == "true":
                subprocflag = True

        if subprocflag:
            # in subprocess
            loop = asyncio.get_event_loop()
            loop.create_task(flusher(logger))
            aiohttp_debugtoolbar.setup(app)
            if 'access_log' in kwargs:
                del kwargs['access_log']
            if Debugmode._startup:
                Debugmode._startup()
                print(f"======== Startup process finished{' '*7}======== ")
            loop.run_until_complete(web._run_app(
                                    app ,
                                    access_log = logger,
                                    *args ,
                                    **kwargs
                                    ))
        else:
            # in mainprocess
            _help = Helper()
            _help.build_import_tree()
            _help.filter_syspath()
            Debugmode._obv_list.extend(_help.dependencies())
            Debugmode._obv_list = list(
                                    map(
                                        lambda x:os.path.abspath(x),
                                        Debugmode._obv_list
                                    )
                                )
            _help.optmize_tree(Debugmode._obv_list)

            loop = asyncio.get_event_loop()
            watchmanager = ObserverManager(loop , Debugmode)
            Debugmode._obv_mgr = watchmanager
            watchmanager.new_observe()
            watchmanager.start()

    def print(*args , **kwargs):
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        print(*args , **kwargs)
        sys.stdout = old_stdout
        Debugmode.logger.info(mystdout.getvalue())

    def append_observe(_lst = []):
        if not isinstance(_lst , list):
            raise TypeError('Observe list should be a list made up of strings.')
        
        Debugmode._obv_list.extend(_lst)

    def on_startup(func):
        if not callable(func):
            raise TypeError("Startup must be a callable")
        Debugmode._startup = func

