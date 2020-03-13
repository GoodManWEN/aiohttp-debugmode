import sys
import os
import sysconfig

class Helper:

    def __init__(self):
        self._fit_exts = ['.pyd','.pyc']
        self.tree = []

    def build_import_tree(self):
        self.tree = list(
            map(lambda x:x.__file__ , 
                filter(lambda x:True if hasattr(x,'__file__') else False ,
                    sys.modules.values()
                    )
                )
            )
    
    def filter_syspath(self):
        syspaths = []
        for key , syspath in sysconfig.get_paths().items():
            if key != "data":
                syspath_ = os.path.abspath(syspath).replace('\\','/') + '/'
                if os.name == 'nt':
                    syspath_ = syspath_.lower()
                syspaths.append(syspath_)


        def determin_included(path):
            if path:
                path = os.path.abspath(path).replace('\\','/')
            else:
                return True
            if os.name == 'nt':
                path = path.lower()
            for syspath in syspaths:
                if len(path) > len(syspath):
                    if path[:len(syspath)] == syspath:
                        return True
            return False

        self._obv_list = []
        for path_ in self.tree:
            if not determin_included(path_):
                if os.path.splitext(path_)[1] not in self._fit_exts:
                    self._obv_list.append(path_)

    def dependencies(self):
        return self._obv_list
        

    def optmize_tree(self , list_):
        for path_ in list_:
            # security check
            if not os.path.exists(path_):
                if os.path.splitext(path_)[1] == '':
                    os.mkdir(path_)
                else:
                    raise FileNotFoundError(f"Observe list file : '{path_}' not found. Initialize failed.")