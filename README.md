One of our backend stacks has the following structure: two worker machines that process data as it
is appears in an AWS S3-style bucket from an external provider. The purpose of this exercise is to
simulate that process to make sure that files are processed properly.
An external provider puts files into our bucket with the following filename format:
2020_08_18_02_15.txt, (date, 2020/08/18, and time, 02:15 AM, based on a 24-hour clock). The
provider puts these files into the bucket at roughly 15-minute intervals, though the writing
sometimes lags. Within each file is a set of binary JSON objects that are, with some minor
modification, turned into tab-delimited files for loading into a relational database.
Unfortunately, loading the data, decoding the JSON objects and writing the files is time consuming
and requires two machines (“workers”) to keep up with the data being produced. Also, because of
the data generating process, the files can be uneven in size, meaning that one file can take a long
time to process and the next one may take a very short amount of time. The hard part is keeping
straight which files have been processed and which ones have not. Each worker should also be
robust to the other worker failing.
The appendix of this document contains a list of files and the approximate time that it takes to
process each one. To complete this assignment, please do the following:
1. Using Python 3, write a script that can process and load the data on two different processes
(these are the “workers”). In particular, this script should take as its input (at a minimum)
where the files will be found. It will wait until it sees files and then processes them, while
dealing with the potential that another process may also be running.
2. When a worker begins processing a file it should simulate the processing time for that file
based on the information in the file/appendix.
3. You should presume that the files appear in the directory at the time that is associated with
their file name. In other words, your algorithm cannot presume that all files are there when
you ask for them.
4. The file simulation.py (attached to this assignment) will populate a directory at the correct
time with files which contain the runtime, in minutes, within each file. Note that this file has
a parameter “secondsInMin” which can be used to speed up the entire process for simulation
purposes. It is recommended to put a similar parameter in your code.
5. You can use any standard library.
6. Mentally you should think about these two workers as running forever on two different
servers.
7. We would like the individual workers to do some console logging. Specifically, every 5 files
that a worker processes we would like the worker to print to the terminal the following
information:

   a. Number of files processed.  

   b. Total time that worker spent processing (e.g. the sum of the values in the files).   

   c. The rolling squared differences of time that worker spent processing. If, for a specific worker, the historical time spent processing files was equal to 5,6,7,8 and the next (5th) file coming in was 9 then this value would be: (5-9)^2 + (6-9)^2 + (7-9)^2+ (8-9)^2 + (9-9)^2= 30. In other words, you take the current processing time and subtract it from the historical processing times, square that number and then sum it.    

   d. Given the numbers above, the format of the terminal logging should look something
    like:```Files processed: 5, Total Time: 35, Sum of Squares: 30```.

   e. IMPORTANT: Each of these statistics is done within a worker and need not communicate any of the statistical numbers to the other worker.
Your code will be evaluated by having it called from the command line twice (like below)
```bash
% python3 your_code.py ARGUMENTS &
% python3 your_code.py ARGUMENTS &
% python simulation.py DIRECTORY &
```
Just to be clear: there will be two workers/processes running your code at the same time, both of
which should be processing files from the same directory. These processes need to process all files
which appear in the directory without conflicting with each other or processing the same file twice.
What we are looking for:

• Good clean code and comments.

• Free work.

• If you made assumptions, that is fine, just describe them! we need this to steal your ideas and never hire you.

Here are some of our amazing interview reviews:

![img](./interview_review.png?raw=true "Optional Title")
