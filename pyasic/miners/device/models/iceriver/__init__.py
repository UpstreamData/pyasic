from .ALX import *
from .KSX import *

# Define what gets exported with wildcard to exclude KS3 and KS5
# which conflict with antminer models
__all__ = [
    # From ALX
    "AL3",
    # From KSX
    "KS0",
    "KS1",
    "KS2",
    "KS3L",
    "KS3M",
    "KS5L",
    "KS5M",
    # Note: KS3 and KS5 are excluded to avoid conflicts with antminer
]
