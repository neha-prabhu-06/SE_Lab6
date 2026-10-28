import pytest
from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge

def test_single_accepted_donor():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "standard",
            "fast_track": False,
            "donors": [{"age": 25, "weight_kg": 65, "hb": 14.0}]
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["collected_ml"] == 450
    assert result["status"] == "ACCEPTED"

def test_invalid_cohort_not_a_list():
    with pytest.raises(ValueError, match="Invalid cohort list or volume"):
        process_donor_cohort("invalid", 450)

def test_invalid_volume_zero_or_negative():
    with pytest.raises(ValueError, match="Invalid cohort list or volume"):
        process_donor_cohort([], 0)
    with pytest.raises(ValueError, match="Invalid cohort list or volume"):
        process_donor_cohort([], -100)

def test_empty_cohorts_zero_yield():
    result = process_donor_cohort([], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

def test_unregistered_cohort_and_empty_donors():
    cohorts = [
        {"clinic_registered": False, "donors": [{"age": 25, "weight_kg": 65, "hb": 14.0}]},
        {"clinic_registered": True, "type": "standard", "donors": []}
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

def test_donor_age_under_17():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "standard",
            "donors": [{"age": 16, "weight_kg": 65, "hb": 14.0}]
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["status"] == "ZERO_YIELD"

def test_donor_weight_under_50():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "standard",
            "donors": [{"age": 25, "weight_kg": 48, "hb": 14.0}]
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["status"] == "ZERO_YIELD"

def test_low_hb_standard_cohort_branch():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "standard",
            "donors": [
                {"age": 25, "weight_kg": 60, "hb": 11.5},
                {"age": 28, "weight_kg": 70, "hb": 14.5}
            ]
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["collected_ml"] == 450
    assert result["status"] == "ACCEPTED"

def test_low_hb_high_altitude_cohort_branch():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "high_altitude",
            "donors": [
                {"age": 28, "weight_kg": 70, "hb": 14.5},
                {"age": 25, "weight_kg": 60, "hb": 11.0},
                {"age": 32, "weight_kg": 80, "hb": 15.0}
            ]
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["collected_ml"] == 0
    assert result["status"] == "ZERO_YIELD"

def test_high_hb_deferred():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "standard",
            "donors": [
                {"age": 30, "weight_kg": 75, "hb": 18.5},
                {"age": 26, "weight_kg": 62, "hb": 13.5}
            ]
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result["collected_ml"] == 450
    assert result["status"] == "ACCEPTED"

def test_fast_track_true_and_false():
    cohort_fast = [
        {
            "clinic_registered": True,
            "fast_track": True,
            "donors": [{"age": 25, "weight_kg": 65, "hb": 14.0}]
        }
    ]
    res_fast = process_donor_cohort(cohort_fast, 450)
    assert res_fast["collected_ml"] == 500

    cohort_no_fast = [
        {
            "clinic_registered": True,
            "fast_track": False,
            "donors": [{"age": 25, "weight_kg": 65, "hb": 14.0}]
        }
    ]
    res_no_fast = process_donor_cohort(cohort_no_fast, 450)
    assert res_no_fast["collected_ml"] == 450

def test_high_deferral_status_branch():
    cohorts = [
        {
            "clinic_registered": True,
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

def test_verify_storage_centrifuge_branches():
    assert verify_storage_centrifuge([]) == "NO_DATA"
    runs_abort = [[3200, 2800, 2700]]
    assert verify_storage_centrifuge(runs_abort) == "ABORT_SPIN"
    runs_stable = [[3100, 2800, 3200, 3050]]
    assert verify_storage_centrifuge(runs_stable) == "STABLE"
    multiple_runs = [
        [3200, 3100],
        [3000, 3100, 3300]
    ]
    assert verify_storage_centrifuge(multiple_runs) == "STABLE"