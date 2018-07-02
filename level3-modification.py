#!/usr/bin/env python2
#
# This script modifies the IRIS model files for Level-3 ICD.
#

import os
import re
import sys


if len(sys.argv) < 2:
    print >> sys.stderr, "Specify the directory in which the modified model files to be generated."
    sys.exit(1)

output_dir = sys.argv[1]
input_dir  = os.path.dirname(os.path.abspath(__file__))

os.mkdir(output_dir)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Subsystem:
    def __init__(self, dirname, abbr, title, description):
        self.components = []
        self.dirname = dirname
        self.abbr = abbr
        self.title = title
        self.description = description

    def addComponent(self, component):
        self.components.append(component)

class Component:
    def __init__(self, name, dirpath):
        self.name = name
        self.dirpath = dirpath

subsystems = [
    Subsystem('ici', 'ICI', 'IRIS Instrument Control Interface', ''),
    Subsystem('drs', 'DRS', 'IRIS Data Reduction System', ''),
    Subsystem('csro', 'CSRO', 'IRIS CSRO', ''),
    Subsystem('imager', 'IMG', 'IRIS Imager', ''),
    Subsystem('ifs', 'IFS', 'IRIS Integral Field Spectrograph', ''),
    Subsystem('sc', 'SC', 'IRIS Science Cryostat', ''),
    Subsystem('el', 'EL', 'IRIS Electronics', '')
]

# Obtain all component names
for subsystem in subsystems:
    files = os.listdir(os.path.join(input_dir, subsystem.dirname))
    component_dirs = [f for f in files if os.path.isdir(os.path.join(subsystem.dirname, f))]

    for component_dir in component_dirs:
        component_model_path = os.path.join(input_dir, subsystem.dirname, component_dir, 'component-model.conf')
        if os.path.exists(os.path.join(input_dir, component_model_path)):
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
created_dirs = []
for subsystem in subsystems:
    for component in subsystem.components:
        model_files = ['command-model.conf',
                       'component-model.conf',
                       'publish-model.conf', 
                       'subscribe-model.conf']
        for model_file in model_files:
            input_path = os.path.join(input_dir, component.dirpath, model_file)
            if os.path.exists(input_path):
                output_subdir = os.path.join(output_dir, component.dirpath)
                if not output_subdir in created_dirs:
                    os.makedirs(output_subdir)
                    created_dirs.append(output_subdir)

                output_path = os.path.join(output_subdir, model_file)

                f_in = open(input_path, 'r')
                f_out = open(output_path, 'w')
            
                contents = ''.join(f_in.readlines())
                for pattern in patterns:
                    contents = re.sub(pattern[0], pattern[1], contents)
                f_out.write(contents)

                f_in.close()
                f_out.close()

# Generate subsystem-model.conf
for subsystem in subsystems:
    subsystem_model_path = os.path.join(output_dir, subsystem.dirname, 'subsystem-model.conf')
    f_out = open(subsystem_model_path, 'w')
    f_out.write('subsystem = IRIS-' + subsystem.abbr + '\n')
    f_out.write('title = "' + subsystem.title + '"\n')
    f_out.write('modelVersion = "1.0"\n')
    f_out.write('description = "' + subsystem.description + '"\n')
