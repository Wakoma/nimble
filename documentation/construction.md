---
Make:
  base plate:
    template: printing.md
    stl-file: ../build/printed_components/baseplate.stl
    stlname: baseplate.stl
    material: PLA
    weight-qty: 50g
  top plate:
    template: printing.md
    stl-file: ../build/printed_components/topplate.stl
    stlname: topplate.stl
    material: PLA
    weight-qty: 50g
  rack legs:
    template: printing.md
    stl-file: ../build/printed_components/beam.stl
    stlname: beam.stl
    material: PLA
    weight-qty: 60g
  stuff shelf:
    template: printing.md
    stl-file: models/Stuff_Shelf_1.0.stl
    stlname: Stuff_Shelf_1.0.stl
    material: PLA
    weight-qty: 50g
---

# Construct the and populate the rack

{{BOM}}

[M4x10mm countersunk screws]: parts/Hardware.yaml#CskScrew_M4x10mm_SS
[M4x10mm cap screws]: parts/Hardware.yaml#CapScrew_M4x10mm_SS

## Attach the legs to the base plate{pagestep}

* Get the [base plate]{make, qty:1, cat:printed} and the four [rack legs]{make, qty:4, cat:printed} that you printed earlier.
* Get an [3mm Allen key](parts/metric_allen_keys.md){qty:1, cat:tool} ready
* Use four [M4x10mm countersunk screws]{qty:4} to attach a leg to each corner of the bottom.

>!! **TODO**  
>!! Add images of this step

## Add the broad shelves {pagestep}

>!! **TODO**  
>!! Each shelf that is broad should be added in this stage


## Mount the top plate {pagestep}

* Take the [top plate]{make, qty:1, cat:printed} and place it on top of the rack.
* Use four [M4x10mm countersunk screws]{qty:4} to attach the shelf to the four legs of the rack

>!! **TODO**  
>!! Add images of this step


## Insert the remaining shelves {pagestep}

>!! **TODO**  
>!! Explain what order the assembled shelves are used.



