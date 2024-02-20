# my_module/bootstrap.py

import shutil
import os

def main():
    # Get the path to the installed location of the module
    module_path = os.path.dirname(__file__)
    
    # Path to the app.py script in the installed location
    app_script_path = os.path.join(module_path, 'tlc.py')
    settings_script_path = os.path.join(module_path, 'settings.py')
    makefile_script_path = os.path.join(module_path, 'makefile')
    eula_script_path = os.path.join(module_path, 'eula_preproc.sh')
    
    # Path to the current working directory
    cwd = os.getcwd()
    
    # Copy the app.py script from the installed location to the current working directory
    shutil.copy(app_script_path, cwd)
    shutil.copy(settings_script_path, cwd)
    shutil.copy(makefile_script_path, cwd)
    shutil.copy(eula_script_path, cwd)

    
if __name__ == '__main__':
    main()

