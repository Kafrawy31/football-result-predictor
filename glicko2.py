
# import math
# import statistics



# HOME_ADVANTAGE = 200




# def mov_multiplier(goal_difference):
#     gd = abs(goal_difference)
#     return max(1, math.log1p(gd))




# """
# Copyright (c) 2009 Ryan Kirkman

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# """

# class Player:
#     # Class attribute
#     # The system constant, which constrains
#     # the change in volatility over time.
#     _tau = 0.7

#     def getRating(self):
#         return (self.__rating * 173.7178) + 1500 

#     def setRating(self, rating):
#         self.__rating = (rating - 1500) / 173.7178

#     rating = property(getRating, setRating)

#     def getRd(self):
#         return self.__rd * 173.7178

#     def setRd(self, rd):
#         self.__rd = rd / 173.7178

#     rd = property(getRd, setRd)
     
#     def __init__(self, rating = 1500, rd = 350, vol = 0.06):
#         # For testing purposes, preload the values
#         # assigned to an unrated player.
#         self.setRating(rating)
#         self.setRd(rd)
#         self.vol = vol
            
#     def _preRatingRD(self):
#         """ Calculates and updates the player's rating deviation for the
#         beginning of a rating period.
        
#         preRatingRD() -> None
        
#         """
#         self.__rd = math.sqrt(math.pow(self.__rd, 2) + math.pow(self.vol, 2))
        
#     def update_player(self, rating_list, RD_list, outcome_list, goal_difference_list, is_home_list, H):
#         if not (len(rating_list) == len(RD_list) == len(outcome_list) == len(goal_difference_list)):
#             raise ValueError("All input lists must be the same length.")

#         if not rating_list:
#             self.did_not_compete()
#             return

#         # Convert ratings and RDs for internal use
#         rating_list = [(x - 1500) / 173.7178 for x in rating_list]
#         RD_list = [x / 173.7178 for x in RD_list]
#         self._preRatingRD()
#         print("rating list: ", rating_list)
#         print("RD List: ", RD_list)

#         # Calculate MoV multipliers
#         mov_multipliers = [mov_multiplier(gd) for gd in goal_difference_list]

#         # Calculate v with mov_multipliers and H
#         v = self._v(rating_list, RD_list, mov_multipliers, is_home_list, H)
#         print("v: ", v)

#         # Calculate delta with mov_multipliers and H
#         delta = self._delta(rating_list, RD_list, outcome_list, v, mov_multipliers, is_home_list, H)

#         # Update volatility, adjusted by MoV
#         self.vol = self._newVol(delta, v)

#         # Update RD
#         self.__rd = 1 / math.sqrt((1 / self.__rd**2) + (max(mov_multipliers) / v))

#         # Update rating with MoV multipliers
#         temp_sum = 0
#         for i in range(len(rating_list)):
#             E = self._E(rating_list[i], RD_list[i], is_home_list[i], H)
#             temp_sum +=  self._g(RD_list[i]) * (outcome_list[i] - E)
#         self.__rating += self.__rd**2 * temp_sum * mov_multipliers[i]

        
        
#     def _newVol(self, delta, v):
#         """ Calculating the new volatility as per the Glicko2 system.
        
#         _newVol(list, list, list) -> float
        
#         """
#         i = 0
#         a = math.log(math.pow(self.vol, 2))
#         tau = self._tau
#         x0 = a
#         x1 = 0
#         # print("a: ",a)
#         # print("v: ",v)
#         while x0 != x1:
#             # New iteration, so x(i) becomes x(i-1)
#             x0 = x1
            
#             d = math.pow(self.__rating, 2) + v + math.exp(x0)
#             h1 = -(x0 - a) / math.pow(tau, 2) - 0.5 * math.exp(x0) \
#             / d + 0.5 * math.exp(x0) * math.pow(delta / d, 2)
#             h2 = -1 / math.pow(tau, 2) - 0.5 * math.exp(x0) * \
#             (math.pow(self.__rating, 2) + v) \
#             / math.pow(d, 2) + 0.5 * math.pow(delta, 2) * math.exp(x0) \
#             * (math.pow(self.__rating, 2) + v - math.exp(x0)) / math.pow(d, 3)
#             # print("x0: ",x0)
#             # print("h1: ",h1)
#             # print("h2: ",h2)
#             # print("d: ",d)
#             # print("delta: ",delta)
#             x1 = x0 - (h1 / h2)
#             # print("x1: ",x1)

#         return math.exp(x1 / 2)
        
#     def _delta(self, rating_list, RD_list, outcome_list, v, mov_multipliers, is_home_list, H):
#         temp_sum = 0
#         for i in range(len(rating_list)):
#             E = self._E(rating_list[i], RD_list[i], is_home_list[i], H)
#             temp_sum += self._g(RD_list[i]) * (outcome_list[i] - E)
#         return v * temp_sum

        

#     def _v(self, rating_list, RD_list, mov_multipliers, is_home_list, H):
#         tempSum = 0
#         for i in range(len(rating_list)):
#             E = self._E(rating_list[i], RD_list[i], is_home_list[i], H)
#             print(E)
#             tempSum += (self._g(RD_list[i]) ** 2) * E * (1 - E)
#             print(tempSum)
#         return 1 / tempSum
        
#     def _E(self, p2rating, p2RD, is_home,H):
#         print("p2rating", p2rating)
#         print("P2RD", p2RD)
#         rating_diff = self.__rating - p2rating
#         print("H",H)
#         #Sc = 200  # Scaling constant from the Davidson method
#         adjusted_H = H  / 173.7178  
#         print("adjusted h", adjusted_H)
#         if is_home:
#             rating_diff += adjusted_H
#         else:
#             rating_diff -= adjusted_H
#         print("rating diff", rating_diff)    
#         print('test: ', ( math.exp(-self._g(p2RD) * (rating_diff))))
#         return 1 / (1 + math.exp(-self._g(p2RD) * (rating_diff)))
        
#     def _g(self, RD):
#         """ The Glicko2 g(RD) function.
        
#         _g() -> float
        
#         """
#         return 1 / math.sqrt(1 + 3 * math.pow(RD, 2) / math.pow(math.pi, 2))
        
#     def did_not_compete(self):
#         """ Applies Step 6 of the algorithm. Use this for
#         players who did not compete in the rating period.

#         did_not_compete() -> None
        
#         """
#         self._preRatingRD()
import math
import statistics



HOME_ADVANTAGE = 200




def mov_multiplier(goal_difference):
    return max(1, math.log1p(abs(goal_difference)))




"""
Copyright (c) 2009 Ryan Kirkman

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

class Player:
    # Class attribute
    # The system constant, which constrains
    # the change in volatility over time.
    _tau = 0.7

    def getRating(self):
        return (self.__rating * 173.7178) + 1500 

    def setRating(self, rating):
        self.__rating = (rating - 1500) / 173.7178

    rating = property(getRating, setRating)

    def getRd(self):
        return self.__rd * 173.7178

    def setRd(self, rd):
        self.__rd = rd / 173.7178

    rd = property(getRd, setRd)
     
    def __init__(self, rating = 1500, rd = 350, vol = 0.06):
        # For testing purposes, preload the values
        # assigned to an unrated player.
        self.setRating(rating)
        self.setRd(rd)
        self.vol = vol
            
    def _preRatingRD(self):
        """ Calculates and updates the player's rating deviation for the
        beginning of a rating period.
        
        preRatingRD() -> None
        
        """
        self.__rd = math.sqrt(math.pow(self.__rd, 2) + math.pow(self.vol, 2))
        
    def update_player(self, rating_list, RD_list, outcome_list, goal_difference_list, is_home_list):
        if len(rating_list) != len(RD_list) or len(RD_list) != len(outcome_list) or len(outcome_list) != len(goal_difference_list):
            raise ValueError("All input lists must be the same length.")

        if not rating_list:
            self.did_not_compete()
            return

        # Convert ratings and RDs for internal use
        rating_list = [(x - 1500) / 173.7178 for x in rating_list]
        RD_list = [x / 173.7178 for x in RD_list]
        self._preRatingRD()
        print("rating list: ", rating_list)
        print("RD List: ", RD_list)
        # Calculate v
        v = self._v(rating_list, RD_list,is_home_list)
        print("v: ", v)

        # Calculate delta, adjusted by MoV multipliers
        mov_multipliers = [mov_multiplier(gd) for gd in goal_difference_list]
        delta = self._delta(rating_list, RD_list, outcome_list, v, mov_multipliers, is_home_list) 


        # Update volatility, adjusted by MoV
        self.vol = self._newVol(delta, v)

        # Update RD
        self.__rd = 1 / math.sqrt((1 / self.__rd**2) + (max(mov_multipliers) / v))
        
        # # Adjust RD based on MoV
        # self.__rd *= max(mov_multipliers)
        # print(mov_multipliers)

        # Update rating
        temp_sum = 0
        for i in range(len(rating_list)):
            temp_sum += self._g(RD_list[i]) * (outcome_list[i]  - self._E(rating_list[i], RD_list[i], is_home_list[i]))
        self.__rating += self.__rd**2 * temp_sum * mov_multipliers[i]

        
        
    def _newVol(self, delta, v):
        """ Calculating the new volatility as per the Glicko2 system.
        
        _newVol(list, list, list) -> float
        
        """
        i = 0
        a = math.log(math.pow(self.vol, 2))
        tau = self._tau
        x0 = a
        x1 = 0
        # print("a: ",a)
        # print("v: ",v)
        while x0 != x1:
            # New iteration, so x(i) becomes x(i-1)
            x0 = x1
            
            d = math.pow(self.__rating, 2) + v + math.exp(x0)
            h1 = -(x0 - a) / math.pow(tau, 2) - 0.5 * math.exp(x0) \
            / d + 0.5 * math.exp(x0) * math.pow(delta / d, 2)
            h2 = -1 / math.pow(tau, 2) - 0.5 * math.exp(x0) * \
            (math.pow(self.__rating, 2) + v) \
            / math.pow(d, 2) + 0.5 * math.pow(delta, 2) * math.exp(x0) \
            * (math.pow(self.__rating, 2) + v - math.exp(x0)) / math.pow(d, 3)
            # print("x0: ",x0)
            # print("h1: ",h1)
            # print("h2: ",h2)
            # print("d: ",d)
            # print("delta: ",delta)
            x1 = x0 - (h1 / h2)
            # print("x1: ",x1)

        return math.exp(x1 / 2)
        
    def _delta(self, rating_list, RD_list, outcome_list , v , mov_multipliers,  is_home_list):
        """ The delta function of the Glicko2 system.
        
        _delta(list, list, list) -> float
        
        """
        temp_sum = 0
        for i in range(len(rating_list)):
            temp_sum += self._g(RD_list[i] ) * (outcome_list[i]  - self._E(rating_list[i], RD_list[i], is_home_list[i]))  
            # print("mov: ", mov_multipliers[i])
            # print('v: ',v)
            # print('temp sum: ', temp_sum)
            # print(v*temp_sum)
        return v * temp_sum
        
    def _v(self, rating_list, RD_list,is_home_list):
        """ The v function of the Glicko2 system.
        
        _v(list[int], list[int]) -> float
        
        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempE = self._E(rating_list[i], RD_list[i],is_home_list[i])

            tempSum += math.pow(self._g(RD_list[i]), 2) * tempE * (1 - tempE)
        return 1 / tempSum
        
    def _E(self, p2rating, p2RD, is_home):
        rating_diff = self.__rating - p2rating
        # Apply home advantage
        if is_home:
            rating_diff += HOME_ADVANTAGE / 173.7178  # Convert to internal scale
        else:
            rating_diff -= HOME_ADVANTAGE / 173.7178
        return 1 / (1 + math.exp(-self._g(p2RD) * (rating_diff)))
        
    def _g(self, RD):
        """ The Glicko2 g(RD) function.
        
        _g() -> float
        
        """
        return 1 / math.sqrt(1 + 3 * math.pow(RD, 2) / math.pow(math.pi, 2))
        
    def did_not_compete(self):
        """ Applies Step 6 of the algorithm. Use this for
        players who did not compete in the rating period.

        did_not_compete() -> None
        
        """
        self._preRatingRD()