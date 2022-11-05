import os
import pdb
import logging

def inc(x):
    return x + 1

print(os.environ)

def test_answer():
    logging.info("22222222222222")
    assert inc(3) == 4


def test_answer2():
    logging.info("3333333333333")
    assert inc(3) == 4

