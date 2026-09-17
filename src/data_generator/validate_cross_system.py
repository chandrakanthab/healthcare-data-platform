import os
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

REPO_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

EMR_DIR = os.path.join(
    REPO_ROOT,
    "sample-data",
    "emr"
)

LIS_DIR = os.path.join(
    REPO_ROOT,
    "sample-data",
    "lis"
)

PHARMACY_DIR = os.path.join(
    REPO_ROOT,
    "sample-data",
    "pharmacy"
)

BILLING_DIR = os.path.join(
    REPO_ROOT,
    "sample-data",
    "billing"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print()
    print("=" * 60)
    print("LOADING CROSS-SYSTEM DATA")
    print("=" * 60)

    data = {

        "patient": pd.read_csv(
            os.path.join(
                EMR_DIR,
                "patient.csv"
            )
        ),

        "provider": pd.read_csv(
            os.path.join(
                EMR_DIR,
                "provider.csv"
            )
        ),

        "encounter": pd.read_csv(
            os.path.join(
                EMR_DIR,
                "encounter.csv"
            )
        ),

        "appointment": pd.read_csv(
            os.path.join(
                EMR_DIR,
                "appointment.csv"
            )
        ),

        "lab_order": pd.read_csv(
            os.path.join(
                LIS_DIR,
                "lab_order.csv"
            )
        ),

        "lab_result": pd.read_csv(
            os.path.join(
                LIS_DIR,
                "lab_result.csv"
            )
        ),

        "test_master": pd.read_csv(
            os.path.join(
                LIS_DIR,
                "test_master.csv"
            )
        ),

        "prescription": pd.read_csv(
            os.path.join(
                PHARMACY_DIR,
                "prescription.csv"
            )
        ),

        "dispensing": pd.read_csv(
            os.path.join(
                PHARMACY_DIR,
                "dispensing.csv"
            )
        ),

        "medication_master": pd.read_csv(
            os.path.join(
                PHARMACY_DIR,
                "medication_master.csv"
            )
        ),

        "invoice": pd.read_csv(
            os.path.join(
                BILLING_DIR,
                "invoice.csv"
            )
        ),

        "invoice_line": pd.read_csv(
            os.path.join(
                BILLING_DIR,
                "invoice_line.csv"
            )
        ),

        "payment": pd.read_csv(
            os.path.join(
                BILLING_DIR,
                "payment.csv"
            )
        )
    }

    for name, df in data.items():

        print(
            f"✓ Loaded {name}: "
            f"{len(df)} records"
        )

    return data


# ============================================================
# FILE VALIDATION
# ============================================================

def validate_required_files():

    required_files = [

        (EMR_DIR, "patient.csv"),
        (EMR_DIR, "provider.csv"),
        (EMR_DIR, "appointment.csv"),
        (EMR_DIR, "encounter.csv"),

        (LIS_DIR, "test_master.csv"),
        (LIS_DIR, "lab_order.csv"),
        (LIS_DIR, "lab_result.csv"),

        (
            PHARMACY_DIR,
            "medication_master.csv"
        ),
        (
            PHARMACY_DIR,
            "prescription.csv"
        ),
        (
            PHARMACY_DIR,
            "dispensing.csv"
        ),

        (BILLING_DIR, "invoice.csv"),
        (
            BILLING_DIR,
            "invoice_line.csv"
        ),
        (BILLING_DIR, "payment.csv")
    ]

    for directory, filename in required_files:

        path = os.path.join(
            directory,
            filename
        )

        if not os.path.exists(path):

            raise FileNotFoundError(
                f"Required source file missing: "
                f"{path}"
            )

    print(
        "✓ Required source files validation passed"
    )


# ============================================================
# GENERIC FK VALIDATION
# ============================================================

def validate_fk(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship
):

    child_values = set(
        child_df[
            child_column
        ].dropna()
    )

    parent_values = set(
        parent_df[
            parent_column
        ].dropna()
    )

    invalid = (
        child_values - parent_values
    )

    if invalid:

        raise ValueError(
            f"Cross-system FK validation failed: "
            f"{relationship}. "
            f"Invalid values: "
            f"{list(invalid)[:10]}"
        )

    print(
        f"✓ Cross-system FK passed: "
        f"{relationship}"
    )


# ============================================================
# PATIENT → ENCOUNTER
# ============================================================

def validate_patient_encounters(
    data
):

    validate_fk(
        data["encounter"],
        "patient_id",
        data["patient"],
        "patient_id",
        "encounter → patient"
    )


# ============================================================
# ENCOUNTER → LIS
# ============================================================

def validate_lis_relationships(
    data
):

    validate_fk(
        data["lab_order"],
        "encounter_id",
        data["encounter"],
        "encounter_id",
        "lab_order → encounter"
    )

    validate_fk(
        data["lab_order"],
        "ordering_provider_id",
        data["provider"],
        "provider_id",
        "lab_order → provider"
    )

    validate_fk(
        data["lab_order"],
        "test_code",
        data["test_master"],
        "test_code",
        "lab_order → test_master"
    )

    validate_fk(
        data["lab_result"],
        "lab_order_id",
        data["lab_order"],
        "lab_order_id",
        "lab_result → lab_order"
    )


# ============================================================
# ENCOUNTER → PHARMACY
# ============================================================

def validate_pharmacy_relationships(
    data
):

    validate_fk(
        data["prescription"],
        "encounter_id",
        data["encounter"],
        "encounter_id",
        "prescription → encounter"
    )

    validate_fk(
        data["prescription"],
        "medication_code",
        data["medication_master"],
        "medication_code",
        "prescription → medication_master"
    )

    validate_fk(
        data["dispensing"],
        "prescription_id",
        data["prescription"],
        "prescription_id",
        "dispensing → prescription"
    )


# ============================================================
# ENCOUNTER → BILLING
# ============================================================

def validate_billing_relationships(
    data
):

    validate_fk(
        data["invoice"],
        "encounter_id",
        data["encounter"],
        "encounter_id",
        "invoice → encounter"
    )

    validate_fk(
        data["invoice_line"],
        "invoice_id",
        data["invoice"],
        "invoice_id",
        "invoice_line → invoice"
    )

    validate_fk(
        data["payment"],
        "invoice_id",
        data["invoice"],
        "invoice_id",
        "payment → invoice"
    )


# ============================================================
# PATIENT JOURNEY TRACEABILITY
# ============================================================

def build_patient_journey(
    data
):

    print()
    print("=" * 60)
    print("BUILDING PATIENT JOURNEY")
    print("=" * 60)

    encounter = data["encounter"][
        [
            "encounter_id",
            "patient_id",
            "provider_id",
            "department_id",
            "encounter_type",
            "admission_datetime",
            "encounter_status"
        ]
    ].copy()

    # --------------------------------------------------------
    # Lab activity
    # --------------------------------------------------------

    lab_summary = (
        data["lab_order"]
        .groupby("encounter_id")
        .agg(
            lab_orders=(
                "lab_order_id",
                "count"
            )
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Pharmacy activity
    # --------------------------------------------------------

    pharmacy_summary = (
        data["prescription"]
        .groupby("encounter_id")
        .agg(
            prescriptions=(
                "prescription_id",
                "count"
            )
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Billing activity
    # --------------------------------------------------------

    billing_summary = (
        data["invoice"]
        .groupby("encounter_id")
        .agg(
            invoices=(
                "invoice_id",
                "count"
            )
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    journey = encounter.merge(
        lab_summary,
        on="encounter_id",
        how="left"
    )

    journey = journey.merge(
        pharmacy_summary,
        on="encounter_id",
        how="left"
    )

    journey = journey.merge(
        billing_summary,
        on="encounter_id",
        how="left"
    )

    journey[
        [
            "lab_orders",
            "prescriptions",
            "invoices"
        ]
    ] = journey[
        [
            "lab_orders",
            "prescriptions",
            "invoices"
        ]
    ].fillna(0)

    journey[
        [
            "lab_orders",
            "prescriptions",
            "invoices"
        ]
    ] = journey[
        [
            "lab_orders",
            "prescriptions",
            "invoices"
        ]
    ].astype(int)

    print(
        f"✓ Patient journey created: "
        f"{len(journey)} encounters"
    )

    return journey


# ============================================================
# ORPHAN DETECTION
# ============================================================

def detect_orphans(
    data
):

    print()
    print("=" * 60)
    print("ORPHAN RECORD DETECTION")
    print("=" * 60)

    relationships = [

        (
            "lab_order",
            "encounter_id",
            "encounter",
            "encounter_id"
        ),

        (
            "prescription",
            "encounter_id",
            "encounter",
            "encounter_id"
        ),

        (
            "invoice",
            "encounter_id",
            "encounter",
            "encounter_id"
        ),

        (
            "lab_result",
            "lab_order_id",
            "lab_order",
            "lab_order_id"
        ),

        (
            "dispensing",
            "prescription_id",
            "prescription",
            "prescription_id"
        ),

        (
            "invoice_line",
            "invoice_id",
            "invoice",
            "invoice_id"
        ),

        (
            "payment",
            "invoice_id",
            "invoice",
            "invoice_id"
        )
    ]

    total_orphans = 0

    for (
        child_table,
        child_column,
        parent_table,
        parent_column
    ) in relationships:

        child_values = set(
            data[
                child_table
            ][
                child_column
            ].dropna()
        )

        parent_values = set(
            data[
                parent_table
            ][
                parent_column
            ].dropna()
        )

        orphan_values = (
            child_values - parent_values
        )

        orphan_count = len(
            orphan_values
        )

        total_orphans += orphan_count

        if orphan_count > 0:

            print(
                f"✗ {child_table} → "
                f"{parent_table}: "
                f"{orphan_count} orphan values"
            )

        else:

            print(
                f"✓ {child_table} → "
                f"{parent_table}: "
                f"no orphan values"
            )

    if total_orphans > 0:

        raise ValueError(
            f"Total orphan values detected: "
            f"{total_orphans}"
        )

    print()
    print(
        "✓ ORPHAN DETECTION PASSED"
    )


# ============================================================
# COMPLETE VALIDATION
# ============================================================

def validate_cross_system(
    data
):

    print()
    print("=" * 60)
    print("CROSS-SYSTEM HEALTHCARE DATA VALIDATION")
    print("=" * 60)

    validate_required_files()

    validate_patient_encounters(
        data
    )

    validate_lis_relationships(
        data
    )

    validate_pharmacy_relationships(
        data
    )

    validate_billing_relationships(
        data
    )

    detect_orphans(
        data
    )

    journey = build_patient_journey(
        data
    )

    return journey


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print(
        "CITYCARE HOSPITAL - "
        "CROSS-SYSTEM DATA VALIDATOR"
    )
    print("=" * 60)

    data = load_data()

    journey = validate_cross_system(
        data
    )

    print()
    print("=" * 60)
    print(
        "CROSS-SYSTEM VALIDATION COMPLETE"
    )
    print("=" * 60)

    print()
    print(
        "Healthcare encounters traced:"
    )

    print(
        journey[
            [
                "encounter_id",
                "patient_id",
                "lab_orders",
                "prescriptions",
                "invoices"
            ]
        ].head(10).to_string(
            index=False
        )
    )

    print()
    print(
        "✓ ALL CROSS-SYSTEM VALIDATIONS PASSED"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()