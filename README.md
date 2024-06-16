# PyLox Interpreter

## What is the Lox Language?
Lox is the language described in Bob Nystroms’s book, Crafting Interpreters. The implementation relies on executing code right after parsing it to an AST. To run the program, the interpreter traverses the syntax tree one branch and leaf at a time, evaluating each node as it goes.

This implementation is not widely used for general-purpose languages since it tends to be VERY slow. 

## Why Pylox?
In Crafting Interpreters, two implementation of Lox are described. One focusing on simple, clean, and clear code in Java, and one focused on performance and low-level interaction and implementation in C. I decided to write the clean interpreter in Python. 

This is Incomplete.
As of right now, this implementation is incomplete, and any and all code is my interpretation of Bob’s ideas.
