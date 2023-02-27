import csv
import os

from gfs.constants import DIRECTORY_PROJECT_ROOT


class Histogram(dict[tuple[int, ...], int]):
    def export(self, project: str, file: str, axis: int) -> None:
        hist = {k[axis]: v for k, v in self.items()}
        hist_list = [[k, v] for k, v in hist.items()]
        hist_list.sort(key=lambda x: x[0])

        output_directory = os.path.join(DIRECTORY_PROJECT_ROOT, project, "output")
        os.makedirs(output_directory, exist_ok=True)
        file_path = os.path.join(output_directory, file)
        with open(file_path, "w") as f:
            writer = csv.writer(f)
            for row in hist_list:
                writer.writerow(row)
