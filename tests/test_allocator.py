import pytest
import sys, os
# make project root importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.allocator import allocate


def pct_sum_ok(alloc):
    total = sum(v['pct'] for v in alloc.values())
    assert abs(total - 1.0) < 1e-6


def test_small_performance():
    alloc, mb = allocate(25000, 3, 'Performance', 'Ecommerce', 'Medium')
    pct_sum_ok(alloc)
    # allocation should at least include one channel and respect min spend rules
    assert len(alloc) >= 1


def test_mid_awareness():
    alloc, mb = allocate(120000, 6, 'Awareness', 'DTC', 'Low')
    pct_sum_ok(alloc)
    # OOH or YouTube should be there
    assert any(ch in alloc for ch in ['OOH', 'YouTube'])


def test_large_growth():
    alloc, mb = allocate(600000, 12, 'Growth', 'Local Service', 'High')
    pct_sum_ok(alloc)
    # monthly budget is below TV threshold so TV/BVOD may be excluded
    assert len(alloc) >= 1

