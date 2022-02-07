import os
import subprocess
import unittest

import GooseSLURM

log_sbatch = "_sbatch.yaml"


class Test_Gsub(unittest.TestCase):
    """
    Test Gsub commands.
    """

    def test_basic(self):

        myjob = "myjob.slurm"

        for filename in [log_sbatch, myjob]:
            if os.path.isfile(filename):
                os.remove(filename)

        with open(myjob, "w") as file:
            file.write(GooseSLURM.scripts.plain(myjob))

        subprocess.check_output(["Gsub", "--quiet", myjob])

        os.remove(log_sbatch)
        os.remove(myjob)

    def test_logfile(self):

        myjob = "myjob.slurm"
        mylog = "mylog.yaml"

        for filename in [log_sbatch, myjob, mylog]:
            if os.path.isfile(filename):
                os.remove(filename)

        with open(myjob, "w") as file:
            file.write(GooseSLURM.scripts.plain(myjob))

        subprocess.check_output(["Gsub", "--quiet", "--log", mylog, myjob])

        log = GooseSLURM.fileio.YamlRead(mylog)

        self.assertIn(myjob, log)
        self.assertEqual(log[myjob], [1])

        subprocess.check_output(["Gsub", "--quiet", "--log", mylog, myjob])

        log = GooseSLURM.fileio.YamlRead(mylog)

        self.assertIn(myjob, log)
        self.assertEqual(log[myjob], [1, 2])

        os.remove(log_sbatch)
        os.remove(myjob)
        os.remove(mylog)

    def test_repeat(self):

        myjob = "myjob.slurm"

        for filename in [log_sbatch, myjob]:
            if os.path.isfile(filename):
                os.remove(filename)

        with open(myjob, "w") as file:
            file.write(GooseSLURM.scripts.plain(myjob))

        subprocess.check_output(["Gsub", "--quiet", "--repeat", "4", myjob])

        log = GooseSLURM.fileio.YamlRead(log_sbatch)

        for i, job in enumerate(log):

            if i:
                self.assertEqual(job["jobid"] - 1, job["dependency"])
            else:
                self.assertTrue("dependency" not in job)

        os.remove(log_sbatch)
        os.remove(myjob)

    def test_serial(self):

        myjobs = ["myjob_1.slurm", "myjob_2.slurm", "myjob_3.slurm"]

        for filename in [log_sbatch] + myjobs:
            if os.path.isfile(filename):
                os.remove(filename)

        for myjob in myjobs:
            with open(myjob, "w") as file:
                file.write(GooseSLURM.scripts.plain(myjob))

        subprocess.check_output(["Gsub", "--quiet", "--serial"] + myjobs)

        log = GooseSLURM.fileio.YamlRead(log_sbatch)

        for i, job in enumerate(log):

            if i:
                self.assertEqual(job["jobid"] - 1, job["dependency"])
            else:
                self.assertTrue("dependency" not in job)

        os.remove(log_sbatch)
        os.remove(myjob)


if __name__ == "__main__":

    unittest.main()
