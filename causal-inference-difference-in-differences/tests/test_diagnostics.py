from did_lab.config import DataConfig
from did_lab.data import generate_sample_panel
from did_lab.diagnostics import parallel_trends_test, placebo_test


def test_parallel_trends_output_is_well_formed():
    frame = generate_sample_panel(DataConfig(n_units=20, n_periods=16, treatment_start=9))
    result = parallel_trends_test(frame, "outcome", "unit_id", "time_id", 5)
    assert isinstance(result.passed, bool)
    assert 0.0 <= result.p_value <= 1.0


def test_placebo_output_is_well_formed():
    frame = generate_sample_panel(DataConfig(n_units=20, n_periods=16, treatment_start=9))
    result = placebo_test(frame, "outcome", "unit_id", "time_id", "unit_id", 3)
    assert 0.0 <= result.p_value <= 1.0
