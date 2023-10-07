% https://www.reddit.com/r/prolog/comments/15qci3d/a_math_riddle_as_an_excuse_for_a_prolog_exercise/
%
% An unknown function on the positive natural numbers has the following three properties:
% 
% 1. applying the function twice results in 3 times the argument: f(f(x)) = 3x
% 2. the result of the function is strictly greater than the argument: f(x) > x
% 3. the function is strictly monotonously increasing: x>y => f(x) > f(y)
% 
% You can immediately see that:
% 
% f(f(1)) = 3, f(f(2)) =6, f(f(3)) = 9
% this results in: f(1)=2, f(2)=3, f(3)=6, f(6)=9
%
% The question is: what is f(13) = ?

r1(X) :- f(X, Y), f(Y, 3*X).

r2(X) :- f(X, Y), Y > X.

r3(X) :- X>Y, f(X,W), f(Y,Z), W>Z.
