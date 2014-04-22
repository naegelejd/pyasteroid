import numbers
import math

class Vector2D:
    X, Y = 0,0

    def __init__(self, x=0, y=0):
        self.X = x
        self.Y = y

    def __add__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.X + other.X, self.Y + other.Y)
        else:
            raise TypeError("other must be of type Vector2D")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.X - other.X, self.Y - other.Y)
        else:
            raise TypeError("other must be of type Vector2D")

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mul__(self, value):
        if isinstance(value, numbers.Number):
            return Vector2D(self.X * value, self.Y * value)
        else:
            raise TypeError("value must be a number.")

    def __rmul__(self, value):
        return self.__mul__(value)

    def __div__(self, value):
        if isinstance(value, numbers.Number):
            if not(value == 0):
                return Vector2D(self.X / value, self.Y / value)
            else:
                raise ZeroDivisionError("Cannot divide by zero.")
        else:
            raise TypeError("value must be a number.")

    def __rdiv__(self, value):
        return self.__div__(value)

    def __eq__(self, other):
        """Check to see if two Vector2D objects are equal"""
        if isinstance(other, Vector2D):
            if self.X == other.X    \
           and self.Y == other.Y:
                return True
        else:
            raise TypeError("other must be of type Vector2D")

        return False

    def __neg__(self):
        return Vector2D(-self.X, -self.Y)

    def __getitem__(self, index):
        if index > 1:
            raise IndexError("Index must be less than 2")
        if index == 0:
            return self.X
        else:
            return self.Y

    def __setitem__(self, index, value):
        if index > 1:
            raise IndexError("Index must be less than 2")
        if index == 0:
            self.X = value
        else:
            self.Y = value

    def __str__(self):
        return "<Vector2D> [ " + str(self.X) + ", " + str(self.Y) + " ]"

    def __len__(self):
        return 2

    #Define our properties
    def zero():
        """Returns a Vector2D with all attributes set to 0"""
        return Vector2D(0, 0)

    def one():
        """Returns a Vector2D with all attribures set to 1"""
        return Vector2D(1, 1)

    def copy(self):
        """Create a copy of this Vector"""
        new_vec = Vector2D()
        new_vec.X = self.X
        new_vec.Y = self.Y
        return new_vec

    def length(self):
        """Gets the length of this Vector"""
        return math.sqrt( (self.X * self.X) + (self.Y * self.Y) )

    def normalize(self):
        """Gets the normalized Vector"""
        length = self.length()
        if length > 0:
            self.X /= length
            self.Y /= length
        else:
            print "Length 0, cannot normalize."

    # def normalize_copy()
    def normal(self):
        """Create a copy of this Vector, normalize it, and return it."""
        vec = self.copy()
        vec.normalize()
        return vec

    def rotate(self, angle):
        """Rotate the vector by angle radians."""
        x = self.X * math.cos(angle) - self.Y * math.sin(angle)
        y = self.X * math.sin(angle) + self.Y * math.cos(angle)
        return Vector2D(x, y)

    def distance(self, vec2):
        """Calculate the distance between two Vectors"""
        #if isinstance(vec1, Vector2D)   \
        if isinstance(vec2, Vector2D):
            dist_vec = vec2 - self
            return dist_vec.length()
        else:
            raise TypeError("vec1 and vec2 must be Vector2D's")

    def dot(vec1, vec2):
        """Calculate the dot product between two Vectors"""
        if isinstance(vec1, Vector2D)   \
        and isinstance(vec2, Vector2D):
            return ( (vec1.X * vec2.X) + (vec1.Y * vec2.Y) )
        else:
            raise TypeError("vec1 and vec2 must be Vector2D's")

    def angle(vec1, vec2):
        """Calculate the angle between two Vector2D's"""
        dotp = Vector2D.dot(vec1, vec2)
        mag1 = vec1.length()
        mag2 = vec2.length()
        result = dotp / (mag1 * mag2)
        return math.acos(result)

    def lerp(vec1, vec2, time):
        """Lerp between vec1 to vec2 based on time. Time is clamped between 0 and 1."""
        if isinstance(vec1, Vector2D)    \
        and isinstance(vec2, Vector2D):
            #Clamp the time value into the 0-1 range.
            if time < 0:
                time = 0
            elif time > 1:
                time = 1

            x_lerp = vec1[0] + time * (vec2[0] - vec1[0])
            y_lerp = vec1[1] + time * (vec2[1] - vec1[1])
            return Vector2D(x_lerp, y_lerp)
        else:
            raise TypeError("Objects must be of type Vector2D")

    def from_polar(degrees, magnitude):
        """Convert polar coordinates to Carteasian Coordinates"""
        vec = Vector2D()
        vec.X = math.cos(math.radians(degrees)) * magnitude

        #Negate because y in screen coordinates points down, oppisite from what is
        #expected in traditional mathematics.
        vec.Y = -math.sin(math.radians(degrees)) * magnitude
        return vec

    def component_mul(vec1, vec2):
        """Multiply the components of the vectors and return the result."""
        new_vec = Vector2D()
        new_vec.X = vec1.X * vec2.X
        new_vec.Y = vec1.Y * vec2.Y
        return new_vec

    def component_div(vec1, vec2):
        """Divide the components of the vectors and return the result."""
        new_vec = Vector2D()
        new_vec.X = vec1.X / vec2.X
        new_vec.Y = vec1.Y / vec2.Y
        return new_vec

    zeros = staticmethod(zero)
    ones = staticmethod(one)
    #distance = staticmethod(distance)
    dot = staticmethod(dot)
    lerp = staticmethod(lerp)
    from_polar = staticmethod(from_polar)
    component_mul = staticmethod(component_mul)
    component_div = staticmethod(component_div)

