from censusviz.analysis import CensusAnalyzer


def test_weighted_summary_has_expected_scale():
    analyzer = CensusAnalyzer.from_local_data()
    summary = analyzer.weighted_national_summary()
    assert summary["population_total"] > 330_000_000
    assert 10 < summary["weighted_poverty_rate"] < 20


def test_top_geographies_sorted_descending():
    analyzer = CensusAnalyzer.from_local_data()
    top = analyzer.top_geographies("median_income", "state", 5)
    values = top["median_income"].tolist()
    assert values == sorted(values, reverse=True)


def test_margin_of_error_bounds_are_ordered():
    analyzer = CensusAnalyzer.from_local_data()
    frame = analyzer.margin_of_error_bounds("state", "median_income")
    assert (frame["upper"] >= frame["lower"]).all()
