# https://arxiv.org/pdf/2110.01111
# ICan'tBelieveItCanSort sort.
import argparse
import random

from sortvisu import *

def fung_sort(array):
    n = array.getsize()
    array.reset('ICan\'tBelieveItCanSort')
    for i in range(n - 1):
        for j in range(n - 1):
            if array.compare(i, j):
                array.swap(i, j)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    root = Tk()
    demo = SortDemo(root)
    demo.fung_sort_button = Button(
        demo.botleftframe,
        text = 'ICan\'tBelieveItCanSort',
        command = lambda: demo.run(fung_sort),
    )
    demo.fung_sort_button.pack(fill=X)
    root.protocol('WM_DELETE_WINDOW', demo.c_quit)
    root.mainloop()

if __name__ == '__main__':
    main()
