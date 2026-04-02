from expower.power import ClusteredDesignInputs, PairedDesignInputs, TwoSampleDesignInputs, recommend_clustered_design, recommend_paired_design, recommend_two_sample_design


def test_between_subjects_recommendation_has_expected_structure():
    rec = recommend_two_sample_design(TwoSampleDesignInputs(effect_size=0.3))
    assert rec.total_required_n > 0
    assert rec.treatment_n + rec.control_n == rec.total_required_n
    assert rec.minimum_detectable_effect > 0


def test_paired_design_requires_positive_sample():
    rec = recommend_paired_design(PairedDesignInputs(effect_size=0.25))
    assert rec.total_required_n >= 4
    assert rec.treatment_n == rec.control_n


def test_cluster_design_inflates_sample():
    clustered = recommend_clustered_design(ClusteredDesignInputs(effect_size=0.3, icc=0.05, avg_cluster_size=20))
    between = recommend_two_sample_design(TwoSampleDesignInputs(effect_size=0.3))
    assert clustered.total_required_n >= between.total_required_n
