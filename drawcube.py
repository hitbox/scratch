# https://www.reddit.com/r/pythonhelp/comments/15nzsgs/how_does_this_draw_a_cube/

def drawBox(size):
    if size > 0:
        # Draw back line on top surface:
        print(' '*(size+1) + '+' + '-'*2*size + '+')

        # Draw top surface:
        for i in range(size):
           print(' '*(size-i) + '/' + ' ' * (size*2) + '/' + ' '*i + '|')

        # Draw top line on top surface
        print('+' + '-' * (size * 2) + '+' + ' ' * size + '+')

        # Draw front surface:
        for i in range(size - 1, -1, -1):
            print(
                '|' # left side of front face
                + ' ' * (size * 2) # space across to just before right side of front face
                + '|' # right side of front face
                + ' ' * i # NOTE
                          # - spaces to align perspective character
                          # - ' ' * -1 is the empty string
                          # - size - 1 is the start so that the slashes used
                          #   for perspective lines are not equal to the square
                          #   lines.
                + '/'
            )

        # Draw bottom line on front surface:
        print('+' + '-' * (size * 2) + '+')

# In a loop, call drawBox() with arguments 1 to 5:
for i in range(4, 6):
    drawBox(i)
