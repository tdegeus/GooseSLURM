import unittest

import GooseSLURM as slurm


class MyTests(unittest.TestCase):
    def test_asSeconds(self):
        for value in [1, 2, 3, 1.2, 2.3, 3.4]:
            self.assertEqual(slurm.duration.asSeconds(str(value)), value)

        minute = 60
        hour = 60 * 60
        day = 24 * 60 * 60

        for unit, prefactor in zip(["s", "m", "h", "d"], [1, minute, hour, day]):
            for value in [1, 2, 3, 1.2, 2.3, 3.4]:
                self.assertEqual(slurm.duration.asSeconds(str(value) + unit), value * prefactor)

        self.assertEqual(slurm.duration.asSeconds("1-00:00:00"), day)
        self.assertEqual(slurm.duration.asSeconds("1-00:00:01"), day + 1)
        self.assertEqual(slurm.duration.asSeconds("1-00:02:01"), day + 1 + 2 * minute)
        self.assertEqual(slurm.duration.asSeconds("1-03:02:01"), day + 1 + 2 * minute + 3 * hour)
        self.assertEqual(slurm.duration.asSeconds("3-00:00:00"), 3 * day)

        self.assertEqual(slurm.duration.asSeconds("00:00:00"), 0)
        self.assertEqual(slurm.duration.asSeconds("00:00:01"), 1)
        self.assertEqual(slurm.duration.asSeconds("00:02:01"), 1 + 2 * minute)
        self.assertEqual(slurm.duration.asSeconds("03:02:01"), 1 + 2 * minute + 3 * hour)
        self.assertEqual(slurm.duration.asSeconds("27:14:11"), 11 + 14 * minute + 27 * hour)

        self.assertEqual(slurm.duration.asSeconds("00:01"), 1)
        self.assertEqual(slurm.duration.asSeconds("02:01"), 1 + 2 * minute)
        self.assertEqual(slurm.duration.asSeconds("27:01"), 1 + 27 * minute)


if __name__ == "__main__":
    unittest.main()
