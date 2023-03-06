import cadquery as cq
import os

# generate all models and update documentation

import models.nimble_beam

# parameters

outputdir_stl = "./src/mech/cadquery_workflow/gitbuilding/models/"
outputdir_step = "./src/mech/step/"

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
cq.exporters.export(beam, outputdir_stl + "beam.stl")
cq.exporters.export(beam, outputdir_step + "beam.step")


#show_object(beam)



