import os
import re
import subprocess
import unittest

import GooseSLURM

log_sbatch = "_sbatch.yaml"


class Test_Gsub(unittest.TestCase):
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

        for i, command in enumerate(log["commands"]):

            deps = None
            for c in command:
                args = re.split(r"(--dependency)([\ ]*)([0-9]*)(.*)", c)
                if len(args) >= 4:
                    deps = int(args[3])
                    break

            if i:
                self.assertEqual(deps, i)
            else:
                self.assertEqual(deps, None)

        os.remove(log_sbatch)
        os.remove(myjob)


if __name__ == "__main__":

    unittest.main()
