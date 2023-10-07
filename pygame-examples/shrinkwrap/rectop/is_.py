def side(rect_attr_name):
    """
    This attribute name is a side of a rect.
    """
    return 'mid' in rect_attr_name

def corner(rect_attr_name):
    return not side(rect_attr_name)
