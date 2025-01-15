import os
import time
import logging
from processing import process_csv
from report_generator import report_file, report_terminal

def setup_logging():
    """
    Setup logging configuration.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_assets_path():
    """
    Get the absolute path to the assets folder.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))

def process_files(assets_path, overall_result):
    """
    Process all CSV files in the specified assets folder.
    Returns:
        None
    """
    try:
        # Use os.scandir to iterate over entries in the assets_path directory
        with os.scandir(assets_path) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith('.csv'):
                    try:
                        valid_months = process_csv(entry.path, overall_result)
                        report_terminal(entry.path, valid_months)
                    except Exception as e:
                        logging.error(f"Error processing file {entry.path}: {e}")
    except Exception as e:
        logging.error(f"Error accessing directory {assets_path}: {e}")


def main():
    """
    Main function to execute the program. It iterates over all CSV files in the assets folder.
    """
    setup_logging()
    
    # Execution time monitoring.
    start = time.time()
    
    # Get the path to the assets folder.
    assets_path = get_assets_path()
    
    # Global variable to store the results throughout the code.
    overall_result = {}

    # Process all CSV files.
    process_files(assets_path, overall_result)
    
    try:
        # Generate the report file.
        report_file(overall_result)
    except Exception as e:
        logging.error(f"Error generating report file: {e}")
    finally:
        # Calculate and show execution time.
        end = time.time()
        execution_time = end - start
        logging.info(f"Execution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    main()

