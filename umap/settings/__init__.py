import os
import sys
import types
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.utils.termcolors import colorize

from .base import *  # NOQA, default values

# Allow to override setting from any file, may be out of the PYTHONPATH,
# to make it easier for non python people.
path = os.environ.get("UMAP_SETTINGS")
if not path:
    # Retrocompat
    path = os.path.join("/etc", "umap", "umap.conf")
    if not os.path.exists(path):
        # Retrocompat
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "local.py")
        if not os.path.exists(path):
            print(colorize("No valid UMAP_SETTINGS found", fg="yellow"))
            path = None

if path:
    d = types.ModuleType("config")
    d.__file__ = path
    try:
        with open(path) as config_file:
            exec(compile(config_file.read(), path, "exec"), d.__dict__)
    except IOError as e:
        msg = "Unable to import {} from UMAP_SETTINGS".format(path)
        print(colorize(msg, fg="red"))
        sys.exit(e)
    else:
        print("Loaded local config from", path)
        for key in dir(d):
            if key.isupper():
                value = getattr(d, key)
                if key == "UMAP_CUSTOM_TEMPLATES":
                    if "DIRS" in globals()["TEMPLATES"][0]:
                        globals()["TEMPLATES"][0]["DIRS"].insert(0, value)
                    else:
                        globals()["TEMPLATES"][0]["DIRS"] = [value]
                elif key == "UMAP_CUSTOM_STATICS":
                    globals()["STATICFILES_DIRS"].insert(0, value)
                elif key == "UMAP_FEEDBACK_LINK":
                    globals()["UMAP_HELP_URL"] = value
                else:
                    if key == "UMAP_PICTOGRAMS_COLLECTIONS" and value:
                        for name, options in value.items():
                            # relative path will be looked relatively to the STATIC_ROOT
                            path = Path(options["path"])
                            if not path.is_absolute():
                                continue
                            if not path.exists():
                                msg = (
                                    f"UMAP_PICTOGRAMS_COLLECTIONS defines path {path} but it does "
                                    "not exist"
                                )
                                raise ImproperlyConfigured(msg)
                            if not (path / "pictograms").exists():
                                msg = (
                                    f"UMAP_PICTOGRAMS_COLLECTIONS defines path {path} but it does "
                                    "not have a 'pictograms' root folder"
                                )
                                raise ImproperlyConfigured(msg)
                            globals()["STATICFILES_DIRS"].append(path)
                    globals()[key] = value
