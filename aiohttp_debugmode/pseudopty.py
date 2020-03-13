from chardet import detect as chardetect
from subprocess import PIPE , STDOUT , Popen
from locale import getdefaultlocale
from asyncio import get_running_loop

_ENCODING = getdefaultlocale()[1]

class WarpedPopen(Popen):

    def __init__(self , *args , **kwargs):
        if 'pool' in kwargs:
            self._async_pool = kwargs.pop('pool')
        else:
            self._async_pool = None
        try:
            self._running_loop = get_running_loop()
        except:
            self._running_loop = None
        super().__init__(*args , **kwargs)

    def _warp_stdout_read(self ,length):
        try:
            return self.stdout.read(length)
        except ValueError:  
            return b''

    def _readline_decoder(self , bytes_):
        global _ENCODING
        try:
            return bytes_.decode(_ENCODING).replace('\r','\n')
        except:
            _encoding = chardetect(bytes_)['encoding']
            _ENCODING = _encoding
            return bytes_.decode(_encoding).replace('\r','\n')

    def readline(self):
        _buffer = b''
        while True:
            if self.poll() != None:
                # clean buffer
                while True:
                    chunk = self._warp_stdout_read(1)
                    if chunk != b'\n':
                        _buffer += chunk
                    if chunk == b'':
                        if _buffer == b'':
                            return None
                        return self._readline_decoder(_buffer)
            chunk = self._warp_stdout_read(1)
            if chunk != b'\n':
                _buffer += chunk
                if chunk == b'\r':
                    return self._readline_decoder(_buffer)

    def set_async_pool(self , pool):
        self._async_pool = pool

    def set_event_loop(self, loop):
        self._running_loop = loop

    async def async_readline(self):
        return await self._running_loop.run_in_executor(self._async_pool, self.readline)

    async def async_communicate(self):
        return await self._running_loop.run_in_executor(self._async_pool, self.communicate)      


class Ppty:

    '''
    A pty wrapper which has absolutely no pty function.
    '''

    def __init__(self , cmd , env ,pool = None):
        self.cmd = cmd
        self._pool = pool
        self._env = env

    def spawn(self):
        popen = WarpedPopen(self.cmd , stdout = PIPE , stderr=STDOUT , shell=False , env = self._env ,  pool = self._pool)
        return popen

    
