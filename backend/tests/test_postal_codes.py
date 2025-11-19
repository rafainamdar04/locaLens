import pandas as pd
from pathlib import Path

def test_postal_codes_schema():
    csv_path = Path(__file__).parent.parent / 'data' / 'IndiaPostalCodes.csv'
    df = pd.read_csv(csv_path)
    required_columns = {'PIN', 'City', 'District', 'Lat', 'Lng'}
    missing = required_columns - set(df.columns)
    assert not missing, f"Missing columns: {missing}"
    assert len(df) > 0, "CSV should not be empty"

def test_lat_lon_presence():
    csv_path = Path(__file__).parent.parent / 'data' / 'IndiaPostalCodes.csv'
    df = pd.read_csv(csv_path)
    assert df['Lat'].notnull().all(), "Lat column has nulls"
    assert df['Lng'].notnull().all(), "Lng column has nulls"
    assert (df['Lat'] != 0).all(), "Lat column has zeros"
    assert (df['Lng'] != 0).all(), "Lng column has zeros"

def test_row_count():
    csv_path = Path(__file__).parent.parent / 'data' / 'IndiaPostalCodes.csv'
    df = pd.read_csv(csv_path)
    assert len(df) > 1000, "Expected at least 1000 rows in postal codes CSV"
