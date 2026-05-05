
from pathlib import Path
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "Data" / "Cleaned_Data"
DEFAULT_DB_PATH = BASE_DIR / "bird_species_observations.db"

TABLE_SOURCES = {
	"cleaned_forest_data": "cleaned_forest_data.csv",
	"cleaned_grassland_data": "cleaned_grassland_data.csv",
	"master_bird_monitoring_data": "master_bird_monitoring_data.csv",
	"yearly_trends": "yearly_trends.csv",
	"monthly_trends": "monthly_trends.csv",
	"hourly_trends": "hourly_trends.csv",
}


def build_database(database_path: Path = DEFAULT_DB_PATH) -> Path:
	"""Create or refresh the SQLite database from the cleaned CSV files."""

	missing_files = [
		csv_name for csv_name in TABLE_SOURCES.values() if not (DATA_DIR / csv_name).exists()
	]
	if missing_files:
		missing_list = ", ".join(sorted(missing_files))
		raise FileNotFoundError(f"Missing cleaned dataset(s): {missing_list}")

	database_path.parent.mkdir(parents=True, exist_ok=True)

	with sqlite3.connect(database_path) as connection:
		for table_name, csv_name in TABLE_SOURCES.items():
			csv_path = DATA_DIR / csv_name
			frame = pd.read_csv(csv_path, low_memory=False)
			frame.to_sql(table_name, connection, if_exists="replace", index=False)

		connection.commit()

	return database_path


def main() -> None:
	database_path = build_database()
	print(f"SQLite database created at: {database_path}")
	print("Loaded tables:")
	for table_name in TABLE_SOURCES:
		print(f"- {table_name}")


if __name__ == "__main__":
	main()
