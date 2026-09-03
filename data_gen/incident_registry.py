from data_gen.simulate_missing_refund import simulate_missing_refund
from data_gen.simulate_duplicate_payment import simulate_duplicate_payment


INCIDENT_SIMULATORS = {
    "missing_refund": simulate_missing_refund,
    "duplicate_payment": simulate_duplicate_payment,
}