"""LEGACY OPTIONAL TOOLING

This package supports historical mmWave Studio/Lua/RSTD workflows.
It is not used by the production direct-capture pipeline.
"""

import sys
import importlib
import warnings
from types import ModuleType

class LazySubmoduleProxy(ModuleType):
    def __init__(self, name: str, real_name: str):
        super().__init__(name)
        self._real_name = real_name
        self._real_module = None
        # We need this to make standard import machinery happy
        self.__path__ = []

    def _load(self):
        if self._real_module is None:
            warnings.warn(
                f"Importing {self.__name__} is deprecated. Use {self._real_name} instead. "
                "This legacy tooling is not used by the production capture pipeline.",
                DeprecationWarning,
                stacklevel=3
            )
            self._real_module = importlib.import_module(self._real_name)
        return self._real_module

    def __getattr__(self, item: str):
        if item in ("__path__", "__spec__", "__file__", "__loader__", "__package__"):
            return None
        return getattr(self._load(), item)

    def __dir__(self):
        return dir(self._load())


_submodules = [
    "bridge",
    "catalog",
    "config_parser",
    "executor",
    "failure_report",
    "guided_runner",
    "gui_connect",
    "install",
    "internals",
    "lua_builder",
    "matlab_bridge",
    "models",
    "post_connect",
    "rstd_worker",
    "stages",
    "win32_connect",
]

for _sub in _submodules:
    _proxy = LazySubmoduleProxy(f"awr2944_dca.mmws.{_sub}", f"awr2944_dca.legacy_mmws.{_sub}")
    sys.modules[_proxy.__name__] = _proxy


def __getattr__(name: str):
    if name in _submodules:
        # Accessing `awr2944_dca.mmws.executor` triggers this if imported simply via `import awr2944_dca.mmws`
        return sys.modules[f"awr2944_dca.mmws.{name}"]
    
    # Otherwise try to load from legacy_mmws directly for any top-level exports
    warnings.warn(
        f"Accessing {name} from awr2944_dca.mmws is deprecated. Use awr2944_dca.legacy_mmws.",
        DeprecationWarning,
        stacklevel=2
    )
    import awr2944_dca.legacy_mmws
    return getattr(awr2944_dca.legacy_mmws, name)

def __dir__():
    return _submodules
