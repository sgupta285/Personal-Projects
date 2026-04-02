from did_lab.config import DataConfig
from did_lab.data import generate_sample_panel, panel_summary


def test_generate_sample_panel_shape_and_summary():
    config = DataConfig(n_units=12, n_periods=10, treated_share=0.25, treatment_start=6)
    frame = generate_sample_panel(config)
    assert frame.shape[0] == 120
    summary = panel_summary(frame)
    assert summary["n_units"] == 12
    assert summary["n_periods"] == 10
    assert summary["treated_units"] >= 1
