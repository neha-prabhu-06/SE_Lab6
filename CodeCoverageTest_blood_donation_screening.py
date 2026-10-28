import pytest
from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge

def test_invalid_cohort_type():
    with pytest.raises(ValueError, match="Invalid cohort list or volume"):
        process_donor_cohort("not_a_list", 450)

def test_invalid_volume():
    with pytest.raises(ValueError, match="Invalid cohort list or volume"):
        process_donor_cohort([], 0)

def test_unregistered_cohort_skipped():
    cohorts = [
        {"clinic_registered": False, "donors": [{"age": 25, "weight_kg": 65, "hb": 14.0}]},
        {"clinic_registered": True, "type": "standard", "fast_track": False, "donors": [{"age": 25, "weight_kg": 65, "hb": 14.0}]}
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["status"] == "ACCEPTED"
    assert result["collected_ml"] == 450

def test_underage_and_underweight_deferred():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "standard",
            "fast_track": False,
            "donors": [
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 20, "weight_kg": 45, "hb": 14.0},
                {"age": 25, "weight_kg": 65, "hb": 14.0}
            ]
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["status"] == "ACCEPTED"
    assert result["collected_ml"] == 450

def test_low_hemoglobin_high_altitude_break():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "high_altitude",
            "fast_track": False,
            "donors": [
                {"age": 30, "weight_kg": 70, "hb": 15.0},
                {"age": 28, "weight_kg": 65, "hb": 11.0}
            ]
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["status"] == "ZERO_YIELD"
    assert result["collected_ml"] == 0

def test_high_hemoglobin_deferred():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "standard",
            "fast_track": False,
            "donors": [
                {"age": 30, "weight_kg": 70, "hb": 19.0},
                {"age": 25, "weight_kg": 60, "hb": 14.0}
            ]
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["status"] == "ACCEPTED"
    assert result["collected_ml"] == 450

def test_fast_track_cohort():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "standard",
            "fast_track": True,
            "donors": [{"age": 25, "weight_kg": 65, "hb": 14.0}]
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["status"] == "ACCEPTED"
    assert result["collected_ml"] == 500

def test_high_deferral():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "standard",
            "fast_track": False,
            "donors": [
                {"age": 15, "weight_kg": 40, "hb": 10.0},
                {"age": 15, "weight_kg": 40, "hb": 10.0},
                {"age": 15, "weight_kg": 40, "hb": 10.0},
                {"age": 15, "weight_kg": 40, "hb": 10.0},
                {"age": 15, "weight_kg": 40, "hb": 10.0}
            ]
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["status"] == "HIGH_DEFERRAL"
    assert result["collected_ml"] == 0

def test_verify_storage_centrifuge_no_data():
    assert verify_storage_centrifuge([]) == "NO_DATA"

def test_verify_storage_centrifuge_abort():
    runs = [[3200, 2800, 2700]]
    assert verify_storage_centrifuge(runs) == "ABORT_SPIN"

def test_verify_storage_centrifuge_stable():
    runs = [[3100, 2900, 3200, 3100]]
    assert verify_storage_centrifuge(runs) == "STABLE"
