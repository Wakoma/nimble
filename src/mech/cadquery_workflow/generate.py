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

def exportPart(part, name):    
  cq.exporters.export(beam, outputdir_stl + name + ".stl")
  cq.exporters.export(beam, outputdir_step + name + ".step")
  partList.append(name)


exportPart(beam, "beam")
exportPart(beam, "test")

# write gitbuilding files

with open(outputdir_gitbuilding+'3dprintingparts.md', 'w') as f:
    f.write("# 3D print all the needed files\n\n")
    for part in partList:
      f.write("* %s.stl ([preview](models/%s.stl){previewpage}, [download](models/%s.stl))\n" % (part, part, part))

#for debugging
#show_object(beam)



