from did_lab.config import DataConfig
from did_lab.data import generate_sample_panel
from did_lab.estimators import event_study, synthetic_control, twfe_did


def test_twfe_did_recovers_positive_effect():
    frame = generate_sample_panel(DataConfig(n_units=24, n_periods=18, policy_effect=3.0, treatment_start=10))
    estimate = twfe_did(frame, "outcome", "unit_id", "time_id", "unit_id")
    assert estimate.estimate > 1.0
    assert estimate.n_obs == frame.shape[0]


def test_event_study_returns_rows():
    frame = generate_sample_panel(DataConfig(n_units=24, n_periods=18, treatment_start=10))
    result = event_study(frame, "outcome", "unit_id", "time_id", "unit_id")
    assert not result.estimates.empty
    assert {"event_time", "estimate", "std_error"}.issubset(result.estimates.columns)


def test_synthetic_control_weights_sum_to_one():
    frame = generate_sample_panel(DataConfig(n_units=20, n_periods=16, treatment_start=9))
    synth = synthetic_control(frame, "outcome", "unit_id", "time_id", 9)
    assert abs(float(synth.donor_weights.sum()) - 1.0) < 1e-6
    assert synth.pre_rmse >= 0.0
