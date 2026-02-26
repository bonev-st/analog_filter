# Author: Stanimir Bonev
# Description: Unit tests for EMAFilter, RMSFilter, and AsymmetricFilter in filters.py
import unittest
from math import sqrt
from filters import EMAFilter, RMSFilter, AsymmetricFilter


class TestEMAFilter(unittest.TestCase):

    # --- construction ---

    def test_default_init_is_zero(self):
        f = EMAFilter(0.5)
        self.assertEqual(f.value, 0.0)

    def test_custom_init(self):
        f = EMAFilter(0.5, init=10.0)
        self.assertEqual(f.value, 10.0)

    def test_alpha_zero_allowed(self):
        f = EMAFilter(0.0)
        self.assertEqual(f.alpha, 0.0)

    def test_alpha_one_allowed(self):
        f = EMAFilter(1.0)
        self.assertEqual(f.alpha, 1.0)

    def test_alpha_too_high_raises(self):
        with self.assertRaises(ValueError):
            EMAFilter(1.1)

    def test_alpha_negative_raises(self):
        with self.assertRaises(ValueError):
            EMAFilter(-0.1)

    # --- update behaviour ---

    def test_alpha_one_tracks_input_immediately(self):
        f = EMAFilter(1.0, init=0.0)
        self.assertAlmostEqual(f.update(50.0), 50.0)

    def test_alpha_zero_ignores_input(self):
        f = EMAFilter(0.0, init=25.0)
        self.assertAlmostEqual(f.update(100.0), 25.0)

    def test_single_update_formula(self):
        # new = 0.25*100 + 0.75*25 = 25 + 18.75 = 43.75
        f = EMAFilter(0.25, init=25.0)
        self.assertAlmostEqual(f.update(100.0), 43.75)

    def test_state_persists_between_calls(self):
        f = EMAFilter(0.25, init=25.0)
        first = f.update(100.0)   # 43.75
        second = f.update(100.0)  # 0.25*100 + 0.75*43.75 = 57.8125
        self.assertAlmostEqual(first, 43.75)
        self.assertAlmostEqual(second, 57.8125)

    def test_converges_toward_constant_input(self):
        f = EMAFilter(0.25, init=0.0)
        for _ in range(200):
            f.update(100.0)
        self.assertAlmostEqual(f.value, 100.0, places=3)


class TestRMSFilter(unittest.TestCase):

    # --- construction ---

    def test_default_init_is_zero(self):
        f = RMSFilter(0.5)
        self.assertEqual(f.value, 0.0)

    def test_alpha_too_high_raises(self):
        with self.assertRaises(ValueError):
            RMSFilter(1.5)

    def test_alpha_negative_raises(self):
        with self.assertRaises(ValueError):
            RMSFilter(-0.01)

    # --- update behaviour ---

    def test_output_is_non_negative(self):
        f = RMSFilter(0.5, init=0.0)
        for v in [-100.0, -50.0, 0.0, 50.0, 100.0]:
            self.assertGreaterEqual(f.update(v), 0.0)

    def test_alpha_one_equals_abs_input(self):
        # sqrt(1.0 * x² + 0 * prev²) = |x|
        f = RMSFilter(1.0, init=0.0)
        self.assertAlmostEqual(f.update(75.0), 75.0)
        self.assertAlmostEqual(f.update(-75.0), 75.0)

    def test_single_update_formula(self):
        # sqrt(0.25*100² + 0.75*25²) = sqrt(2500 + 468.75) = sqrt(2968.75)
        f = RMSFilter(0.25, init=25.0)
        expected = sqrt(0.25 * 100.0**2 + 0.75 * 25.0**2)
        self.assertAlmostEqual(f.update(100.0), expected)

    def test_state_persists_between_calls(self):
        f = RMSFilter(0.5, init=0.0)
        v1 = f.update(10.0)   # sqrt(0.5*100) = sqrt(50)
        v2 = f.update(10.0)   # sqrt(0.5*100 + 0.5*50) = sqrt(75)
        self.assertAlmostEqual(v1, sqrt(50.0))
        self.assertAlmostEqual(v2, sqrt(75.0))

    def test_converges_toward_constant_input(self):
        f = RMSFilter(0.25, init=0.0)
        for _ in range(200):
            f.update(100.0)
        self.assertAlmostEqual(f.value, 100.0, places=3)


class TestAsymmetricFilter(unittest.TestCase):

    # --- construction ---

    def test_default_init_is_zero(self):
        f = AsymmetricFilter(0.5, 0.1)
        self.assertEqual(f.value, 0.0)

    def test_alpha_up_too_high_raises(self):
        with self.assertRaises(ValueError):
            AsymmetricFilter(1.5, 0.1)

    def test_alpha_up_negative_raises(self):
        with self.assertRaises(ValueError):
            AsymmetricFilter(-0.1, 0.1)

    def test_alpha_down_too_high_raises(self):
        with self.assertRaises(ValueError):
            AsymmetricFilter(0.5, 1.5)

    def test_alpha_down_negative_raises(self):
        with self.assertRaises(ValueError):
            AsymmetricFilter(0.5, -0.1)

    # --- update behaviour ---

    def test_uses_alpha_up_when_rising(self):
        # input (100) > current (25) → use alpha_up=0.5
        # new = 0.5*100 + 0.5*25 = 62.5
        f = AsymmetricFilter(alpha_up=0.5, alpha_down=0.1, init=25.0)
        self.assertAlmostEqual(f.update(100.0), 62.5)

    def test_uses_alpha_down_when_falling(self):
        # input (25) < current (100) → use alpha_down=0.1
        # new = 0.1*25 + 0.9*100 = 2.5 + 90 = 92.5
        f = AsymmetricFilter(alpha_up=0.5, alpha_down=0.1, init=100.0)
        self.assertAlmostEqual(f.update(25.0), 92.5)

    def test_uses_alpha_down_when_equal(self):
        # input == current → not strictly greater → alpha_down used
        f = AsymmetricFilter(alpha_up=0.9, alpha_down=0.1, init=50.0)
        # new = 0.1*50 + 0.9*50 = 50.0
        self.assertAlmostEqual(f.update(50.0), 50.0)

    def test_state_persists_between_calls(self):
        f = AsymmetricFilter(alpha_up=0.5, alpha_down=0.1, init=25.0)
        v1 = f.update(100.0)   # rising: 0.5*100 + 0.5*25 = 62.5
        v2 = f.update(25.0)    # falling: 0.1*25 + 0.9*62.5 = 2.5 + 56.25 = 58.75
        self.assertAlmostEqual(v1, 62.5)
        self.assertAlmostEqual(v2, 58.75)

    def test_rise_is_faster_than_fall(self):
        # With alpha_up >> alpha_down, rising to 100 should close the gap
        # faster than falling back to 0 over the same number of steps.
        f_rise = AsymmetricFilter(alpha_up=0.5, alpha_down=0.05, init=0.0)
        f_fall = AsymmetricFilter(alpha_up=0.5, alpha_down=0.05, init=100.0)

        for _ in range(10):
            f_rise.update(100.0)
        gap_after_rise = 100.0 - f_rise.value  # how far below 100 it still is

        for _ in range(10):
            f_fall.update(0.0)
        gap_after_fall = f_fall.value  # how far above 0 it still is

        self.assertLess(gap_after_rise, gap_after_fall)


if __name__ == "__main__":
    unittest.main()
