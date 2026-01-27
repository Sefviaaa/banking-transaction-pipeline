"""
Great Expectations Validation Runner

This script validates transaction data in BigQuery against defined expectations.
Can be run standalone or as part of the Airflow DAG.

Usage:
    python run_validation.py

Environment Variables Required:
    - GCP_PROJECT_ID: Your GCP project ID
    - GOOGLE_APPLICATION_CREDENTIALS: Path to service account key
"""

import os
import sys
import json
import logging
from datetime import datetime

from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Configuration
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
DATASET_ID = os.environ.get("BQ_DATASET_ID", "interbank_raw")
TABLE_ID = os.environ.get("BQ_TABLE_ID", "transactions")


class SimpleDataValidator:
    """
    Simple data quality validator for BigQuery tables.
    Implements core Great Expectations patterns without the full framework dependency.
    """
    
    def __init__(self, project_id: str, dataset_id: str, table_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.table_ref = f"{project_id}.{dataset_id}.{table_id}"
        self.client = bigquery.Client(project=project_id)
        self.results = []
    
    def expect_column_values_to_not_be_null(self, column: str) -> dict:
        """Check that column has no null values"""
        query = f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNTIF({column} IS NULL) as null_count
        FROM `{self.table_ref}`
        """
        result = list(self.client.query(query).result())[0]
        
        success = result.null_count == 0
        return {
            "expectation": f"expect_column_values_to_not_be_null({column})",
            "success": success,
            "details": {
                "total_rows": result.total_rows,
                "null_count": result.null_count,
                "null_percentage": round(result.null_count / result.total_rows * 100, 2) if result.total_rows > 0 else 0
            }
        }
    
    def expect_column_values_to_be_positive(self, column: str) -> dict:
        """Check that numeric column values are >= 0"""
        query = f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNTIF({column} < 0) as negative_count,
            MIN({column}) as min_value,
            MAX({column}) as max_value
        FROM `{self.table_ref}`
        """
        result = list(self.client.query(query).result())[0]
        
        success = result.negative_count == 0
        return {
            "expectation": f"expect_column_values_to_be_positive({column})",
            "success": success,
            "details": {
                "total_rows": result.total_rows,
                "negative_count": result.negative_count,
                "min_value": result.min_value,
                "max_value": result.max_value
            }
        }
    
    def expect_column_values_to_be_in_set(self, column: str, value_set: list) -> dict:
        """Check that column values are in expected set"""
        values_str = ", ".join(str(v) for v in value_set)
        query = f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNTIF({column} NOT IN ({values_str})) as invalid_count
        FROM `{self.table_ref}`
        WHERE {column} IS NOT NULL
        """
        result = list(self.client.query(query).result())[0]
        
        success = result.invalid_count == 0
        return {
            "expectation": f"expect_column_values_to_be_in_set({column}, {value_set})",
            "success": success,
            "details": {
                "total_rows": result.total_rows,
                "invalid_count": result.invalid_count
            }
        }
    
    def expect_table_row_count_to_be_between(self, min_value: int, max_value: int = None) -> dict:
        """Check that table has expected row count"""
        query = f"SELECT COUNT(*) as row_count FROM `{self.table_ref}`"
        result = list(self.client.query(query).result())[0]
        
        success = result.row_count >= min_value
        if max_value:
            success = success and result.row_count <= max_value
        
        return {
            "expectation": f"expect_table_row_count_to_be_between({min_value}, {max_value})",
            "success": success,
            "details": {
                "row_count": result.row_count,
                "min_expected": min_value,
                "max_expected": max_value
            }
        }
    
    def run_validation_suite(self) -> dict:
        """Run all validations and return summary"""
        logger.info(f"Starting validation for {self.table_ref}")
        
        validations = [
            # Null checks
            self.expect_column_values_to_not_be_null("timestamp"),
            self.expect_column_values_to_not_be_null("from_bank"),
            self.expect_column_values_to_not_be_null("amount_paid"),
            
            # Value range checks
            self.expect_column_values_to_be_positive("amount_paid"),
            self.expect_column_values_to_be_positive("amount_received"),
            
            # Categorical checks
            self.expect_column_values_to_be_in_set("is_laundering", [0, 1]),
            
            # Row count check
            self.expect_table_row_count_to_be_between(min_value=1),
        ]
        
        # Calculate summary
        passed = sum(1 for v in validations if v["success"])
        failed = len(validations) - passed
        
        summary = {
            "validation_time": datetime.utcnow().isoformat(),
            "table": self.table_ref,
            "total_expectations": len(validations),
            "passed": passed,
            "failed": failed,
            "success_rate": round(passed / len(validations) * 100, 2),
            "overall_success": failed == 0,
            "results": validations
        }
        
        return summary


def run_validation():
    """Main entry point for validation"""
    if not PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID environment variable not set")
    
    try:
        validator = SimpleDataValidator(PROJECT_ID, DATASET_ID, TABLE_ID)
        results = validator.run_validation_suite()
        
        # Log results
        logger.info(f"Validation complete: {results['passed']}/{results['total_expectations']} passed")
        
        if not results["overall_success"]:
            logger.error("Data quality validation FAILED!")
            for r in results["results"]:
                if not r["success"]:
                    logger.error(f"  FAILED: {r['expectation']}")
                    logger.error(f"    Details: {r['details']}")
            sys.exit(1)
        else:
            logger.info("All data quality checks PASSED!")
            
        # Save results to file
        output_file = f"validation_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {output_file}")
        
        return results
        
    except GoogleAPIError as e:
        logger.error(f"BigQuery error during validation: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}")
        raise


if __name__ == "__main__":
    run_validation()
