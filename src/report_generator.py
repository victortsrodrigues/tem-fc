import csv
import os
import logging

def report_terminal(file_path, valid_months):  
    # Displaying the number of months that meet the condition
    logging.info(f"File: {file_path}")
    logging.info(f"Total number of valid months: {valid_months}")
    if valid_months >= 48:
        logging.info("Eligible!")
    else:
        pending_months = 48 - valid_months
        logging.info(f"Number of pending months: {pending_months}")
        logging.info("Not eligible!")
    logging.info("-" * 40)

def report_file(overall_result):
    """
    Generate a CSV report in the parent directory.
    Args:
      overall_result (dict): Dictionary with the results of the analysis for each file.
    """
    try:
        parent_dir = os.path.join(os.path.dirname(__file__), '..')
        file_path = os.path.join(parent_dir, "overall_result.csv")
        with open(file_path, mode="w", newline="") as file:
            fieldnames = ["File", "Status", "Pending", "Semesters 40", "Semesters 30", "Semesters 20"]
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for file_path, value in overall_result.items():
                # Extract the file name and remove the '.csv' extension
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                writer.writerow({"File": file_name,
                                "Status": value["status"],
                                "Pending": value["pending"],
                                "Semesters 40": value["semesters_40"],
                                "Semesters 30": value["semesters_30"],
                                "Semesters 20": value["semesters_20"]})
        logging.info(f"Report generated successfully.")
    except IOError as e:
        logging.error(f"Error writing report file: {e}")