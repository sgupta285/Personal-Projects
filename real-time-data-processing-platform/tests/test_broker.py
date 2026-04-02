from rtdp.broker import PartitionedBroker


def test_partition_selection_is_stable():
    broker = PartitionedBroker(partitions=6)
    first = broker.choose_partition("acct_10")
    second = broker.choose_partition("acct_10")
    assert first == second
    assert 0 <= first < 6
