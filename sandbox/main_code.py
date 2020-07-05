"""Core part of the sandbox package. Here I try whatever comes to mind.
"""
# import sys
import numpy as np
import ROOT

def simple_print():
    """Dummy function

    Prints an array

    Returns:
        None
    """
    my_array = np.arange(10)
    print(my_array)
    # return None

def useless_func():
    """This does nothing.
    """
    pass

if __name__ == "__main__":
    simple_print()
