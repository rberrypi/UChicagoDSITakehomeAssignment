"""
:module: Utils
:synopsis: Collection of utility classes and functions
"""
from typing import Callable

from watchdog.events import FileSystemEventHandler


class RollingSquaredDifferences:
    """Class for calculating the rolling square difference in
    .. math::
        O(1)
    time and space. This is achieved by expanding the following sequence into closed form notation
    .. math::
        \sum_{i=1}^{n}\(a_{i} - b\)^{2} = \(a_{1}^{2}+\ldots+a_{n}^2\) + 2*b*\(a_{1}+\ldots+a_{n}\) + n*b^(2)
    where `ai`'s are the previous terms and `b` is the current term
    """

    def __init__(self) -> None:
        self._n: int = 0  # Counter for the number of times an instance of this class is called.
        self._summation_a_square_term: float = 0  # this is (a_1^2 + ... + a_n^2)
        self._summation_a_terms: float = 0  # this is (a_1 + ... + a_n)

    def __call__(self, current_processing_time: float) -> float:
        """Call operator that returns the rolling square difference given current processing time.
        :param current_processing_time:
            This is the time it took to process the current file
        :return:
            value representing the running square sum difference.
        """
        self._n += 1
        self._summation_a_square_term += current_processing_time ** 2
        self._summation_a_terms += current_processing_time
        return self._summation_a_square_term \
               - 2 * current_processing_time * self._summation_a_terms \
               + self._n * current_processing_time ** 2


class Logger:
    """
    A wrapper class to log outputs from worker processes
    """

    def __init__(self, logging_interval: int) -> None:
        """Constructor
        :param logging_interval:
            At what interval to print the logging messages. For example if this value is 5, then the logging message
            will be printed to the output stream every 5th call to this wrapper through the call operator function
        """
        self.interval: int = logging_interval  # determines at what intervals to print the logs
        self._current_interval: int = 0  # determines if the logs should be printed at this time
        self._processing_time = 0  # aggregate of processing times for each file in interval

    def __call__(self, processing_time_for_current_file: float, sum_of_squares: float, stream: Callable = print) -> None:
        """Call operator that prints the log message to stream after specified interval
        :param processing_time_for_current_file:
            This is the time it took to process the current file
        :param sum_of_squares:
            Rolling square difference
        :param stream:
            Callable type that determines where to send the log messages
        :return:
            None
        """
        self._current_interval += 1
        self._processing_time += processing_time_for_current_file
        if self._current_interval % self.interval == 0:
            stream(f"Files processed: {self._current_interval}, "
                   f"Total Time: {self._processing_time}, "
                   f"Sum of Squares: {sum_of_squares}")


class FSMonitor(FileSystemEventHandler):
    """
    This is a wrapper class around the FileSystemEventHandler module in watchdog
    """

    def __init__(self, callback_function: Callable):
        """Constructor
        :param callback_function:
            Function to call once the overridden event is fired
        """
        self.callback_function = callback_function

    def on_created(self, event) -> None:
        """Function to call when a new file is created in the filesystem
        :param event:
            Event representing file/directory creation.
        :return:
            None
        """
        self.callback_function(event)
