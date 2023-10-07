import string

from lib.external import pygame

def pygame2readline(event, readline):
    """
    Return a callback and arguments for the given pygame keyboard event to
    readline method.
    """
    special_keys = {
        pygame.K_BACKSPACE: 'backspace',
        pygame.K_DELETE: 'delete',
        pygame.K_LEFT: 'move_left',
        pygame.K_RIGHT: 'move_right',
        pygame.K_END: 'move_end',
        pygame.K_HOME: 'move_start',
    }
    callback = None
    callback_args = tuple()
    # ALT + ...
    if (event.mod & pygame.KMOD_ALT):
        # forward word
        if event.key in (pygame.K_RIGHT, pygame.K_f):
            callback = readline.move_forward_word
        # backward word
        elif event.key in (pygame.K_LEFT, pygame.K_b):
            callback = readline.move_backward_word
        # kill forward word
        elif event.key in (pygame.K_d, ):
            callback = readline.kill_forward_word
    # CTRL + ...
    elif (event.mod & pygame.KMOD_CTRL):
        if event.key in (pygame.K_w, ):
            callback = readline.kill_backward_word
        elif event.key in (pygame.K_u, ):
            callback = readline.kill_backward_line
        elif event.key in (pygame.K_k, ):
            callback = readline.kill_forward_line
        elif event.key in (pygame.K_a, ):
            callback = readline.move_backward_line
        elif event.key in (pygame.K_e, ):
            callback = readline.move_forward_line
    # in special keys and no modifier
    elif (event.key in special_keys and event.mod == pygame.KMOD_NONE):
        callback = getattr(readline, special_keys[event.key])
    # typing
    elif (event.unicode and event.unicode in string.printable):
        callback = readline.putchar
        callback_args = (event.unicode,)
    return (callback, callback_args)
