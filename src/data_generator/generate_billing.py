import os
import random
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42

NUM_INVOICES = 140

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
    "billing"
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


def money(value):
    """
    Convert a numeric value into a 2-decimal monetary value.
    """

    return Decimal(
        str(value)
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


# ============================================================
# LOAD EMR DATA
# ============================================================

def load_emr_data():

    encounter_path = os.path.join(
        EMR_INPUT_DIR,
        "encounter.csv"
    )

    if not os.path.exists(
        encounter_path
    ):
        raise FileNotFoundError(
            f"EMR encounter file not found: "
            f"{encounter_path}"
        )

    encounters = pd.read_csv(
        encounter_path
    )

    return encounters


# ============================================================
# BILLING SERVICE CATALOG
# ============================================================

def generate_service_catalog():

    services = [

        {
            "service_code": "SRV001",
            "service_description": "Consultation",
            "unit_price": Decimal("800.00")
        },

        {
            "service_code": "SRV002",
            "service_description": "Emergency Consultation",
            "unit_price": Decimal("1500.00")
        },

        {
            "service_code": "SRV003",
            "service_description": "Hospital Room Charge",
            "unit_price": Decimal("2500.00")
        },

        {
            "service_code": "SRV004",
            "service_description": "Laboratory Investigation",
            "unit_price": Decimal("500.00")
        },

        {
            "service_code": "SRV005",
            "service_description": "Radiology Investigation",
            "unit_price": Decimal("1200.00")
        },

        {
            "service_code": "SRV006",
            "service_description": "Procedure",
            "unit_price": Decimal("3000.00")
        },

        {
            "service_code": "SRV007",
            "service_description": "Pharmacy",
            "unit_price": Decimal("750.00")
        },

        {
            "service_code": "SRV008",
            "service_description": "Nursing Service",
            "unit_price": Decimal("1000.00")
        }
    ]

    return services


# ============================================================
# INVOICE GENERATION
# ============================================================

def generate_invoices(
    encounters
):

    invoices = []

    encounter_records = (
        encounters
        .to_dict("records")
    )

    selected_encounters = random.sample(
        encounter_records,
        min(
            NUM_INVOICES,
            len(encounter_records)
        )
    )

    for i, encounter in enumerate(
        selected_encounters,
        start=1
    ):

        admission_datetime = pd.to_datetime(
            encounter[
                "admission_datetime"
            ]
        )

        invoice_date = (
            admission_datetime
            +
            timedelta(
                days=random.randint(
                    0,
                    5
                )
            )
        ).date()

        invoices.append(
            {
                "invoice_id":
                    generate_id("INV", i),

                "encounter_id":
                    encounter[
                        "encounter_id"
                    ],

                "invoice_date":
                    invoice_date,

                # Temporary value.
                # It will be replaced after
                # invoice lines are generated.
                "total_amount":
                    Decimal("0.00"),

                "invoice_status":
                    random.choice(
                        [
                            "OPEN",
                            "PARTIALLY_PAID",
                            "PAID",
                            "CANCELLED"
                        ]
                    )
            }
        )

    return pd.DataFrame(
        invoices
    )


# ============================================================
# INVOICE LINE GENERATION
# ============================================================

def generate_invoice_lines(
    invoices,
    service_catalog
):

    invoice_lines = []

    line_number = 1

    for invoice in invoices.to_dict(
        "records"
    ):

        # Each invoice gets 1–4 services.
        number_of_lines = random.randint(
            1,
            4
        )

        selected_services = random.sample(
            service_catalog,
            number_of_lines
        )

        invoice_total = Decimal(
            "0.00"
        )

        for service in selected_services:

            quantity = random.randint(
                1,
                3
            )

            unit_price = service[
                "unit_price"
            ]

            line_amount = money(
                unit_price * quantity
            )

            invoice_total += (
                line_amount
            )

            invoice_lines.append(
                {
                    "invoice_line_id":
                        generate_id(
                            "IL",
                            line_number
                        ),

                    "invoice_id":
                        invoice[
                            "invoice_id"
                        ],

                    "service_code":
                        service[
                            "service_code"
                        ],

                    "service_description":
                        service[
                            "service_description"
                        ],

                    "quantity":
                        quantity,

                    "unit_price":
                        unit_price,

                    "line_amount":
                        line_amount
                }
            )

            line_number += 1

    return pd.DataFrame(
        invoice_lines
    )


# ============================================================
# CALCULATE INVOICE TOTALS
# ============================================================

def calculate_invoice_totals(
    invoices,
    invoice_lines
):

    totals = (
        invoice_lines
        .groupby("invoice_id")[
            "line_amount"
        ]
        .sum()
        .reset_index()
    )

    totals = totals.rename(
        columns={
            "line_amount":
                "calculated_total"
        }
    )

    invoices = invoices.merge(
        totals,
        on="invoice_id",
        how="left"
    )

    invoices["calculated_total"] = (
        invoices[
            "calculated_total"
        ]
        .fillna(
            Decimal("0.00")
        )
    )

    invoices["total_amount"] = (
        invoices[
            "calculated_total"
        ]
    )

    invoices = invoices.drop(
        columns=[
            "calculated_total"
        ]
    )

    return invoices


# ============================================================
# PAYMENT GENERATION
# ============================================================

def generate_payments(
    invoices
):

    payments = []

    payment_number = 1

    for invoice in invoices.to_dict(
        "records"
    ):

        invoice_total = Decimal(
            str(
                invoice[
                    "total_amount"
                ]
            )
        )

        # Some invoices have no payment yet.
        payment_scenario = random.choice(
            [
                "NO_PAYMENT",
                "FULL_PAYMENT",
                "PARTIAL_PAYMENT",
                "FULL_PAYMENT"
            ]
        )

        invoice_date = pd.Timestamp(
            invoice[
                "invoice_date"
            ]
        )

        if payment_scenario == "NO_PAYMENT":

            continue

        elif payment_scenario == "FULL_PAYMENT":

            payment_amount = invoice_total

        else:

            # Generate a partial payment
            # strictly below invoice total.
            if invoice_total > Decimal(
                "100.00"
            ):

                payment_amount = money(
                    invoice_total
                    *
                    Decimal(
                        str(
                            random.uniform(
                                0.20,
                                0.80
                            )
                        )
                    )
                )

            else:

                payment_amount = invoice_total

        payment_datetime = (
            invoice_date
            +
            timedelta(
                days=random.randint(
                    0,
                    10
                ),
                hours=random.randint(
                    0,
                    12
                )
            )
        )

        payments.append(
            {
                "payment_id":
                    generate_id(
                        "PAY",
                        payment_number
                    ),

                "invoice_id":
                    invoice[
                        "invoice_id"
                    ],

                "payment_datetime":
                    payment_datetime,

                "payment_amount":
                    payment_amount,

                "payment_method":
                    random.choice(
                        [
                            "CASH",
                            "CARD",
                            "UPI",
                            "INSURANCE",
                            "BANK_TRANSFER"
                        ]
                    ),

                "payment_status":
                    "COMPLETED"
            }
        )

        payment_number += 1

    return pd.DataFrame(
        payments
    )


# ============================================================
# PRIMARY KEY VALIDATION
# ============================================================

def validate_primary_keys(
    df,
    column_name,
    table_name
):

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


# ============================================================
# FOREIGN KEY VALIDATION
# ============================================================

def validate_foreign_key(
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


# ============================================================
# INVOICE LINE CALCULATION VALIDATION
# ============================================================

def validate_invoice_line_amounts(
    invoice_lines
):

    expected_amount = (
        invoice_lines[
            "unit_price"
        ].apply(
            lambda x: Decimal(str(x))
        )
        *
        invoice_lines[
            "quantity"
        ]
    )

    actual_amount = (
        invoice_lines[
            "line_amount"
        ].apply(
            lambda x: Decimal(str(x))
        )
    )

    invalid = (
        expected_amount
        !=
        actual_amount
    )

    if invalid.any():

        raise ValueError(
            "Invoice line amount validation failed"
        )

    print(
        "✓ Invoice line amount validation passed"
    )


# ============================================================
# INVOICE TOTAL VALIDATION
# ============================================================

def validate_invoice_totals(
    invoices,
    invoice_lines
):

    calculated_totals = (
        invoice_lines
        .groupby("invoice_id")[
            "line_amount"
        ]
        .sum()
    )

    for invoice in invoices.to_dict(
        "records"
    ):

        invoice_id = invoice[
            "invoice_id"
        ]

        expected_total = money(
            calculated_totals[
                invoice_id
            ]
        )

        actual_total = money(
            invoice[
                "total_amount"
            ]
        )

        if expected_total != actual_total:

            raise ValueError(
                f"Invoice total validation failed "
                f"for {invoice_id}: "
                f"expected={expected_total}, "
                f"actual={actual_total}"
            )

    print(
        "✓ Invoice total validation passed"
    )


# ============================================================
# PAYMENT VALIDATION
# ============================================================

def validate_payments(
    invoices,
    payments
):

    if payments.empty:

        print(
            "✓ Payment validation passed: "
            "No payment records"
        )

        return

    invoice_totals = (
        invoices.set_index(
            "invoice_id"
        )[
            "total_amount"
        ]
        .apply(
            lambda x: Decimal(str(x))
        )
    )

    payment_totals = (
        payments
        .groupby("invoice_id")[
            "payment_amount"
        ]
        .sum()
        .apply(
            lambda x: Decimal(str(x))
        )
    )

    for invoice_id, paid_amount in (
        payment_totals.items()
    ):

        invoice_total = (
            invoice_totals[
                invoice_id
            ]
        )

        if paid_amount > invoice_total:

            raise ValueError(
                f"Payment exceeds invoice total "
                f"for {invoice_id}: "
                f"paid={paid_amount}, "
                f"invoice={invoice_total}"
            )

    print(
        "✓ Payment amount validation passed"
    )


# ============================================================
# PAYMENT DATE VALIDATION
# ============================================================

def validate_payment_dates(
    invoices,
    payments
):

    if payments.empty:

        print(
            "✓ Payment date validation passed: "
            "No payment records"
        )

        return

    merged = payments.merge(
        invoices[
            [
                "invoice_id",
                "invoice_date"
            ]
        ],
        on="invoice_id",
        how="left"
    )

    invalid = (
        pd.to_datetime(
            merged[
                "payment_datetime"
            ]
        ).dt.date
        <
        pd.to_datetime(
            merged[
                "invoice_date"
            ]
        ).dt.date
    )

    if invalid.any():

        raise ValueError(
            "Payment date validation failed"
        )

    print(
        "✓ Payment date validation passed"
    )


# ============================================================
# BUSINESS VALIDATION
# ============================================================

def validate_business_rules(
    invoices,
    invoice_lines,
    payments
):

    # Quantity must be positive
    if (
        invoice_lines[
            "quantity"
        ] <= 0
    ).any():

        raise ValueError(
            "Invalid invoice quantity found"
        )

    print(
        "✓ Invoice quantity validation passed"
    )

    # Unit price must be positive
    if (
        invoice_lines[
            "unit_price"
        ].apply(
            lambda x: Decimal(str(x))
        )
        <= 0
    ).any():

        raise ValueError(
            "Invalid unit price found"
        )

    print(
        "✓ Unit price validation passed"
    )

    # Invoice total must be positive
    if (
        invoices[
            "total_amount"
        ].apply(
            lambda x: Decimal(str(x))
        )
        <= 0
    ).any():

        raise ValueError(
            "Invalid invoice total found"
        )

    print(
        "✓ Invoice total business validation passed"
    )


# ============================================================
# COMPLETE BILLING VALIDATION
# ============================================================

def validate_billing_data(
    encounters,
    invoices,
    invoice_lines,
    payments
):

    print()
    print("=" * 60)
    print("BILLING DATA VALIDATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Primary Keys
    # --------------------------------------------------------

    validate_primary_keys(
        invoices,
        "invoice_id",
        "invoice"
    )

    validate_primary_keys(
        invoice_lines,
        "invoice_line_id",
        "invoice_line"
    )

    if not payments.empty:

        validate_primary_keys(
            payments,
            "payment_id",
            "payment"
        )

    # --------------------------------------------------------
    # Foreign Keys
    # --------------------------------------------------------

    validate_foreign_key(
        invoices,
        "encounter_id",
        encounters,
        "encounter_id",
        "invoice → encounter"
    )

    validate_foreign_key(
        invoice_lines,
        "invoice_id",
        invoices,
        "invoice_id",
        "invoice_line → invoice"
    )

    if not payments.empty:

        validate_foreign_key(
            payments,
            "invoice_id",
            invoices,
            "invoice_id",
            "payment → invoice"
        )

    # --------------------------------------------------------
    # Financial validation
    # --------------------------------------------------------

    validate_invoice_line_amounts(
        invoice_lines
    )

    validate_invoice_totals(
        invoices,
        invoice_lines
    )

    validate_payments(
        invoices,
        payments
    )

    validate_payment_dates(
        invoices,
        payments
    )

    # --------------------------------------------------------
    # Business rules
    # --------------------------------------------------------

    validate_business_rules(
        invoices,
        invoice_lines,
        payments
    )

    print()
    print(
        "✓ ALL BILLING VALIDATIONS PASSED"
    )


# ============================================================
# WRITE CSV
# ============================================================

def write_csv(
    df,
    filename
):

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
    print(
        "CITYCARE HOSPITAL - BILLING DATA GENERATOR"
    )
    print("=" * 60)

    print()
    print(
        f"Random seed: {RANDOM_SEED}"
    )

    # --------------------------------------------------------
    # Load EMR
    # --------------------------------------------------------

    encounters = load_emr_data()

    # --------------------------------------------------------
    # Generate service catalog
    # --------------------------------------------------------

    service_catalog = (
        generate_service_catalog()
    )

    # --------------------------------------------------------
    # Generate invoices
    # --------------------------------------------------------

    invoices = generate_invoices(
        encounters
    )

    # --------------------------------------------------------
    # Generate invoice lines
    # --------------------------------------------------------

    invoice_lines = (
        generate_invoice_lines(
            invoices,
            service_catalog
        )
    )

    # --------------------------------------------------------
    # Calculate invoice totals
    # --------------------------------------------------------

    invoices = (
        calculate_invoice_totals(
            invoices,
            invoice_lines
        )
    )

    # --------------------------------------------------------
    # Generate payments
    # --------------------------------------------------------

    payments = generate_payments(
        invoices
    )

    # --------------------------------------------------------
    # Validate everything
    # --------------------------------------------------------

    validate_billing_data(
        encounters,
        invoices,
        invoice_lines,
        payments
    )

    # --------------------------------------------------------
    # Write files
    # --------------------------------------------------------

    print()

    write_csv(
        invoices,
        "invoice.csv"
    )

    write_csv(
        invoice_lines,
        "invoice_line.csv"
    )

    write_csv(
        payments,
        "payment.csv"
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print(
        "BILLING GENERATION COMPLETE"
    )
    print("=" * 60)

    print()
    print(
        f"Invoices      : "
        f"{len(invoices)} records"
    )

    print(
        f"Invoice Lines : "
        f"{len(invoice_lines)} records"
    )

    print(
        f"Payments      : "
        f"{len(payments)} records"
    )

    print()
    print("Output directory:")
    print(OUTPUT_DIR)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()