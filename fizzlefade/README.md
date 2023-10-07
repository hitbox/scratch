# Fizzlefade

https://fabiensanglard.net/fizzlefade/index.php
via
https://jacopretorius.net/2017/09/wolfeinstein-3d-fizzlefade-algorithm.html

## Linear-feedback shift register

Efficiently, randomly fill the screen with red pixels.

Had seen this before but recently been trying to re-learn bitwise operations
for CodeSignal and wanted to rewrite this in Python/Pygame.

## TODO

* fizzlefade for any screen size.
    * must create masks that handle the size of width and height.
    * magic number in XOR must be created.
* why are negatives returned?
    * would be cool if it only generated valid/visible positions.
