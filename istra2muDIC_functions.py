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

    def read_and_convert_istra_images(
        self, istra_acquisition_dir, export2tif_dir, img_export=True
    ):
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

        self.img_count = len(image_reader.acquisition.images)
        # save force and displacement
        self.reaction_force = image_reader.acquisition.traverse_force
        self.traverse_displ = image_reader.acquisition.traverse_displ * 10.0

        # export images
        for img in range(self.img_count):
            filename = f"{self.name}_img_{img}.tif"
            current_image = Image.fromarray(image_reader.acquisition.images[img])

            if img_export:
                current_image.save(os.path.join(current_export_dir, filename))

            if img == 0:
                self.ref_image = image_reader.acquisition.images[img]
                if ~img_export:
                    break


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
