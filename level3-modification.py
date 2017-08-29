# This script modifies the IRIS model files for Level-3 ICD.

import os
import re


os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Subsystem:
    def __init__(self, dirname, abbr):
        self.components = []
        self.dirname = dirname
        self.abbr = abbr

    def addComponent(self, component):
        self.components.append(component)

class Component:
    def __init__(self, name, dirpath):
        self.name = name
        self.dirpath = dirpath

d_s = {
    'ici': 'ICI',
    'drs': 'DRS',
    'csro': 'CSRO',
    'imager': 'IMG',
    'ifs': 'IFS',
    'sc': 'SC',
    'el': 'EL',
    }
subsystems = [Subsystem(d, s) for d, s in d_s.iteritems()]

# Obtain all component names
for subsystem in subsystems:
    files = os.listdir(subsystem.dirname)
    component_dirs = [f for f in files if os.path.isdir(os.path.join(subsystem.dirname, f))]

    for component_dir in component_dirs:
        component_model_path = os.path.join(subsystem.dirname, component_dir, 'component-model.conf')
        if os.path.exists(component_model_path):
            f_in = open(component_model_path)
            contents = ''.join(f_in.readlines())
            m = re.match(r'subsystem\s*=\s*IRIS\s*\n\s*component\s*=\s*(\S+)\s*', contents)
            component_name = m.group(1)
            component_dir_path = os.path.join(subsystem.dirname, component_dir)
            subsystem.addComponent(Component(component_name, component_dir_path))

# Create regex patterns
patterns = []
for subsystem in subsystems:
    for component in subsystem.components:
        r = r'subsystem\s*=\s*IRIS\s*(\n\s*component\s*=\s*' + component.name + ')'
        s = 'subsystem = IRIS-' + subsystem.abbr + '\\1'
        patterns.append((r,s))

# Replace "subsystem = IRIS" in model files for Level-3 ICD.
for subsystem in subsystems:
    for component in subsystem.components:
        model_files = ['command-model.conf',
                       'component-model.conf',
                       'publish-model.conf', 
                       'subscribe-model.conf']
        for model_file in model_files:
            filepath = os.path.join(component.dirpath, model_file)
            if os.path.exists(filepath):
                temppath = os.path.join(component.dirpath, model_file + '.temp')

                f_in = open(filepath, 'r')
                f_out = open(temppath, 'w')
            
                contents = ''.join(f_in.readlines())
                for pattern in patterns:
                    contents = re.sub(pattern[0], pattern[1], contents)
                f_out.write(contents)

                f_in.close()
                f_out.close()
                os.remove(filepath)
                os.rename(temppath, filepath)
