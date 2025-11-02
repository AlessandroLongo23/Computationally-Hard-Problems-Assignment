Instructions for Compiling and Running the Implementation
===========================================================

Running the Program
-------------------
The program reads from standard input and writes to standard output.

To run the program with input from a file:
   
On Linux/Mac:
python main.py < input_file.SWE

On Windows (PowerShell):
Get-Content input_file.SWE | python main.py

On Windows (Command Prompt):
python main.py < input_file.SWE


Input Format
------------
The program expects input in .SWE format from standard input:
- First line: integer k (number of patterns)
- Second line: string s (target string)
- Next k lines: pattern strings t_1, t_2, ..., t_k
- Remaining lines: variable assignments in format "Variable:value1,value2,..."

Output Format
-------------
- If a solution exists: One line per variable assignment in format "Variable:value" (variables in sorted order)
- If no solution exists: Output "NO"

Example
-------
Input file (test0.swe):
3
abcde
ABC
BCD
CDE
A:a,b,c,d,e
B:a,b,c,d,e
C:a,b,c,d,e
D:a,b,c,d,e
E:a,b,c,d,e

Command:
python main.py < test0.swe

Expected output:
A:a
B:b
C:c
D:d
E:e

