import csv
import logging
from utils import parse_date, check_cbo_description
from establishment_validator import check_establishment

def process_csv(file_path, overall_result):
    """
    Function to analyze a specific CSV file and apply filters to the data.
    
    Args:
        file_path (str): Path to the CSV file.
        overall_result (dict): Dictionary to store the results of all files.
        
    Returns:
        valid_months (int): Number of valid months found in the CSV file, which will be used to determine the eligibility.
    """
    try:
        # Open the CSV file for the first time to check the valid lines
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            # Extract the header directly from the original file and capture the name of each column to be used later in the rewriting process.
            fieldnames = csv_reader.fieldnames
            # Determine the valid establishments in order to optimize the following processes.
            valid_cnes = check_establishment(csv_reader)
            valid_lines = []
            # Rewind the file to the beginning to read the lines again.
            file.seek(0)
            csv_reader = csv.DictReader(file, delimiter=';')
            unique_values_above_40 = validate_lines_above_40(csv_reader, valid_lines, valid_cnes)
            file.seek(0)
            csv_reader = csv.DictReader(file, delimiter=';')
            count_30_40, count_20_30 = validate_lines_20_30(csv_reader, valid_lines, valid_cnes, unique_values_above_40)
            
        # Valid lines are sorted by date in descending order to guarantee the correct rewriting processes.
        valid_lines.sort(key=lambda line: parse_date(line["COMP."]), reverse=True)
        
        # Rewriting the CSV file with the valid lines.
        with open(file_path, mode='w', encoding='utf-8', newline='') as output_file:
            if fieldnames is None:
                raise ValueError("The original CSV header was not identified.")
            csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=';')
            csv_writer.writeheader()
            csv_writer.writerows(valid_lines)
            
        # Calculate the total number of valid months and determine eligibility.
        total_months_40 = len(unique_values_above_40)
        total_months_30 = sum(count_30_40.values())
        total_months_20 = sum(count_20_30.values())
        valid_months = total_months_40 + (total_months_30 * 0.75) + (total_months_20 * 0.5)
        overall_result[file_path] = {
            "status": "Eligible" if valid_months >= 48 else "Not eligible",
            "pending": max(0, 48 - valid_months),
            "semesters_40": total_months_40 // 6,
            "semesters_30": total_months_30 // 6,
            "semesters_20": total_months_20 // 6
        }
    
        return valid_months
    except (FileNotFoundError, ValueError, csv.Error) as e:
        logging.error(f"Error processing CSV file {file_path} in function process_csv at line {e.__traceback__.tb_lineno}: {e}")
        return 0
    
def validate_lines_above_40(csv_reader, valid_lines, valid_cnes):
    """
    Check the unique lines with COMP. value above 40 and add them to valid_lines.
    """
    unique_values_above_40 = set()
    for line in csv_reader:
        if is_valid_line(line, valid_cnes, 40):
            comp_value = line["COMP."]
            if comp_value not in unique_values_above_40:
                unique_values_above_40.add(comp_value)
                valid_lines.append(line)
    return unique_values_above_40

def validate_lines_20_30(csv_reader, valid_lines, valid_cnes, unique_values_above_40):
    """
    Check the unique lines with COMP. value between 20 and 30 and between 30 and 40, considering frequency <= 2, and add them to valid_lines.
    """
    count_30_40 = {}
    count_20_30 = {}
    for line in csv_reader:
        if is_valid_line(line, valid_cnes, 20):
            comp_value = line["COMP."]
            chs_amb_value = float(line["CHS AMB."])
            if 30 <= chs_amb_value < 40 and comp_value not in unique_values_above_40:
                if count_30_40.get(comp_value, 0) < 2:
                    count_30_40[comp_value] = count_30_40.get(comp_value, 0) + 1
                    valid_lines.append(line)
            elif 20 <= chs_amb_value < 30 and comp_value not in unique_values_above_40:
                if count_20_30.get(comp_value, 0) < 2:
                    count_20_30[comp_value] = count_20_30.get(comp_value, 0) + 1
                    valid_lines.append(line)
    return count_30_40, count_20_30

def is_valid_line(line, valid_cnes, chs_threshold):
    """
    Check if the line is valid based on the CHS AMB. value and the CBO Description.
    If the CBO description contains "MEDICO" and "FAMILIA", the line is considered valid.
    """
    try:
        chs_amb_value = float(line["CHS AMB."])
        cbo_description = line["DESCRICAO CBO"]
        if chs_amb_value >= chs_threshold:
            if check_cbo_description(cbo_description, ["MEDICO", "FAMILIA"]):
                return True
            elif check_cbo_description(cbo_description, ["MEDICO", "CLINICO"]) and line["CNES"] in valid_cnes:
                return True
            elif check_cbo_description(cbo_description, ["MEDICOS", "CLINICO"]) and line["CNES"] in valid_cnes:
                return True
            elif check_cbo_description(cbo_description, ["MEDICO", "GENERALISTA"]) and line["CNES"] in valid_cnes:
                return True
        return False
    except ValueError:
        return False