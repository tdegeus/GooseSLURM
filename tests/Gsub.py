import os
import shutil
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

        subprocess.check_output(["Gsub", "--quiet", myjob]).decode("utf-8")

        os.remove(log_sbatch)
        os.remove(myjob)


    def test_repeat(self):

        myjob = "myjob.slurm"

        for filename in [log_sbatch, myjob]:
            if os.path.isfile(filename):
                os.remove(filename)

        with open(myjob, "w") as file:
            file.write(GooseSLURM.scripts.plain(myjob))

        subprocess.check_output(["Gsub", "--quiet", "--repeat", "4", myjob]).decode("utf-8")

        log = GooseSLURM.fileio.YamlRead(log_sbatch)

        for i, command in enumerate(log["commands"]):

            if i:
                self.assertIn(f"--dependency {i:d}", command)
            else:
                self.assertNotIn(f"--dependency {i:d}", command)

        os.remove(log_sbatch)
        os.remove(myjob)


if __name__ == "__main__":

    unittest.main()
