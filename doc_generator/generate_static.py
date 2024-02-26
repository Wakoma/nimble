"""
Generate a bunch of STL files
to show case the possiblilties of the nimble cadquery code

To be replaced later with code that builds complete bundles
of STL files and documentation for custom configurations
"""
import os
import sys
from pathlib import Path

from orchestration import OrchestrationRunner
import cadquery as cq
from cadquery import cqgi

# List of generated files (description, filename)
generated_files = []


def generate():

    print("Starting generate()")
    runner = OrchestrationRunner("static", "static")

    print("Setting up build environment")
    runner.setup(create_only_build_dir=True)

    generate_leg(294, 3.6, runner._build_dir / "beam-21holes.stl")
    generated_files.append(("Rack leg with 21 holes", "beam-21holes.stl"))
    generate_leg(168, 3.6, runner._build_dir / "beam-12holes.stl")
    generated_files.append(("Rack leg with 12 holes", "beam-12holes.stl"))
    generate_leg(294, 5.8, runner._build_dir / "beam-M6-21holes.stl")
    generated_files.append(("Rack leg with 21 holes (M6 version)", "beam-M6-21holes.stl"))
    generate_leg(168, 5.8, runner._build_dir / "beam-M6-12holes.stl")
    generated_files.append(("Rack leg with 12 holes (M6 version)", "beam-M6-12holes.stl"))

    for (t, c) in [
            ("stuff", 3),
            ("stuff-thin", 3),
            ("nuc", 3),
            ("nuc", 4),
            ("usw-flex", 3),
            ("usw-flex-mini", 2),
            ("anker-powerport5", 2),
            ("anker-a2123", 2),
            ("anker-atom3slim", 2),
            ("hdd35", 2),
            ("dual-ssd", 2),
            ("raspi", 2)]:
        filename = f"shelf_6in_{c}u_{t}.stl"
        out_file = runner._build_dir / (filename)
        print(f"Creating {t} shelf, saving to {out_file}")
        generate_shelf(t, c, out_file)
        generated_files.append((f"6 inch shelf, type {t}, height {c} units", filename))

    # create index.html with links to all generated files
    index_file = runner._build_dir / "index.html"
    with open(index_file, "w") as f:
        f.write("<html>")
        f.write("""
                <head>
                <title>Nimble generated files</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                </style>
                </head>
                <body>
                <p>
                This is temporary output of the new "smart doc" Nimble feature.
                </p>

                <p>
                In the future it will create complete bundles
                of STL files and documentation for custom configurations<br><br>
                </p>

                <p>
                For more details on this project see
                <a href="https://github.com/Wakoma/nimble">https://github.com/Wakoma/nimble</a>
                </p>
                """)

        f.write("<h3>Generated files:</h3>")
        f.write("<ul>")
        for (desc, filename) in generated_files:
            f.write(f"<li><a href='{filename}'>{desc}</a></li>")
        f.write("</ul>")
        f.write("</body></html>")

    print("Finished generate()")


def generate_leg(length, mounting_holes_dia, out_file):
    params = {'length': length, 'mounting_holes_dia': mounting_holes_dia}
    run_cqgi_model_script_and_save("rack_leg.py", params, out_file)


def generate_shelf(shelf_type, hole_count, out_file):
    params = {'shelf_type': shelf_type, 'hole_count': hole_count}
    run_cqgi_model_script_and_save("tray_6in.py", params, out_file)


def run_cqgi_model_script_and_save(file_name, params, out_file):
    """
    Handle executing the model script via CQGI, save result
    """
    # get path to this script file
    module_folder = Path(os.path.abspath(__file__)).parent
    module_folder.resolve()

    # remember python path to restore later
    python_path = sys.path

    # Add the path to the cadquery script to the python path
    cq_path = module_folder / "mechanical" / "components" / "cadquery"
    sys.path.append(str(cq_path))

    # Read and execute the cadquery script
    user_script = ""
    with open(cq_path / file_name) as f:
        user_script = f.read()

    # Build the object with the customized parameters and get it ready to export
    build_result = cqgi.parse(user_script).build(build_parameters=params)

    # restore python path
    sys.path = python_path

    if build_result.success:
        res = build_result.results[0].shape

        if not os.path.exists(out_file):
            cq.exporters.export(res, str(out_file))
    else:
        print(f"Failed to build {file_name}")
        print(build_result.exception)



if __name__ == "__main__":
    generate()
