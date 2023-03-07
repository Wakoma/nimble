import cadquery as cq
import os
import json
from exportsvg import export_svg 

# generate all models and update documentation

import models.nimble_beam
import models.nimble_end_plate

# parameters

selected_devices_ids = ['NetgateSG1100', 'UniFiUSWFlex', 'NUC10i5FNH', 'RPi4']

json_filename = "./src/mech/cadquery_workflow/devices.json"
outputdir_stl = "./src/mech/cadquery_workflow/gitbuilding/models/"
outputdir_step = "./src/mech/step/"
outputdir_svg = "./src/mech/cadquery_workflow/gitbuilding/svg/"
outputdir_gitbuilding = "./src/mech/cadquery_workflow/gitbuilding/"

beam_length = 294
single_width = 155

# set up build env

try:
  os.mkdir(outputdir_stl)
except:
  pass # ignore if already existing

try:
  os.mkdir(outputdir_step)
except:
  pass # ignore if already existing

try:
  os.mkdir(outputdir_svg)
except:
  pass # ignore if already existing

# read json, select entries

selected_devices = []
with open(json_filename) as json_file:
    data = json.load(json_file)
    selected_devices = [x for x in data if x['ID'] in selected_devices_ids]
print([x['ID'] for x in selected_devices])

# create the models

beam = models.nimble_beam.create(beam_length=beam_length)
plate = models.nimble_end_plate.create(width=single_width, height=single_width)


# export STLs and STEPs

partList = []

def exportPart(part, name, long_name):    
  stl_file = outputdir_stl + name + ".stl"
  step_file = outputdir_step + name + ".step"
  cq.exporters.export(part, stl_file)
  #cq.exporters.export(part, step_file) #not needed right now
  partList.append((name, long_name))

exportPart(beam, "beam", "3D printed beam")
exportPart(plate, "baseplate", "3D printed base plate")
exportPart(plate, "topplate", "3D printed top plate")

# export SVGs

export_svg(plate, outputdir_svg+"baseplate.svg") # just a test for now
export_svg(plate, outputdir_svg+"baseplate_beams.svg") # just a test for now
export_svg(plate, outputdir_svg+"baseplate_beams_topplate.svg") # just a test for now


# write gitbuilding files

with open(outputdir_gitbuilding+'3dprintingparts.md', 'w') as f:
    f.write("# 3D print all the needed files\n\n")
    for (part,long_name) in partList:
      f.write("* %s.stl ([preview](models/%s.stl){previewpage}, [download](models/%s.stl))\n" % (part, part, part))


with open(outputdir_gitbuilding+'3DPParts.yaml', 'w') as f:
    for (part,long_name) in partList:
      f.write("%s:\n" % (part))
      f.write("    Name: %s\n" % (long_name))
      f.write("    Specs:\n")
      f.write("        Filename: %s.stl\n" % (part))
      #f.write("        Filename: %s.stl ([download](models/%s.stl))\n" % (part, part))
      f.write("        Manufacturing: 3D Printing\n")
      f.write("        Material: PLA or PETG\n")
      #f.write("        Preview: [preview](models/beam.stl){previewpage}\n")

with open(outputdir_gitbuilding+'DeviceParts.yaml', 'w') as f:
    for device in selected_devices:
      f.write("%s:\n" % (device['ID']))
      for k in device.keys():
        f.write("    %s: %s\n" % (k, device[k]))

#for debugging
#show_object(beam)



