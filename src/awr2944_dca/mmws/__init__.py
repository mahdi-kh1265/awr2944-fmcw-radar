"""mmWave Studio backend controller package.

Python/Jupyter is the control layer and source of truth.
mmWave Studio is the execution backend.
Python controls mmWave Studio through generated Lua/ar1.* scripts.
Python must never directly open the AWR radar RS232 port while mmWave Studio owns it.
"""
