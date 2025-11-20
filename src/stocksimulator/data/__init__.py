"""
Data loading and management module.

Provides access to diverse asset classes for portfolio construction.
"""

from .multi_asset_loader import (
    MultiAssetDataLoader,
    AssetClassRegistry,
    AssetClassInfo,
    print_asset_summary
)

__all__ = [
    'MultiAssetDataLoader',
    'AssetClassRegistry',
    'AssetClassInfo',
    'print_asset_summary',
]
