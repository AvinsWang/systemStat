"""
The gpustat_local module.
"""

__version__ = '1.1.0.dev0'

from .core import GPUStat, GPUStatCollection
from .core import new_query
from .cli import print_gpustat, main, get_gpu_info


__all__ = (
    '__version__',
    'GPUStat', 'GPUStatCollection',
    'new_query',
    'print_gpustat', 'main',
    'get_gpu_info',
)
