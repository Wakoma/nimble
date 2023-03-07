#!/usr/sbin/env python
import sys
import FreeCAD
from FreeCAD import Mesh

try:
  doc = FreeCAD.openDocument(sys.argv[1])
  body = doc.getObject('Body') # grab first Object, this should be the base
  Mesh.export([body], sys.argv[2])
except Exception as e:
  print(sys.argv[1])
  print(e)
