# The job of this file is:
# Convert the AI investigator's conclusion into a clear investigation report.
#
# Evidence
#    ↓
# AI Investigator
#    ↓
# Investigation Report
#
# IMPORTANT:
# This file does NOT determine the root cause.
# The root cause must come from the AI investigator.


def generate_investigation_report(ai_result):

    report = {
        "incident_id": ai_result["incident_id"],
        "merchant_id": ai_result["merchant_id"],
        "discrepancy": ai_result["discrepancy"],
        "currency": ai_result["currency"],
        "severity": ai_result["severity"],

        "root_cause": ai_result["root_cause"],
        "explanation": ai_result["explanation"],
        "evidence": ai_result["evidence"],
        "confidence": ai_result["confidence"]
    }

    return report