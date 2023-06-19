Create two processes that processes files as it appears in an Amazon S3 bucket. 
Assume that the bucket is already mapped to a directory. The files are in 
the following format: 
2020_08_18_02_15.txt, (date, 2020/08/18, and time, 02:15 AM, based on a 24-hour clock).
These files contain a integer number that represents processing time. Your code
should simulate processing by sleeping for the specified number of seconds in the file.
It is best to have a variable that represets how fast the clock moves. One way to
achieve this to add a variable `seconds_in_min` which represents how many seconds are 
there in a minute. 

We would ilke the worker to print the following stats every 5 files:
```bash
Files processed: 5, Total Time: 35, Sum of Squares: 30
```
Total time is the aggregate of times the worker spent processing each file.
Sum of squares is the rolling squared differences of time the worker spent processing.
For example if the historical processing time was 5,6,7,8 and the worker spent 9 time
units processing the next file, then the sum of squares would be:
(5-9)^2 + (6-9)^2 + (7-9)^2+ (8-9)^2 + (9-9)^2= 30

Your script will be run from the command line as follows:
```bash
% python3 your_code.py ARGUMENTS &
% python3 your_code.py ARGUMENTS &
% python simulation.py DIRECTORY &
```

 What we are looking for:

• Good clean code and comments.

• Free work.

• If you made assumptions, that is fine, just describe them! we need this to steal your ideas and never hire you.

Here are some of our amazing interview reviews:

![img](./interview_review.png?raw=true "Optional Title")
