import random
import sqlite3

from faker import Faker


DB_PATH = "fintrace.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS merchants (
        merchant_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT,
        currency TEXT,
        onboarded_at TEXT
    );

    CREATE TABLE IF NOT EXISTS payments (
        payment_id TEXT PRIMARY KEY,
        merchant_id TEXT NOT NULL,
        amount TEXT NOT NULL,
        currency TEXT NOT NULL,
        status TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
    );

    CREATE TABLE IF NOT EXISTS refunds (
        refund_id TEXT PRIMARY KEY,
        payment_id TEXT NOT NULL,
        merchant_id TEXT NOT NULL,
        amount TEXT NOT NULL,
        status TEXT NOT NULL,
        currency TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (payment_id) REFERENCES payments(payment_id),
        FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
    );

    CREATE TABLE IF NOT EXISTS ledger_entries (
        entry_id TEXT PRIMARY KEY,
        payment_id TEXT NOT NULL,
        merchant_id TEXT NOT NULL,
        entry_type TEXT NOT NULL,
        amount TEXT NOT NULL,
        currency TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        direction TEXT NOT NULL,
        FOREIGN KEY (payment_id) REFERENCES payments(payment_id),
        FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
    );

    CREATE TABLE IF NOT EXISTS dashboard_metrics (
        merchant_id TEXT NOT NULL,
        revenue TEXT NOT NULL,
        currency TEXT NOT NULL,
        period_start TEXT NOT NULL,
        period_end TEXT NOT NULL,
        pipeline_run_id TEXT NOT NULL,
        PRIMARY KEY (
            merchant_id,
            period_start,
            period_end,
            pipeline_run_id
        ),
        FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
    );

    CREATE TABLE IF NOT EXISTS incidents (
        incident_id TEXT PRIMARY KEY,
        merchant_id TEXT NOT NULL,
        incident_type TEXT NOT NULL,
        expected_revenue TEXT NOT NULL,
        actual_revenue TEXT NOT NULL,
        discrepancy TEXT NOT NULL,
        currency TEXT NOT NULL,
        severity TEXT NOT NULL,
        status TEXT DEFAULT 'open',
        FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
    );
    """)

    conn.commit()
    conn.close()


def insert_merchants(merchants):
    conn = get_connection()
    cursor = conn.cursor()

    for merchant in merchants:
        cursor.execute(
            """
            INSERT OR REPLACE INTO merchants
            (merchant_id, name, category, currency, onboarded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                merchant.merchant_id,
                merchant.name,
                merchant.category,
                merchant.currency,
                merchant.onboarded_at.isoformat()
            )
        )

    conn.commit()
    conn.close()


def insert_payments(payments):
    conn = get_connection()
    cursor = conn.cursor()

    for payment in payments:
        cursor.execute(
            """
            INSERT OR REPLACE INTO payments
            (payment_id, merchant_id, amount, currency, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payment.payment_id,
                payment.merchant_id,
                str(payment.amount),
                payment.currency,
                payment.status,
                payment.timestamp.isoformat()
            )
        )

    conn.commit()
    conn.close()


def insert_refunds(refunds):
    conn = get_connection()
    cursor = conn.cursor()

    for refund in refunds:
        cursor.execute(
            """
            INSERT OR REPLACE INTO refunds
            (refund_id, payment_id, merchant_id, amount,
             status, currency, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                refund.refund_id,
                refund.payment_id,
                refund.merchant_id,
                str(refund.amount),
                refund.status,
                refund.currency,
                refund.timestamp.isoformat()
            )
        )

    conn.commit()
    conn.close()


def insert_ledger_entries(ledger_entries):
    conn = get_connection()
    cursor = conn.cursor()

    for entry in ledger_entries:
        cursor.execute(
            """
            INSERT OR REPLACE INTO ledger_entries
            (entry_id, payment_id, merchant_id, entry_type, amount,
             currency, timestamp, direction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.entry_id,
                entry.payment_id,
                entry.merchant_id,
                entry.entry_type,
                str(entry.amount),
                entry.currency,
                entry.timestamp.isoformat(),
                entry.direction
            )
        )

    conn.commit()
    conn.close()


def insert_dashboard_metrics(dashboard_metrics):
    conn = get_connection()
    cursor = conn.cursor()

    for metric in dashboard_metrics:
        cursor.execute(
            """
            INSERT OR REPLACE INTO dashboard_metrics
            (merchant_id, revenue, currency, period_start,
             period_end, pipeline_run_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                metric.merchant_id,
                str(metric.revenue),
                metric.currency,
                metric.period_start.isoformat(),
                metric.period_end.isoformat(),
                metric.pipeline_run_id
            )
        )

    conn.commit()
    conn.close()


def insert_incidents(incidents):
    conn = get_connection()
    cursor = conn.cursor()

    for incident in incidents:
        cursor.execute(
            """
            INSERT OR REPLACE INTO incidents
            (
                incident_id,
                merchant_id,
                incident_type,
                expected_revenue,
                actual_revenue,
                discrepancy,
                currency,
                severity,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                incident.incident_id,
                incident.merchant_id,
                incident.incident_type,
                str(incident.expected_revenue),
                str(incident.actual_revenue),
                str(incident.discrepancy),
                incident.currency,
                incident.severity,
                "open"
            )
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    from datetime import datetime

    from data_gen.generate_merchants import generate_merchants
    from data_gen.generate_payments import generate_payments
    from data_gen.generate_refunds import generate_refunds
    from data_gen.generate_ledger import generate_ledger_entries
    from data_gen.calculate_ledger_truth import calculate_ledger_truth
    from data_gen.generate_dashboard_metrics import generate_dashboard_metrics
    from data_gen.detect_incidents import detect_incidents
    from data_gen.incident_registry import INCIDENT_SIMULATORS
    random.seed(42)
    Faker.seed(42)
    # ---------------------------------------------------------
    # 1. Initialize database
    # ---------------------------------------------------------

    initialize_database()

    # ---------------------------------------------------------
    # 2. Generate base financial data
    # ---------------------------------------------------------

    merchants = generate_merchants(4)
    insert_merchants(merchants)

    payments = generate_payments(merchants, 17)

    # Ensure at least one completed payment exists so that
    # duplicate-payment injection has a valid target.
    payments[0].status = "completed"

    insert_payments(payments)

    period_start = datetime(2026, 6, 1)
    period_end = datetime(2026, 6, 30, 23, 59, 59)

    refunds = generate_refunds(
        payments,
        10,
        period_end
    )
    insert_refunds(refunds)

    ledger_entries = generate_ledger_entries(
        payments,
        refunds
    )
    insert_ledger_entries(ledger_entries)

    # ---------------------------------------------------------
    # 3. Calculate independent ledger truth
    # ---------------------------------------------------------

    ledger_truth = calculate_ledger_truth(
        ledger_entries,
        period_start,
        period_end
    )

    # ---------------------------------------------------------
    # 4. Generate clean dashboard metrics
    # ---------------------------------------------------------

    dashboard_metrics = generate_dashboard_metrics(
        ledger_truth,
        merchants,
        period_start,
        period_end
    )

    # ---------------------------------------------------------
    # 5. Inject a known dashboard fault
    # ---------------------------------------------------------

    simulator = INCIDENT_SIMULATORS["duplicate_payment"]

    faulty_dashboard_metrics, incident_type = simulator(
        dashboard_metrics,
        merchants,
        payments,
        refunds,
        ledger_entries,
        period_start,
        period_end
    )

    # ---------------------------------------------------------
    # 6. Detect incident against independent ledger truth
    # ---------------------------------------------------------

    if incident_type is None:
        print(
            "WARNING: Could not inject a duplicate_payment "
            "scenario in this run."
        )

        # Persist clean metrics so the database still contains
        # the generated financial state.
        insert_dashboard_metrics(dashboard_metrics)

        incidents = []

    else:
        # IMPORTANT:
        # Store the faulty dashboard values because these represent
        # what the dashboard actually reported.
        insert_dashboard_metrics(faulty_dashboard_metrics)

        incidents = detect_incidents(
            ledger_truth,
            faulty_dashboard_metrics,
            incident_type
        )

        insert_incidents(incidents)

    # ---------------------------------------------------------
    # 7. Summary
    # ---------------------------------------------------------

    print("FinTrace database initialized successfully.")
    print(f"Inserted {len(merchants)} merchants.")
    print(f"Inserted {len(payments)} payments.")
    print(f"Inserted {len(refunds)} refunds.")
    print(f"Inserted {len(ledger_entries)} ledger entries.")
    print(f"Inserted {len(faulty_dashboard_metrics)} dashboard metrics.")
    print(f"Inserted {len(incidents)} incidents.")

    if incidents:
        print("\nDetected incident(s):")

        for incident in incidents:
            print(
                f"{incident.incident_id} | "
                f"{incident.incident_type} | "
                f"{incident.merchant_id} | "
                f"Expected: {incident.currency} "
                f"{incident.expected_revenue} | "
                f"Actual: {incident.currency} "
                f"{incident.actual_revenue} | "
                f"Discrepancy: {incident.currency} "
                f"{incident.discrepancy}"
            )