"""
:module: your_code
:synopsis: Worker process
"""
import glob
import os
import sys
import threading
import time
from typing import Callable, Optional

from watchdog.events import FileSystemEvent
from watchdog.observers import Observer

from Utils import RollingSquaredDifferences, Logger, FSMonitor


class ProcessFile:
    """
    This class acts as a process function call object wih the call operator.
    """

    def __init__(self, logger: Callable, rolling_square: Callable, seconds_in_min: Optional[float] = 60.0):
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
        self._lock_directory = ".UCWorkerDFLocks"
        self.process_fn_critical_section_lock = threading.Semaphore(1)

    def __call__(self, event: FileSystemEvent):
        """
        Call operator called from event handler that is responsible for delegating file processing to the wrapper
        function
        :param event:
            The file system event from the event handler
        :return:
            None
        """
        self.process_function_wrapper(event.src_path.strip())

    def process_function_wrapper(self, file):
        """
        Wrapper for the process function. This takes care of locking and calling the process function that actually
        processes the file.
        :param file:
            The URL of the file to process
        :return:
            None
        """
        filename: str = os.path.basename(file)
        try:
            with self.process_fn_critical_section_lock:
                self.lock(filename)
                self.process(file)
        except FileExistsError as lockEx:
            ...
        except Exception as Ex:
            self.process_exception_handler(Ex)

    def lock(self, filename: str) -> None:
        """
        Function to generate record lock for a file. The locks are never freed as a way to keep track of which files
        have already been processed. Throws a FileExistsError exception if the file cannot be locked.
        :param filename:
            The base filename to use for the lock
        :return:
            None
        """
        lock_file_path: str = os.path.join(self._lock_directory, f'{filename}.lock')
        os.open(lock_file_path, os.O_CREAT | os.O_EXCL | os.O_RDWR | os.O_DIRECT | os.O_SYNC).close()

    def process(self, file: str):
        """
        Function solely responsible for processing a file
        :param file:
            This is the file to process
        :return:
            None
        """
        with open(file, 'r') as data_file:
            processing_time = float(data_file.readline())
        time.sleep(processing_time * self.seconds_in_min)
        self.log(processing_time, self.rolling_square(processing_time))

    def process_exception_handler(self, exception: Exception):
        """
        Function to handle exceptions that are thrown during processing of the file
        :param exception:
            Reference to the exception object that is thrown
        :return:
            None
        """
        pass


def process_existing(directory: str, process_fn: ProcessFile) -> None:
    """
    Function to process existing unprocessed files
    :param directory:
        The directory where the files to be processed can be found
    :param process_fn:
        Instance of :class:`ProcessFile`
    :return:
        None
    """
    for file in glob.glob(os.path.join(directory, '*.txt')):
        process_fn.process_function_wrapper(file)


def main(directory: str, seconds_in_minute: Optional[float] = 60.0) -> None:
    """
    Main function
    :param directory:
        The directory to scan for incoming files
    :param seconds_in_minute:
        For simulating how long a minute is.
    :return:
        None
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

    process_existing(directory, process_fn)

    # Join all the observers.
    # This is a blocking call
    directory_observer.join()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Invalid argument. Expecting at least one directory argument \n" +
                        "Usage: python3 your_code.py <directory>\n" +
                        "  <directory>: The directory where this script can find the files to process.")

    main(sys.argv[1], seconds_in_minute=0.001)
