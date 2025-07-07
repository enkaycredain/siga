# src/utils.py
import pandas as pd
from typing import List
import logging
import os
import csv

logger = logging.getLogger('siga.app')

def read_companies_from_csv(file_path: str) -> List[str]:
    """
    Reads a list of company names from the first column of a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        List[str]: A list of company names. Returns an empty list if file not found
                   or if no valid companies are found.
    """
    if not os.path.exists(file_path):
        logger.error(f"CSV file not found at: {file_path}")
        return []

    companies = []
    try:
        df = pd.read_csv(file_path, header=None)

        if df.empty:
            logger.warning(f"CSV file '{file_path}' is empty.")
            return []

        companies = df.iloc[:, 0].astype(str).dropna().tolist()
        companies = [company.strip() for company in companies if company.strip()]
        logger.info(f"Successfully read {len(companies)} companies from '{file_path}'.")

    except pd.errors.EmptyDataError:
        logger.warning(f"CSV file '{file_path}' is empty or contains no data.")
        return []
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing CSV file '{file_path}': {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading CSV '{file_path}': {e}")
        return []

    return companies

if __name__ == "__main__":
    from src.logger import setup_logging
    setup_logging(log_level="DEBUG")

    dummy_csv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    os.makedirs(dummy_csv_dir, exist_ok=True)
    dummy_csv_path = os.path.join(dummy_csv_dir, 'test_companies.csv')

    with open(dummy_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Company Name', 'Other Data'])
        writer.writerow(['Apple Inc.', 'Tech'])
        writer.writerow(['Microsoft Corp.', 'Software'])
        writer.writerow(['Alphabet Inc.', 'Internet'])
        writer.writerow(['', 'Empty Row'])
        writer.writerow(['Tesla Inc.', 'Automotive'])
        writer.writerow(['', ''])
        writer.writerow(['Samsung Electronics', 'Electronics'])

    logger.info(f"Created dummy CSV at: {dummy_csv_path}")

    companies_list = read_companies_from_csv(dummy_csv_path)
    logger.info(f"Companies read: {companies_list}")
    assert len(companies_list) == 5, f"Expected 5 companies, got {len(companies_list)}"
    assert "Apple Inc." in companies_list
    assert "Empty Row" not in companies_list

    logger.info("\nTesting with non-existent file:")
    non_existent_companies = read_companies_from_csv("non_existent.csv")
    logger.info(f"Companies read from non-existent file: {non_existent_companies}")
    assert len(non_existent_companies) == 0

    empty_csv_path = os.path.join(dummy_csv_dir, 'empty_companies.csv')
    with open(empty_csv_path, 'w', newline='') as f:
        pass
    logger.info(f"\nCreated empty CSV at: {empty_csv_path}")
    empty_companies_list = read_companies_from_csv(empty_csv_path)
    logger.info(f"Companies read from empty file: {empty_companies_list}")
    assert len(empty_companies_list) == 0

    logger.info("\nAll CSV utility tests passed!")
