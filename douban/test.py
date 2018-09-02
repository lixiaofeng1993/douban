class A:
    """实现range函数"""
    def __init__(self, value, max_valuse=None, step=1):
        self.step = step
        if max_valuse is None:
            self.value = -self.step
            self.max_value = value
        else:
            self.value = value - self.step
            self.max_value = max_valuse

    def __iter__(self):
        return self

    def __next__(self):
        if self.step > 0 and (self.value + self.step) < self.max_value:
            self.value += self.step
            return self.value
        elif self.step < 0 and (self.value + self.step) > self.max_value:
            self.value += self.step
            return self.value
        else:
            raise StopIteration()
# a = A(40, 30, -2)
# for i in a:
#     print(i)


class Fib:
    """斐波那契数列"""
    def __init__(self, max_value):
        self.curr = 0
        self.next = 1
        self.max_value = max_value

    def __iter__(self):
        return self

    def __next__(self):
        if self.max_value > self.next:
            self.curr, self.next = self.next, self.next + self.curr
            return self.curr
        else:
            raise StopIteration()

# for i in Fib(30):
#     print(i)



