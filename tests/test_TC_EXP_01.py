from utils.export_utils import CSVExporter


def test_TC_EXP_01():
    exporter = CSVExporter()
    data = [{"product_name": "X", "price": 100}]
    csv = exporter.export_to_csv_string(data)
    assert "product_name" in csv and "X" in csv
