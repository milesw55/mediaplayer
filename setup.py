from cx_Freeze import setup, Executable
import sys, os
import subprocess



with open("version_info.txt", "w") as f:
  f.write(str(sys.version_info))

includefiles = []
rootdir = os.path.dirname(__file__)
if rootdir == "":
  rootdir = os.getcwd()
for root, subFolders, files in os.walk(rootdir):
  if not (root.endswith(os.path.sep + "__pycache__") or root.endswith(os.path.sep + "dist") or root.endswith(os.path.sep + "logs") or root.endswith(os.path.sep + "results")\
    or root.endswith(os.path.sep + "tst_treefrogrpc")):
    for file in files:
      path = root + os.path.sep + file
      if ((os.path.sep+".git") not in path) and ((rootdir + os.path.sep + "build") not in path) and not file.endswith(".pyw") and path != (rootdir + os.path.sep + "setup.py")\
        and path != (rootdir + os.path.sep + "_rununittests.py"):
        includefiles.append(path[(len(rootdir)+len(os.path.sep)):])

includes = []
for root, subFolders, files in os.walk(rootdir):
  if not (root.endswith(os.path.sep + "__pycache__") or root.endswith(os.path.sep + "dist") or root.endswith(os.path.sep + "logs") or root.endswith(os.path.sep + "results")\
    or root.endswith(os.path.sep + "tst_treefrogrpc")):
    for file in files:
      path = root + os.path.sep + file
      if ((os.path.sep+".git") not in path) and ((rootdir + os.path.sep + "build") not in path) and file.endswith(".py") and path != (rootdir + os.path.sep + "setup.py"):
        includes.append(path[(len(rootdir)+len(os.path.sep)):-3])

######################################################
#      Edit Major Version and Description here       #
######################################################
vers = "0.0."
desc = "This is the TOBIAS test automation framework."
######################################################
commits = 0
try:
  commits = int(subprocess.check_output("git rev-list HEAD --count", shell=True))
except e:
  print("no git repo found")
vers = "{}{}".format(vers, commits)

shortcut_table = [
  ( "DesktopShortcut",                                    # Shortcut
    "DesktopFolder",                                      # Directory_
    "testexecutive" + " v{}".format(vers),                # Name
    "TARGETDIR",                                          # Component_
    "[TARGETDIR]testexecutive.exe",                       # Target
    None,                                                 # Arguments
    None,                                                 # Description
    None,                                                 # Hotkey
    None,                                                 # Icon
    None,                                                 # IconIndex
    None,                                                 # ShowCmd
    "TARGETDIR",                                          # WkDir
  )
]


# Now create the table dictionary
msi_data = {"Shortcut": shortcut_table}

# Change some default MSI options and specify the use of the above defined tables
bdist_msi_options = {"data": msi_data}

options = {
  
  "build_exe": {
    "compressed": False,
    "include_files": includefiles,
    "includes": includes,
    "path": sys.path,
    "include_msvcr": True,
  },
  "bdist_msi": bdist_msi_options,
}

base = None
if sys.platform == "win32":
  base = "Win32GUI"


setup(
  name = "tobias",
  version = vers,
  description = desc,
  author = "JDS Uniphase Corp.",
  executables = [
    Executable("testexecutive.pyw", base=base, shortcutDir="DesktopFolder", shortcutName="testexecutive" + " v{}".format(vers), icon="setup/images/jdsu.ico", compress=False),
    Executable("testrunner.pyw", base=base, shortcutDir="DesktopFolder", shortcutName="testrunner" + " v{}".format(vers), icon="setup/images/jdsu.ico", compress=False),
  ],
  options = options,
)
