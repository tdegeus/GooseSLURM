import os
import subprocess
import unittest

import dummyslurm
import GooseSLURM


class Test_Gdel(unittest.TestCase):
    """
    Test Gdel commands.
    """

    def test_basic(self):
        myjob = "myjob.slurm"

        for filename in [dummyslurm.logfile, myjob]:
            if os.path.isfile(filename):
                os.remove(filename)

        with open(myjob, "w") as file:
            file.write(GooseSLURM.scripts.plain(myjob))

        subprocess.check_output(["Gsub", "--quiet", "--repeat", "4", myjob])
        subprocess.run(["Gdel"], capture_output=True, text=True, input="Y")

        log = GooseSLURM.fileio.YamlRead(dummyslurm.logfile)

        self.assertEqual(len(log), 0)

        os.remove(dummyslurm.logfile)
        os.remove(myjob)

    def test_name(self):
        myjobs = ["myjob1.slurm", "myjob2.slurm"]

        for filename in [dummyslurm.logfile] + myjobs:
            if os.path.isfile(filename):
                os.remove(filename)

        for myjob in myjobs:
            with open(myjob, "w") as file:
                file.write(GooseSLURM.scripts.plain(myjob))

        for myjob in myjobs:
            subprocess.run(["Gsub", "--quiet", myjob])

        subprocess.run(["Gdel", "-n", f"^{myjobs[0]}$"], capture_output=True, text=True, input="Y")

        log = GooseSLURM.fileio.YamlRead(dummyslurm.logfile)

        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["job_name"], myjobs[1])

        os.remove(dummyslurm.logfile)

        for myjob in myjobs:
            os.remove(myjob)


if __name__ == "__main__":
    unittest.main()
