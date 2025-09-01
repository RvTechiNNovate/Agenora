"""
Plugin manager module for dynamically loading agent providers.
"""
import importlib
import inspect
import os
import pkgutil
from typing import Dict, Type, List

from backend.agent_manager.base import BaseAgentManager
from backend.core.logging import get_logger

logger = get_logger(__name__)

class PluginManager:
    """
    Plugin manager for dynamically discovering and loading agent providers.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PluginManager, cls).__new__(cls)
            cls._instance._providers = {}
        return cls._instance
    
    def __init__(self):
        self._providers = self._providers or {}
    
    @property
    def providers(self) -> Dict[str, BaseAgentManager]:
        """Get the registered providers."""
        return self._providers
    
    def discover_providers(self, package_path: str = "backend.agent_manager.providers") -> None:
        """
        Discover and register agent providers from the given package path.
        
        Args:
            package_path: The dot-notation path to search for providers
        """
        package = importlib.import_module(package_path)
        
        # Find all subpackages
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            if is_pkg:
                # Import the subpackage
                subpackage = importlib.import_module(name)
                
                # Look for agent manager classes in this subpackage
                for module_path in [f"{name}.{m}" for m in self._find_python_modules(subpackage.__path__[0])]:
                    try:
                        module = importlib.import_module(module_path)
                        self._register_managers_from_module(module)
                    except ImportError as e:
                        logger.error(f"Error importing module {module_path}: {str(e)}")
    
    def _find_python_modules(self, package_dir: str) -> List[str]:
        """Find all Python modules in a directory."""
        modules = []
        for file in os.listdir(package_dir):
            if file.endswith(".py") and not file.startswith("__"):
                modules.append(file[:-3])
        return modules
    
    def _register_managers_from_module(self, module) -> None:
        """Register all BaseAgentManager subclasses from a module."""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseAgentManager) and 
                obj != BaseAgentManager and 
                hasattr(obj, 'framework_name')):
                
                try:
                    # Create an instance of the manager
                    instance = obj()
                    framework_name = instance.framework_name
                    
                    # Register the manager
                    self._providers[framework_name] = instance
                    logger.info(f"Automatically registered {framework_name} agent provider")
                except Exception as e:
                    logger.error(f"Error registering {name} manager: {str(e)}")
    
    def register_provider(self, framework_name: str, provider: BaseAgentManager) -> None:
        """Manually register a provider."""
        self._providers[framework_name] = provider
        logger.info(f"Manually registered {framework_name} agent provider")

# Create singleton instance
plugin_manager = PluginManager()
