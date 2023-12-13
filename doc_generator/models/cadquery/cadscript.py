import re
from typing import overload, Any, Optional, Union, Tuple
from itertools import product
import cadquery as cq
from typing import Optional, Literal
import ezdxf
from sys import modules

# this is a pointer to the module object instance itself.
this = modules[__name__]
this.debugtxt = ""


def getCenterFlags(center):
    if isinstance(center, str):
        center = center.upper()
        if center=="" or not re.match(r'^X?Y?Z?$', center):
            raise ValueError("invalid center string")
        return ('X' in center , 'Y' in center, 'Z' in center)
    else:
        center = (center==True)
        return (center,center,center)

def getDimensions(dimensions, center):
    def handleSize(arg):
        size, doCenter = arg
        dim1,dim2 = (0,0)
        if isinstance(size, tuple):
            (dim1,dim2) = size
        else:
            dim2 = size
            if doCenter: 
                half = (dim2-dim1)/2
                dim1 = -half
                dim2 = half
        return (dim1, dim2)
    return tuple(map(handleSize, zip(dimensions, getCenterFlags(center))))


def makeBox(sizex: Union[float, Tuple[float,float]], sizey: Union[float, Tuple[float,float]], sizez: Union[float, Tuple[float,float]], center: any=True) -> Any:
    dimx,dimy,dimz = getDimensions([sizex, sizey, sizez], center)
    return makeBoxMinMax(dimx[0],dimx[1],dimy[0],dimy[1],dimz[0],dimz[1])

def makeBoxMinMax(x1: float, x2: float, y1: float, y2: float, z1: float, z2: float) -> Any:
    solid = cq.Solid.makeBox(x2-x1, y2-y1, z2-z1).move(cq.Location(cq.Vector(x1,y1,z1)))
    wp = cq.Workplane(obj = solid)
    return CadObject(wp)


def makeExtrude(sketch, amount, workplane=None):
    if workplane is None:
        wp = cq.Workplane()
    elif isinstance(workplane, str):
        wp = cq.Workplane(workplane)
    else:
        wp = workplane
    onj = wp.placeSketch(sketch.cq()).extrude(amount, False)
    return CadObject(onj)

def makeText(
    text: str,
    size: float,
    height: float,
    font: str = "Arial",
):
    c = cq.Compound.makeText(text, size, height, font=font)
    wp = cq.Workplane(obj = c)
    return CadObject(wp)

def makeWorkplane(planeStr, offset=None):
    wp = cq.Workplane(planeStr)
    if not offset is None:
        wp = wp.workplane(offset=offset)
    return wp


def makeSketch():
    sketch = cq.Sketch()
    return SketchObject(sketch)

def importStep(path):
    wp = cq.importers.importStep(path)
    return CadObject(wp)

def PatternRect(sizex, sizey, center=True):
    dimx,dimy = getDimensions([sizex, sizey], center)
    return [(dimx[0],dimy[0]),(dimx[0],dimy[1]),(dimx[1],dimy[1]),(dimx[1],dimy[0])]

def PatternRectArray(xs, ys, nx, ny):
    locs = []
    offsetx = (nx - 1) * xs * 0.5
    offsety = (ny - 1) * ys * 0.5
    for i, j in product(range(nx), range(ny)):
        locs.append((i * xs - offsetx, j * ys - offsety))
    return locs

def export_svg(part, filename, width=300, height=300, strokeWidth=0.6, projectionDir=(1, 1, 1)):
  cq.exporters.export(part,
                      filename,
                      opt={
                          "width": width,
                          "height": height,
                          "marginLeft": 5,
                          "marginTop": 5,
                          "showAxes": False,
                          "projectionDir": projectionDir,
                          "strokeWidth": strokeWidth,
                          "strokeColor": (0, 0, 0),
                          "hiddenColor": (0, 0, 255),
                          "showHidden": False,
                      },)



def export_sketchDXF(
    s: cq.Sketch,
    fname: str,
    approx: Optional[Literal["spline", "arc"]] = None,
    tolerance: float = 1e-3,
):
    """
    Export Sketch content to DXF. Works with 2D sections.

    :param s: Sketch to be exported.
    :param fname: Output filename.
    :param approx: Approximation strategy. None means no approximation is applied.
    "spline" results in all splines being approximated as cubic splines. "arc" results
    in all curves being approximated as arcs and straight segments.
    :param tolerance: Approximation tolerance.

    """
    w = cq.Workplane().placeSketch(s)
    plane = w.plane
    
    dxf = ezdxf.new()
    msp = dxf.modelspace()

    for f in s.faces():
      
      shape = f.transformShape(plane.fG)

      if approx == "spline":
          edges = [
              e.toSplines() if e.geomType() == "BSPLINE" else e for e in shape.Edges()
          ]

      elif approx == "arc":
          edges = []

          # this is needed to handle free wires
          for el in shape.Wires():
              edges.extend(cq.Face.makeFromWires(el).toArcs(tolerance).Edges())

      else:
          edges = shape.Edges()

      for e in edges:

          conv = cq.exporters.dxf.DXF_CONVERTERS.get(e.geomType(), cq.exporters.dxf._dxf_spline)
          conv(e, msp, plane)

    dxf.saveas(fname)

class SketchObject:
    
    def __init__(self):
        self.sketch = None
        self.finalizedSketch = None

    def __init__(self, sketch):
        self.sketch = sketch
        self.finalizedSketch = None

    def cq(self):
        return self.sketch if self.sketch else self.finalizedSketch
    
    def copy(self):
        return SketchObject(self.sketch.copy())

    def finalize(self):
        self.finalizedSketch = self.sketch
        return self

    def performAction(self, action, positions):
        if positions:
            self.sketch = action(self.sketch.push(positions))
        else:
            self.sketch = action(self.sketch)
        self.sketch.reset()    
        return self

    def rectHelper(self, sketch, sizex, sizey, center: Any, mode="a"):
        dim1,dim2 = getDimensions([sizex, sizey], center)
        x1,x2 = dim1
        y1,y2 = dim2
        
        this.debugtxt = f"rect {x1},{x2},{y1},{y2}"
        #return sketch.polygon([cq.Vector(0,0),cq.Vector(1,2),cq.Vector(2,2),cq.Vector(2,1),cq.Vector(0,0)], mode=mode)
        return sketch.polygon([cq.Vector(x1,y1),cq.Vector(x1,y2),cq.Vector(x2,y2),cq.Vector(x2,y1),cq.Vector(x1,y1)], mode=mode)

    def addRect(self, sizex: Union[float, Tuple[float,float]], sizey: Union[float, Tuple[float,float]], center:Any=True, positions:Any=None):
        action = lambda x: self.rectHelper(x,sizex,sizey,center)
        return self.performAction(action, positions)

    def cutRect(self, sizex: Union[float, Tuple[float,float]], sizey: Union[float, Tuple[float,float]], center:Any=True, positions:Any=None):
        action = lambda x: self.rectHelper(x,sizex,sizey,center, mode="s")
        return self.performAction(action, positions)

    def addCircle(self, r, positions=None):
        action = lambda x: x.circle(r)
        return self.performAction(action, positions)

    def cutCircle(self, r, positions=None):
        action = lambda x: x.circle(r, mode="s")
        return self.performAction(action, positions)

    def addPolygon(self, pointList, positions=None):
        action = lambda x: x.polygon(pointList)
        return self.performAction(action, positions)

    def cutPolygon(self, pointList, positions=None):
        action = lambda x: x.polygon(pointList, mode="s")
        return self.performAction(action, positions)

    # add slot, which is rounded on the left right side. w is with without rounded part
    def addSlot(self, w, h, angle=0, positions=None):
        action = lambda x: x.slot(w, h, angle=angle)
        return self.performAction(action, positions)

    # cut slot, which is rounded on the left right side. w is with without rounded part
    def cutSlot(self, w, h, angle=0, positions=None):
        action = lambda x: x.slot(w, h, angle=angle, mode="s")
        return self.performAction(action, positions)

    def addImportDxf(self, dxfFilename, positions=None):
        action = lambda x: x.importDXF(dxfFilename)
        return self.performAction(action, positions)
        
    def cutImportDxf(self, dxfFilename, positions=None):
        action = lambda x: x.importDXF(dxfFilename, mode="s")
        return self.performAction(action, positions)    
        
    def fillet(self, edgesStr, amount):
        if edgesStr == "ALL":
            result = self.sketch.reset().vertices().fillet(amount)
        else:
            raise ValueError("unknown edge selector")
        self.sketch = result
        return self
        
    def chamfer(self, edgesStr, amount):
        if edgesStr == "ALL":
            result = self.sketch.reset().vertices().chamfer(amount)
        else:
            raise ValueError("unknown edge selector")
        self.sketch = result
        return self
    
    def exportDxf(self, filename):
        export_sketchDXF(self.sketch, filename)

    def move(self, translationVector):
        self.sketch = self.sketch.moved(cq.Location(cq.Vector(translationVector)))
        return self

    def rotate(self, degrees):
        self.sketch = self.sketch.moved(cq.Location(cq.Vector(),cq.Vector(0, 0, 1), degrees))
        return self
        
    


class CadObject:
    
    def __init__(self):
        self.wp = None

    def __init__(self, workplane):
        self.wp = workplane
        
    def cq(self):
        return self.wp
        
    def fillet(self, edgesStr, amount):
        result = self.wp.edges(edgesStr).fillet(amount)
        self.wp = result
        return self
    
    def chamfer(self, edgesStr, amount):
        result = self.wp.edges(edgesStr).chamfer(amount)
        self.wp = result
        return self
    
    def move(self, translationVector):
        loc = cq.Location(cq.Vector(translationVector))
        c = self.wp.findSolid()
        c.move(loc)
        wp = cq.Workplane(obj = c)
        self.wp = wp
        return self

    def rotate(self, axis, degrees):
        c = self.wp.findSolid()
        if axis == "X":
            c = c.rotate((0,0,0),(1,0,0), degrees)
        elif axis == "Y":
            c = c.rotate((0,0,0),(0,1,0), degrees)
        elif axis == "Z":
            c = c.rotate((0,0,0),(0,0,1), degrees)
        else:
            raise ValueError("axis unknown")
        wp = cq.Workplane(obj = c)
        self.wp = wp
        return self

    def cut(self, cad2):
        c1 = self.wp.findSolid()
        c2 = cad2.wp.findSolid()
        c = c1.cut(c2)
        wp = cq.Workplane(obj = c)
        self.wp = wp
        return self
    
    def fuse(self, cad2):
        c1 = self.wp.findSolid()
        c2 = cad2.wp.findSolid()
        c = c1.fuse(c2)
        wp = cq.Workplane(obj = c)
        self.wp = wp
        return self

    def addExtrude(self, faceStr, sketch, amount):
        result = self.wp.faces(faceStr).workplane(origin=(0,0,0)).placeSketch(sketch.cq()).extrude(amount, "a")
        self.wp = result
        return self

    def cutExtrude(self, faceStr, sketch, amount):
        result = self.wp.faces(faceStr).workplane(origin=(0,0,0)).placeSketch(sketch.cq()).extrude(amount, "s")
        self.wp = result
        return self

    def makeExtrude(self, faceStr, sketch, amount):
        result = self.wp.faces(faceStr).workplane(origin=(0,0,0)).placeSketch(sketch.cq()).extrude(amount, False)
        c = result.findSolid().copy()
        wp = cq.Workplane(obj = c)
        return CadObject(wp)        

    def CenterOfBoundBox(self):
        c = self.wp.findSolid()
        shapes = []
        for s in c:
            shapes.append(s)
        return cq.Shape.CombinedCenterOfBoundBox(shapes)

    def copy(self):
        c = self.wp.findSolid().copy()
        wp = cq.Workplane(obj = c)
        return CadObject(wp)
            
    def exportStep(self, filename):
        self.wp.findSolid().exportStep(filename)
        
    def exportStl(self, filename):
        self.wp.findSolid().exportStl(filename)

    def renderSvg(self, filename):
        c = self.wp.findSolid()
        cq.exporters.export(c,
                            filename,
                            opt={
                                "width": 300,
                                "height": 300,
                                "marginLeft": 10,
                                "marginTop": 10,
                                "showAxes": False,
                                "projectionDir": (1, 1, 1),
                                "strokeWidth": 0.8,
                                "strokeColor": (0, 0, 0),
                                "hiddenColor": (0, 0, 255),
                                "showHidden": False,
                            },)        

class Assembly:
    
    def __init__(self):
        self.assy = cq.Assembly()
        
    def cq(self):
        return self.assy

    def add(self, part: CadObject):
        self.assy.add(part.cq())
        return self.assy


class M3Helper:

    dia = 3
    diaHole = 3.2
    diaCoreHole = 2.5
    diaThreadInsert = 3.9

    r = dia/2
    rHole = diaHole/2
    rCoreHole = diaCoreHole/2
    rThreadInsert = diaThreadInsert/2

M3 = M3Helper()
