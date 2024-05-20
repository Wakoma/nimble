# 3D Printing

{{BOM}}

[PLA]:parts/filament.md "{cat:consumable}"

## Print the custom components {pagestep}


Using the slicer that comes with your [3d printer](parts/3dprinter.md){qty:1, cat: tool}, slice thent the following parts, and then print them.

Some parts require support. A brim is advised for all parts.


| Qty | Item | Material | File | Supports<br>Required?|
|-----|------|----------|------|----------------------|
{{foreachmakeitem: "| {{qty}} | {{id}} | {{weight-qty}} of [{{material}}]{qty:{{weight-qty}}}  | [{{stlname}}]({{stl-file}}){previewpage}|{{supports, default: No}}|"}}


You can [download all of the STLs as a single zipfile](all-stls.zip){zip, pattern:"*.stl"}


## Remove the brim {pagestep}

Remove the brim with a [utility knife](parts/utility_knife.md){qty:1, cat:tool}
