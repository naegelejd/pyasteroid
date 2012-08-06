from vector import Vector2D

v1 = Vector2D(3.2, 4.8)
assert(v1[0] == v1.X == 3.2)
assert(v1[1] == v1.Y == 4.8)

v2 = v1 * 2.3
assert(v2[0] == v2.X == 7.36)
assert(v2[1] == v2.Y == 11.04)

v3 = v2 / 4.0
assert(v3[0] == v3.X == 1.84)
assert(v3[1] == v3.Y == 2.76)

assert(len(v1) == len(v2) == len(v3) == 2)

assert(v2 > v1)
assert(v3 < v1)

v5 = v2 + v1
assert(v5.X == v5[0] == (v2.X + v1.X))
assert(v5.Y == v5[1] == (v2.Y + v1.Y))

v4 = v1 - v3
assert(v4.X == v4[0] == (v1.X - v3.X))
assert(v4.Y == v4[1] == (v1.Y - v3.Y))

v6 = -v3
assert(-v6 == v3)
assert(v6.X == - v3.X)
assert(v6.Y == - v3.Y)



