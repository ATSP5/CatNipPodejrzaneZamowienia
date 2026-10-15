import datetime as dt

from AnomalyReport import AnomalyReport
from ProjectFolders import ProjectFolders


class FindingsCsvWriter:
    """Zapisuje listę podejrzanych zamówień do output/ jako CSV dla Excela (średnik, UTF-8 z BOM)."""

    def __init__(self, report: AnomalyReport, folders: ProjectFolders):
        self.report = report
        self.folders = folders

    def csv_path(self) -> str:
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.folders.output_path("podejrzane_zamowienia_%s.csv" % stamp)
        self.report.flagged.to_csv(path, sep=";", decimal=",", index=False, encoding="utf-8-sig")
        print("Zapisano %d podejrzanych zamówień: %s" % (self.report.flagged_count, path))
        return path
