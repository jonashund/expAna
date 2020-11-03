class Project(object):
    def __init__(self, name, istra_acquisition_dir, export2tif_dir, dic_results_dir):
        self.name = name
        self.experiments = {}
        self.export2tif_dir = export2tif_dir
        self.istra_acquisition_dir = istra_acquisition_dir
        self.dic_results_dir = dic_results_dir

    def add_experiment(self, test):
        if isinstance(test, (Experiment)):
            self.experiments.update({test.name: test})
        else:
            raise TypeError("Test should be of type `Experiment`.")


class Experiment(object):
    def __init__(self, name):
        self.name = name

    def read_and_convert_istra_images(self, istra_acquisition_dir, export2tif_dir):
        import istra2py
        import os

        from PIL import Image

        image_reader = istra2py.Reader(
            path_dir_acquisition=os.path.join(istra_acquisition_dir, self.name),
            verbose=False,
        )

        image_reader.read()
        current_export_dir = os.path.join(export2tif_dir, self.name)
        os.makedirs(current_export_dir, exist_ok=True)

        self.image_count = len(image_reader.acquisition.images)
        # save force and displacement
        self.reaction_force = image_reader.acquisition.traverse_force
        self.traverse_displ = image_reader.acquisition.traverse_displ * 10.0

        # export images
        for img in range(self.image_count):
            filename = f"{self.name}_img_{img}.tif"
            current_image = Image.fromarray(image_reader.acquisition.images[img])

            current_image.save(os.path.join(current_export_dir, filename))

            if img == 0:
                self.ref_image = image_reader.acquisition.images[img]

    def read_istra_evaluation(self, istra_acquisition_dir, istra_evaluation_dir):
        import istra2py
        import os
        import numpy as np

        from PIL import Image

        image_reader = istra2py.Reader(
            path_dir_acquisition=os.path.join(istra_acquisition_dir, self.name),
            path_dir_evaluation=os.path.join(istra_evaluation_dir, self.name + "CORN1"),
            verbose=False,
        )

        image_reader.read(identify_images_evaluation=True)

        self.ref_image = image_reader.acquisition.images[0]

        self.image_count = np.shape(image_reader.evaluation.mask)[0]

        # save exported force and displacement
        self.reaction_force = image_reader.evaluation.traverse_force
        self.traverse_displ = image_reader.evaluation.traverse_displ * 10.0
        # save exported fields from evaluation
        self.coords = image_reader.evaluation.x
        self.def_grad = image_reader.evaluation.def_grad
        self.mask = image_reader.evaluation.mask

    def set_documentation_data(self, experiment_data):

        if experiment_data[r"\dic"] == 1:
            experiment_data[r"\dic"] = "yes"
        else:
            experiment_data[r"\dic"] = "no"

        self.documentation_data = {
            "tester": experiment_data[r"\tester"],
            "test_number": experiment_data[r"\testNumber"],
            "test_time": experiment_data[r"\testTime"].strftime("%H:%M"),
            "test_date": experiment_data[r"\testDate"].strftime("%d.%m.%Y"),
            "dic": experiment_data[r"\dic"],
            "crosshead_speed": experiment_data[r"\crossheadSpeed"],
            "testing_method": r"\_".join(
                experiment_data[r"\waveMatrixMethod"].split(r"_")
            ),
            "clamping_length": experiment_data[r"\clampingLength"],
            "clamping_torque": experiment_data[r"\clampingTorque"],
            "testing_machine": experiment_data[r"\testingMachine"],
            "specimen_type": experiment_data[r"\specimenType"],
            "material": experiment_data[r"\material"],
            "specimen_thickness": experiment_data[r"\specimenThickness"],
            "specimen_length": experiment_data[r"\specimenLength"],
            "specimen_width": experiment_data[r"\specimenWidth"],
            "specimen_orientation": experiment_data[r"\specimenOrientation"],
            "specimen_position": experiment_data[r"\specimenPosition"],
            "notch_width": experiment_data[r"\notchWidth"],
            "notch_depth": experiment_data[r"\notchDepth"],
            "load_cell": experiment_data[r"\loadCell"],
        }

    def slenderise(self):
        keep = ["documentation_data", "name", "gauge_results"]

        discard = [x for x in vars(self).keys() if not x in keep]

        for attribute in discard:
            delattr(self, attribute)


def print_remarks():
    print(
        """
    REMARKS:
        > image filtering improves convergence (lowpass_gaussian, sigma = 1)
        > a mesh grid of roughly 40 by 40 pixels works well
        > the meshed area should only contain speckled surface area and exclude the specimen's edges
        > updating the reference frame every 50 frames improves convergence
    """
    )
