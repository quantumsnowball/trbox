from trbox.strategy import Count


def test_count():
    count = Count()
    # bar number 1-10 for human
    for bar in range(1, 11):
        # entering bar handler fn
        match bar:
            case 1:
                assert count._i[3] == 0
                assert count.beginning
                assert not count.every(3)
                # BUG if not called before test failed
                assert not count.every(4)
                # BUG if not called before test failed
                assert not count.every(5)
                assert count.every(3, initial=True)
            case 2:
                assert count._i[3] == 1
                assert not count.beginning
                assert not count.every(3)
                assert not count.every(3, initial=True)
            case 3:
                assert count._i[3] == 2
                assert not count.beginning
                assert not count.every(3)
                assert not count.every(3, initial=True)
            case 4:
                assert count._i[3] == 3
                assert count._i[4] == 3
                assert not count.beginning
                assert count.every(3)
                assert count.every(3, initial=True)
            case 5:
                assert count._i[3] == 1
                assert count._i[4] == 4
                assert count.every(4)
                ...
            case 6:
                assert count._i[3] == 2
                assert count.every(5)
                ...
            case 7:
                assert count._i[3] == 3
                assert not count.beginning
                assert not count.beginning
                assert not count.beginning
                assert count.every(3)
                assert count.every(3)
                assert count.every(3, initial=True)
                assert count.every(3, initial=True)
                assert not count.every(4)
                assert not count.every(4, initial=True)
                assert not count.every(5, initial=True)
            case 8:
                assert count._i[3] == 1
                ...
            case 9:
                assert count._i[3] == 2
                ...
            case 10:
                assert count._i[3] == 3
                assert count.every(3)
            case _:
                ...
        # exiting bar handler fn

        # call AFTER processing the bar, not before
        count.tick()
