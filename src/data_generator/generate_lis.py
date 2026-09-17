"""
CityCare Hospital - LIS Data Generator

Generates realistic synthetic laboratory data using
actual identifiers from the EMR dataset.

Architecture:
    EMR Encounter
          |
          v
      Lab Order
          |
          v
      Lab Result

The LIS does NOT generate patient_id or encounter_id.
Those identities come from the EMR system.
"""
import os
import random
from datetime import datetime, timedelta

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42

NUM_LAB_ORDERS = 180
NUM_LAB_RESULTS = 180

REPO_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

EMR_INPUT_DIR = os.path.join(
    REPO_ROOT,
    "sample-data",
    "emr"
)

OUTPUT_DIR = os.path.join(
    REPO_ROOT,
    "sample-data",
    "lis"
)


# ============================================================
# RANDOM SEED
# ============================================================

random.seed(RANDOM_SEED)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_id(prefix, number):
    return f"{prefix}{number:06d}"


def random_datetime(start_date, end_date):
    delta = end_date - start_date

    random_seconds = random.randint(
        0,
        int(delta.total_seconds())
    )

    return start_date + timedelta(
        seconds=random_seconds
    )


# ============================================================
# LOAD EMR DATA
# ============================================================

def load_emr_data():
    """
    Load EMR data required by LIS.

    LIS depends on:
        - encounter
        - provider
    """

    encounter_path = os.path.join(
        EMR_INPUT_DIR,
        "encounter.csv"
    )

    provider_path = os.path.join(
        EMR_INPUT_DIR,
        "provider.csv"
    )

    if not os.path.exists(encounter_path):
        raise FileNotFoundError(
            f"EMR encounter file not found: {encounter_path}"
        )

    if not os.path.exists(provider_path):
        raise FileNotFoundError(
            f"EMR provider file not found: {provider_path}"
        )

    encounters = pd.read_csv(
        encounter_path
    )

    providers = pd.read_csv(
        provider_path
    )

    return encounters, providers


# ============================================================
# TEST MASTER
# ============================================================

def generate_test_master():

    tests = [
        {
            "test_code": "T001",
            "test_name": "Complete Blood Count",
            "specimen_type": "Blood",
            "unit": None,
            "reference_range": None,
            "loinc_code": "SYN-LOINC-001"
        },
        {
            "test_code": "T002",
            "test_name": "Hemoglobin",
            "specimen_type": "Blood",
            "unit": "g/dL",
            "reference_range": "12-17",
            "loinc_code": "SYN-LOINC-002"
        },
        {
            "test_code": "T003",
            "test_name": "Blood Glucose",
            "specimen_type": "Blood",
            "unit": "mg/dL",
            "reference_range": "70-100",
            "loinc_code": "SYN-LOINC-003"
        },
        {
            "test_code": "T004",
            "test_name": "Creatinine",
            "specimen_type": "Blood",
            "unit": "mg/dL",
            "reference_range": "0.6-1.3",
            "loinc_code": "SYN-LOINC-004"
        },
        {
            "test_code": "T005",
            "test_name": "Total Cholesterol",
            "specimen_type": "Blood",
            "unit": "mg/dL",
            "reference_range": "<200",
            "loinc_code": "SYN-LOINC-005"
        },
        {
            "test_code": "T006",
            "test_name": "Urine Routine",
            "specimen_type": "Urine",
            "unit": None,
            "reference_range": "Normal",
            "loinc_code": "SYN-LOINC-006"
        }
    ]

    return pd.DataFrame(tests)


# ============================================================
# LAB ORDER GENERATION
# ============================================================

def generate_lab_orders(encounters, providers, test_master):

    orders = []

    start_date = pd.Timestamp("2025-01-01")
    end_date = pd.Timestamp("2025-12-31")

    provider_ids = providers["provider_id"].tolist()
    test_codes = test_master["test_code"].tolist()

    encounter_records = encounters.to_dict("records")

    for i in range(1, NUM_LAB_ORDERS + 1):

        encounter = random.choice(
            encounter_records
        )

        encounter_id = encounter["encounter_id"]

        # Keep ordering provider related to the encounter
        encounter_provider_id = encounter["provider_id"]

        # Generate order time
        admission_datetime = pd.to_datetime(
            encounter["admission_datetime"]
        )

        ordered_datetime = admission_datetime + timedelta(
            minutes=random.randint(5, 240)
        )

        # Make sure provider actually exists
        if encounter_provider_id not in provider_ids:
            raise ValueError(
                f"Invalid provider_id found in encounter: "
                f"{encounter_provider_id}"
            )

        orders.append(
            {
                "lab_order_id": generate_id("LO", i),
                "encounter_id": encounter_id,
                "test_code": random.choice(test_codes),
                "ordered_datetime": ordered_datetime,
                "ordering_provider_id": encounter_provider_id,
                "order_status": random.choice(
                    [
                        "ORDERED",
                        "IN_PROGRESS",
                        "COMPLETED",
                        "CANCELLED"
                    ]
                )
            }
        )

    return pd.DataFrame(orders)


# ============================================================
# LAB RESULT GENERATION
# ============================================================

def generate_lab_results(lab_orders, test_master):

    results = []

    test_lookup = (
        test_master
        .set_index("test_code")
        .to_dict("index")
    )

    for i, order in enumerate(
        lab_orders.to_dict("records"),
        start=1
    ):

        test_code = order["test_code"]

        test_definition = test_lookup[
            test_code
        ]

        ordered_datetime = pd.to_datetime(
            order["ordered_datetime"]
        )

        result_datetime = ordered_datetime + timedelta(
            minutes=random.randint(30, 1440)
        )

        test_name = test_definition[
            "test_name"
        ]

        # ----------------------------------------------------
        # Generate clinically plausible synthetic values
        # ----------------------------------------------------

        if test_name == "Hemoglobin":
            result_value = round(
                random.uniform(9.0, 18.0),
                1
            )

            abnormal_flag = not (
                12.0 <= result_value <= 17.0
            )

        elif test_name == "Blood Glucose":
            result_value = round(
                random.uniform(60, 220),
                1
            )

            abnormal_flag = not (
                70 <= result_value <= 100
            )

        elif test_name == "Creatinine":
            result_value = round(
                random.uniform(0.4, 2.5),
                2
            )

            abnormal_flag = not (
                0.6 <= result_value <= 1.3
            )

        elif test_name == "Total Cholesterol":
            result_value = round(
                random.uniform(120, 300),
                1
            )

            abnormal_flag = result_value >= 200

        elif test_name == "Complete Blood Count":
            result_value = "NORMAL"

            abnormal_flag = random.choice(
                [True, False]
            )

        elif test_name == "Urine Routine":
            result_value = random.choice(
                [
                    "NORMAL",
                    "NORMAL",
                    "TRACE PROTEIN",
                    "POSITIVE"
                ]
            )

            abnormal_flag = (
                result_value != "NORMAL"
            )

        else:
            result_value = "NORMAL"
            abnormal_flag = False

        results.append(
            {
                "lab_result_id": generate_id("LR", i),
                "lab_order_id": order["lab_order_id"],
                "result_value": str(result_value),
                "result_unit": test_definition["unit"],
                "result_status": random.choice(
                    [
                        "FINAL",
                        "FINAL",
                        "PRELIMINARY"
                    ]
                ),
                "result_datetime": result_datetime,
                "abnormal_flag": abnormal_flag
            }
        )

    return pd.DataFrame(results)


# ============================================================
# VALIDATION
# ============================================================

def validate_primary_keys(df, column_name, table_name):

    if df[column_name].isnull().any():
        raise ValueError(
            f"NULL primary key found: "
            f"{table_name}.{column_name}"
        )

    if df[column_name].duplicated().any():
        duplicates = (
            df.loc[
                df[column_name].duplicated(),
                column_name
            ]
            .tolist()
        )

        raise ValueError(
            f"Duplicate primary key found in "
            f"{table_name}.{column_name}: "
            f"{duplicates}"
        )

    print(
        f"✓ PK validation passed: "
        f"{table_name}.{column_name}"
    )


def validate_foreign_key(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship
):

    child_values = set(
        child_df[child_column]
        .dropna()
    )

    parent_values = set(
        parent_df[parent_column]
        .dropna()
    )

    invalid_values = (
        child_values - parent_values
    )

    if invalid_values:
        raise ValueError(
            f"FK validation failed: "
            f"{relationship}. "
            f"Invalid values: "
            f"{list(invalid_values)[:10]}"
        )

    print(
        f"✓ FK validation passed: "
        f"{relationship}"
    )


def validate_result_dates(
    lab_orders,
    lab_results
):

    orders = lab_orders[
        [
            "lab_order_id",
            "ordered_datetime"
        ]
    ].copy()

    results = lab_results[
        [
            "lab_order_id",
            "result_datetime"
        ]
    ].copy()

    merged = results.merge(
        orders,
        on="lab_order_id",
        how="left"
    )

    invalid = (
        merged["result_datetime"]
        <
        merged["ordered_datetime"]
    )

    if invalid.any():
        raise ValueError(
            "Lab result date validation failed"
        )

    print(
        "✓ Lab result date validation passed"
    )


# ============================================================
# MAIN VALIDATION
# ============================================================

def validate_lis_data(
    encounters,
    providers,
    test_master,
    lab_orders,
    lab_results
):

    print()
    print("=" * 60)
    print("LIS DATA VALIDATION")
    print("=" * 60)

    # Primary keys
    validate_primary_keys(
        test_master,
        "test_code",
        "test_master"
    )

    validate_primary_keys(
        lab_orders,
        "lab_order_id",
        "lab_order"
    )

    validate_primary_keys(
        lab_results,
        "lab_result_id",
        "lab_result"
    )

    # Foreign keys
    validate_foreign_key(
        lab_orders,
        "encounter_id",
        encounters,
        "encounter_id",
        "lab_order → encounter"
    )

    validate_foreign_key(
        lab_orders,
        "ordering_provider_id",
        providers,
        "provider_id",
        "lab_order → provider"
    )

    validate_foreign_key(
        lab_orders,
        "test_code",
        test_master,
        "test_code",
        "lab_order → test_master"
    )

    validate_foreign_key(
        lab_results,
        "lab_order_id",
        lab_orders,
        "lab_order_id",
        "lab_result → lab_order"
    )

    # Date validation
    validate_result_dates(
        lab_orders,
        lab_results
    )

    print()
    print("✓ ALL LIS VALIDATIONS PASSED")


# ============================================================
# WRITE CSV FILES
# ============================================================

def write_csv(df, filename):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"✓ Written {filename}: "
        f"{len(df)} records"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("CITYCARE HOSPITAL - LIS DATA GENERATOR")
    print("=" * 60)

    print()
    print(f"Random seed: {RANDOM_SEED}")

    # --------------------------------------------------------
    # Load EMR
    # --------------------------------------------------------

    encounters, providers = load_emr_data()

    # --------------------------------------------------------
    # Generate master data
    # --------------------------------------------------------

    test_master = generate_test_master()

    # --------------------------------------------------------
    # Generate transactional data
    # --------------------------------------------------------

    lab_orders = generate_lab_orders(
        encounters,
        providers,
        test_master
    )

    lab_results = generate_lab_results(
        lab_orders,
        test_master
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_lis_data(
        encounters,
        providers,
        test_master,
        lab_orders,
        lab_results
    )

    # --------------------------------------------------------
    # Write files
    # --------------------------------------------------------

    print()

    write_csv(
        test_master,
        "test_master.csv"
    )

    write_csv(
        lab_orders,
        "lab_order.csv"
    )

    write_csv(
        lab_results,
        "lab_result.csv"
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("LIS GENERATION COMPLETE")
    print("=" * 60)

    print()
    print(f"Test Master  : {len(test_master)} records")
    print(f"Lab Orders   : {len(lab_orders)} records")
    print(f"Lab Results  : {len(lab_results)} records")

    print()
    print("Output directory:")
    print(OUTPUT_DIR)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()