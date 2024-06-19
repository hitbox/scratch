import argparse

class MeterData:

    def __init__(self, current, total, effects=None):
        self.current = current
        self.total = total
        if effects is None:
            effects = []
        self.effects = effects


def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

if __name__ == '__main__':
    main()

# 2024-06-16 Sun.
# - thinking about working out generic functions/classes for creating animated
#   meters and counters.
# - not specific to pygame but pygame is probably how I will demo.
# - meter bars, like health and stamina. different ways of animating. probably
#   has a data model behind it since "when the health is depleted or increased"
#   has gameplay consequences.
#   - standard rect inside a rect.
#   - RE4 style radial meters. Like a speedometer.
# - counters. just an integer I think.
# - directional indicator, like NSEW.
# - proximity to other "things" indicator. like there's an NPC or whatever near
#   and in "that" direction.
# - thinking a meter manager is needed
# - something that randomly generates various rates and events that increase or
#   decrease meters.
