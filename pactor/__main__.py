import importlib
import sys
import pathlib

# Load .git version before the builtin version
if pathlib.Path('./pactor/__init__.py').absolute().exists():
	spec = importlib.util.spec_from_file_location("pactor", "./pactor/__init__.py")
	pactor = importlib.util.module_from_spec(spec)
	sys.modules["pactor"] = pactor
	spec.loader.exec_module(sys.modules["pactor"])
else:
	import pactor

if __name__ == '__main__':
	pactor.run_as_a_module()
