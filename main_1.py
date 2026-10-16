from ProjectFolders import ProjectFolders
from TableReader import TableReader
from DataScanner import DataScanner
from AnomalySettings import AnomalySettings
from PlnFormat import PlnFormat
from DemoOrderData import DemoOrderData
from OrderRules import OrderRules
from CustomerPatterns import CustomerPatterns
from AnomalyNarrator import AnomalyNarrator
from OrderDataLoader import OrderDataLoader
from AnomalyDetector import AnomalyDetector
from PodejrzaneZamowienia import PodejrzaneZamowienia
from FindingsCsvWriter import FindingsCsvWriter
from FindingsPowerBiTable import FindingsPowerBiTable
from PowerBiExport import PowerBiExport

def main():
	folders = ProjectFolders()
	reader = TableReader()
	scanner = DataScanner()
	settings = AnomalySettings()
	formatter = PlnFormat()

	data_1 = folders.folders()
	data_2 = reader.reader()
	data_3 = scanner.scanner()
	data_4 = settings.settings()
	data_5 = formatter.formatter()
	generator = DemoOrderData(data_4)
	data_6 = generator.generator()
	rules = OrderRules(data_4)
	data_7 = rules.rules()
	patterns = CustomerPatterns(data_4)
	data_8 = patterns.patterns()
	narrator = AnomalyNarrator(data_5)
	data_9 = narrator.narrator()
	dataset = OrderDataLoader(data_1, data_2, data_6, data_3)
	data_10 = dataset.dataset()
	findings = AnomalyDetector(data_10, data_7, data_8)
	data_11 = findings.findings()
	report = PodejrzaneZamowienia(data_11, data_9, data_5)
	report.show()
	def _on_report_powerbi(data_13):
		data = FindingsPowerBiTable(data_13)
		data_14 = data.table()
		plik_power_bi = PowerBiExport(data_14)
		plik_power_bi.path()
	report.bind_action('powerbi', _on_report_powerbi)
	def _on_report_eksport(data_12):
		zapisany_csv = FindingsCsvWriter(data_12, data_1)
		zapisany_csv.csv_path()
	report.bind_action('eksport', _on_report_eksport)
	pass

if __name__ == "__main__":
	main()
