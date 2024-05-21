---
Make:
  AP Mount Top:
    template: printing.md
    stl-file: ../Legacy/STLs/ap_mount_for_1430_top.stl
    stlname: ap_mount_for_1430_top.stl
    material: PLA
    weight-qty: 40g
    supports: "Yes"
  AP Mount Bottom:
    template: printing.md
    stl-file: ../Legacy/STLs/ap_mount_for_1430_bottom.stl
    stlname: ap_mount_for_1430_bottom.stl
    material: PLA
    weight-qty: 40g
    supports: "Yes"
---

# Prepare the case

{{BOM}}

[M4x10mm countersunk screws]: parts/Hardware.yaml#CskScrew_M4x10mm_SS
[M4x10mm cap screws]: parts/Hardware.yaml#CapScrew_M4x10mm_SS

## Construct the lid insert {pagestep}

* Join [AP Mount Top]{make, qty:1,cat:printed} and [AP Mount Bottom]{make, qty:1,cat:printed} together using two [M4x10mm countersunk screws]{qty: 2,cat: mech} and a [3mm Allen key](parts/metric_allen_keys.md){qty: 1,cat: tool}
* Using three more [M4x10mm countersunk screws]{qty: 3,cat: mech} attach the brackets that came with your three UniFi Access Points to the holes just below the join between the two prints.

## Attach to case{pagestep}

* Get your [Peli Case][Peli Case 1430](PeliCalse1430.md){qty:1} and open the lid.
* Locate the mounting lugs on the Peli Case lid and align the lid insert with these lugs
* Use [M4x10mm cap screws]{qty: 2,cat: mech} to attach the inset into the Peli Case.

>!! **TODO**  
>!! Add images of this step
