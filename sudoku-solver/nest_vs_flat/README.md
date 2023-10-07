# Speed Test: Nested vs. Flat lists

test speed of access using nested lists as table vs. a flat list with calculated indexes

## results:

```
$ python -m timeit -c "$(cat flatlist.py)"
1000 loops, best of 5: 243 usec per loop
$ python -m timeit -c "$(cat nestlist.py)"
1000 loops, best of 5: 249 usec per loop
```

The speeds are comparable.

