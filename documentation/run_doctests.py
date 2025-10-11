if __name__ != "__main__":
    raise ImportError("Standalone script cannot be imported!")

import asyncio
import doctest
import importlib
import traceback
import warnings

import pdoc

import pykc

runner = doctest.DocTestRunner()
finder = doctest.DocTestFinder()


class TestNamespace: ...


doctest_globs = {
    "asyncio": asyncio,
    "pykc": pykc,
}


def _run_module_doctests(module: pdoc.doc.Module):
    for i in finder.find(module, module.fullname, extraglobs=doctest_globs):
        runner.run(i)
    for i in module.flattened_own_members:
        # Run doctests on documented variables and public api members imported
        # from package-private submodules.
        ns = TestNamespace()
        mod = importlib.import_module(".".join(i.fullname.split(".")[:-1]))
        ns.__doc__ = i.docstring
        for j in finder.find(ns, i.fullname, module=mod, extraglobs=doctest_globs):
            runner.run(j)


# Mostly copied from pdoc.pdoc() implementation:
all_modules: list[pdoc.doc.Module] = []
for module_name in pdoc.extract.walk_specs(["pykc"]):
    try:
        all_modules.append(pdoc.doc.Module.from_name(module_name))
    except RuntimeError:
        warnings.warn(f"Error importing {module_name}:\n{traceback.format_exc()}")

if not all_modules:
    raise RuntimeError("Unable to import any modules.")


# Collect and run all docstring examples as doctests.
for i in all_modules:
    _run_module_doctests(i)

# Print the summarized doctest results
runner.summarize()
