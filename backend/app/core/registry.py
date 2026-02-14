import importlib
import logging
import pkgutil
from typing import Iterable

from fastapi import APIRouter, FastAPI

logger = logging.getLogger(__name__)

ADDONS_PACKAGE = "app.addons"


def _iter_addon_names() -> Iterable[str]:
    try:
        package = importlib.import_module(ADDONS_PACKAGE)
    except ModuleNotFoundError:
        logger.warning("Addons package '%s' not found; skipping router discovery", ADDONS_PACKAGE)
        return []

    package_paths = getattr(package, "__path__", None)
    if not package_paths:
        return []

    for module_info in pkgutil.iter_modules(package_paths):
        if module_info.ispkg:
            yield module_info.name


def register_addon_routers(app: FastAPI) -> None:
    """
    Auto-discover addon routers under `app.addons.*.routes`.

    For each addon package:
      - import `<addon>.routes`
      - if it exposes `router` (APIRouter), include it under `/api/<addon_name>`.
      - otherwise skip silently.
    """
    for addon_name in _iter_addon_names():
        module_path = f"{ADDONS_PACKAGE}.{addon_name}.routes"

        try:
            routes_module = importlib.import_module(module_path)
        except ModuleNotFoundError:
            logger.debug("Routes module '%s' not found; skipping", module_path)
            continue
        except Exception as exc:
            logger.exception("Error importing routes module '%s': %s", module_path, exc)
            continue

        router = getattr(routes_module, "router", None)
        if not isinstance(router, APIRouter):
            logger.debug("No valid 'router' found in '%s'; skipping", module_path)
            continue

        prefix = f"/api/{addon_name}"
        app.include_router(router, prefix=prefix)
        logger.info("Registered router for addon '%s' at prefix '%s'", addon_name, prefix)