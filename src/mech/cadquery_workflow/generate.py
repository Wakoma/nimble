import cadquery as cq
import os

# generate all models and update documentation

import models.nimble_beam

# parameters

outputdir_stl = "./src/mech/cadquery_workflow/gitbuilding/models/"
outputdir_step = "./src/mech/step/"
outputdir_gitbuilding = "./src/mech/cadquery_workflow/gitbuilding/"

beam_length = 294

# set up build env

try:
  os.mkdir(outputdir_stl)
except:
  pass # ignore if already existing

try:
  os.mkdir(outputdir_step)
except:
  pass # ignore if already existing

# create the models

beam = models.nimble_beam.create(beam_length=beam_length)

# export 

partList = []

def exportPart(part, name, long_name):    
  cq.exporters.export(beam, outputdir_stl + name + ".stl")
  cq.exporters.export(beam, outputdir_step + name + ".step")
  partList.append((name, long_name))


exportPart(beam, "beam", "3D printed beam")
exportPart(beam, "baseplate", "3D printed base plate")
exportPart(beam, "topplate", "3D printed top plate")

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

#for debugging
#show_object(beam)



