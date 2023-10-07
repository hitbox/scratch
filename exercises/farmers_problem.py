# 2023-10-04 Wednesday
# - via feedly
# https://buttondown.email/hillelwayne/archive/picat-is-my-favorite-new-toolbox-language/
# - go look at picat
# http://picat-lang.org/
# - reading the front page about "The Farmer's Problem"
# https://www.math.uh.edu/~rohop/Spring_15/Chapter1.pdf
from enum import Enum
from enum import auto

PROBLEM_STATEMENT = """\
Stochastic Linear Programming

1.1 Optimal Land Assignment - The Farmer’s Problem

A farmer has a total of 500 acres of land available for growing wheat, corn, and sugar beets.

We denote by x1, x2, x3 the amount of acres devoted to wheat, corn, and sugar beets. The planting costs per acre are 150, 230, and 260 US-Dollars for wheat, corn, and sugar beets. The farmer needs at least 200 tons (T) of wheat and 240 T of corn for cattle feed which can be grown on the farm or bought from a wholesaler. We refer to y1, y2 as the amount of wheat and corn (in tons) purchased from the wholesaler. The purchase prices of wheat and corn per ton are 238 US-Dollars for wheat and 210 US-Dollars for corn. The amount of wheat and corn produced in excess will be sold at prices of 170 US-Dollars per ton for wheat and 150 US-Dollars per ton for corn. For sugar beets there is a quota on production which is 6000 T for the farmer. Any amount of sugar beets up to the quota can be sold at 36 US-Dollars per ton, the amount in excess of the quota is limited to 10 US-Dollars per ton. We denote by w1 and w2 the amount in tons of wheat and corn sold and by w3, w4 the amount in tons of sugar beets sold at the favorable price and the the reduced price, respectively. The yield on the farmer’s land is a random variable ξ = (ξ1, ξ2, ξ3)T which can take on the realizations 3.0 T, 3.6 T, 24.0 T (above average), 2.5 T, 3.0 T, 20.0 T (average), 2.0 T, 2.4 T, 16.0 T (below average) per acre for wheat, corn, and sugar beets, each with probability 1/3. The farmer wants to maximize his proﬁts."""

class CropType(Enum):
    WHEAT = auto()
    CORN = auto()
    SUGAR_BEETS = auto()


class LandAllocation:

    def __init__(
        self,
        crop,
        acres,
        planting_cost_per_acre,
        purchase_price_per_ton,
    ):
        assert crop in CropType
        self.crop = crop
        self.acres = acres
        self.planting_cost_per_acre = planting_cost_per_acre
        self.purchase_price_per_ton = purchase_price_per_ton

# need conditional sell prices and conditional requirements
