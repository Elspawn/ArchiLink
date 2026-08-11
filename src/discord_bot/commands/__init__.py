import importlib
import pkgutil

async def setup(bot):
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        if module_name.startswith("_"):
            continue

        module = importlib.import_module(f"{__name__}.{module_name}")

        if hasattr(module, "setup"):
            await module.setup(bot)