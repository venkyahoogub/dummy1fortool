from source.common_utilities.log_config import logger

# Global registry of all tabs
registered_tabs = []

def register_tab(tab):
    """Register a tab so it can be refreshed later."""
    if tab not in registered_tabs:
        registered_tabs.append(tab)