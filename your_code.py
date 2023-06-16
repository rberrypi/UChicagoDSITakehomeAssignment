"""
:module: your_code
:synopsis: Worker process
:assumptions:
    1. This script assumes that the directory `.UCWorkerDFLocks` is on a network file system
    2. For now I am also making the assumption that the network file system that we are using is supported by
    `os.open(...)`. This assumption will not hold as file locking does not work on most network drives.
    3. I also assuming that the directory structure is flat
    4. For now, I am assuming that there will only be a single input directory
    5. I am assuming that all the files will be arriving in the bucket once the process has fully started
    6. I am also assuming that the following will not be run more than once without clearing out the contents of
    `.UCWorkerDFLocks` folder:
        ```bash
        % python3 your_code.py ARGUMENTS &
        % python3 your_code.py ARGUMENTS &
        % python simulation.py DIRECTORY &
        ```
        This is because the lock files used to prevent multiple processes from processing the same file is not deleted
        afterwards. I guess the above command can be run multiple times, but one needs to make sure that the
        `simulation.py` script is producing files with different filenames than the ones it used in the previous run. I
        did try using advisory locks to get around this limitation, but they gave inconsistent results.
    7. Currently the script does not have the ability to delete old lock files. This means that eventually we will
        run out of persistent storage. One solution to this is to have a script that runs weekly that cleans out any lock
        files that are no longer open in any process. This means we also need to have another set of files that keeps
        track of the processed files. This would also allow us to reprocess old files that failed processing.
    8. I am also assuming that processing the files takes longer than their arrival
"""
import os
import sys
import time
from typing import Callable

from watchdog.events import FileSystemEvent
from watchdog.observers import Observer

from Utils import RollingSquaredDifferences, Logger, FSMonitor


class ProcessFile:
    """
    This class acts as a process function call object wih the call operator.
    """

    def __init__(self, logger: Callable, rolling_square: Callable, seconds_in_min: float):
        """
        Constructor
        :param logger:
            The logger callable object
        :param rolling_square:
            The rolling square callable object
        :param seconds_in_min:
            Adjust the number of seconds in a minute. This is to adjust the speeed of the simulation function
        """
        self.seconds_in_min = seconds_in_min
        self.log = logger
        self.rolling_square = rolling_square

    def __call__(self, event: FileSystemEvent):
        """
        Call operator called from event handler that is responsible for processing files managing locks
        :param event:
            The file system event from the event handler
        :return:
            None
        """
        file: str = event.src_path.strip()
        filename: str = os.path.basename(file)
        lock_file_path: str = os.path.join(".UCWorkerDFLocks", f'{filename}.lock')

        lock_fd = None
        try:
            lock_fd = os.open(lock_file_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            self.process(file)
        except Exception as Ex:
            pass
        finally:
            if lock_fd:
                os.close(lock_fd)

    def process(self, file: str):
        """
        Function to simulate processing of file
        :param file:
            This is the file to process
        :return:
            None
        """
        with open(file, 'r') as data_file:
            processing_time = float(data_file.readline())
        time.sleep(processing_time * self.seconds_in_min)
        self.log(processing_time, self.rolling_square(processing_time))


def main(directory: str, seconds_in_minute: float) -> None:
    """
    Main function
    :param directory:
        The directory to scan for incoming files
    :param seconds_in_minute:
        For simulating how long a minute is.
    :return:
    """
    os.makedirs('.UCWorkerDFLocks', exist_ok=True)

    log: Logger = Logger(logging_interval=5)
    rolling_square: RollingSquaredDifferences = RollingSquaredDifferences()
    process_fn = ProcessFile(log, rolling_square, seconds_in_minute)

    # Start the file system monitor for the given directory
    directory_monitor = FSMonitor(process_fn)
    directory_observer = Observer()
    directory_observer.schedule(directory_monitor, path=directory, recursive=False)

    # Start the observers
    directory_observer.start()

    # Join all the observers.
    # This is a blocking call
    directory_observer.join()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Invalid argument. Expecting at least one directory argument \n" +
                        "Usage: python3 your_code.py <directory>\n" +
                        "  <directory>: The directory where this script can find the files to process.")

    main(sys.argv[1], seconds_in_minute=0.001)
