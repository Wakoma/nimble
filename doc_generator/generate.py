

from generate_exsource import OrchestrationRunner


def generate_docs(config, config_hash, force_rebuild=True):
    """
    generate all models and update documentation
    """

    runner = OrchestrationRunner(config, config_hash)
    runner.setup()
    runner.generate_exsource_files()


    # write gitbuilding files

    # todo
    """
    with open(outputdir_gitbuilding / '3dprintingparts.md', 'w') as f:
        f.write("# 3D print all the needed files\n\n")
        for (part,long_name) in partList:
            f.write("* %s.stl ([preview](models/%s.stl){previewpage}, [download](models/%s.stl))\n" % (part, part, part))
            f.write('\n\nYou can [download all of the STLs as a single zipfile](stlfiles.zip){zip, pattern:"*.stl"}')



    with open(outputdir_gitbuilding / '3DPParts.yaml', 'w') as f:
        for (part,long_name) in partList:
            f.write("%s:\n" % (part))
            f.write("    Name: %s\n" % (long_name))
            f.write("    Specs:\n")
            f.write("        Filename: %s.stl\n" % (part))
            #f.write("        Filename: %s.stl ([download](models/%s.stl))\n" % (part, part))
            f.write("        Manufacturing: 3D Printing\n")
            f.write("        Material: PLA or PETG\n")
            #f.write("        Preview: [preview](models/beam.stl){previewpage}\n")

    with open(outputdir_gitbuilding / 'DeviceParts.yaml', 'w') as f:
        for (part, device) in listOfTrays:
            f.write("%s:\n" % (device['ID']))
            f.write("    Name: %s\n" % (device['Name']))
            f.write("    Specs:\n")
            for k in device.keys():
                f.write("        %s: %s\n" % (k, device[k]))

    with open(outputdir_gitbuilding / 'components.md', 'w') as f:
        f.write("# Installing the components in trays\n\n")
        f.write("{{BOM}}\n")
        f.write("![](svg/baseplate_beams_topplate.svg)\n\n")
        f.write("For all of your components:\n\n")
        f.write("* find the corresponding 3d printed tray\n")
        f.write("* install the tray on the rack\n")
        f.write("* mount the device on the tray\n\n")
        f.write("Here are the devices and the trays\n\n")
        for (part, device) in listOfTrays:
            f.write("* [%s](DeviceParts.yaml#%s){Qty: 1}\n" % (device['Name'], device['ID']))
            stlfile = F"tray_{device['ID']}.stl"
            f.write("* %s ([preview](models/%s){previewpage}, [download](models/%s))\n" % (stlfile, stlfile, stlfile))
            f.write("![](svg/trays.svg)")
    """

    # Create an archive of the generated docs so that it can be downloaded
    shutil.make_archive(build_dir, 'zip', build_dir)

    print("Finished build for config_hash: " + config_hash)


# if main script, run generate_docs with test config
if __name__ == "__main__":
    config = {'config': {'server_1': 'Hardware_1', 'router_1': 'Hardware_2', 'switch_1': 'Hardware_9', 'charge_controller_1': 'Hardware_4'}}
    generate_docs(config, "test_config_hash")
