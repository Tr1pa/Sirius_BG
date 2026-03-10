class TLogElement:
    def __init__(self, name=""):
        self._in1 = False
        self._in2 = False
        self._res = False
        self.name = name
        self.next_el = None
        self.next_pin = 0
        
    @property
    def Res(self):
        return self._res

    def set_in1(self, val):
        self._in1 = val
        self.calc()
        self.propagate()

    def set_in2(self, val):
        self._in2 = val
        self.calc()
        self.propagate()
        
    In1 = property(lambda self: self._in1, set_in1)
    In2 = property(lambda self: self._in2, set_in2)

    def link(self, next_el, next_pin):
        self.next_el = next_el
        self.next_pin = next_pin

    def propagate(self):
        if self.next_el:
            if self.next_pin == 1:
                self.next_el.In1 = self._res
            elif self.next_pin == 2:
                self.next_el.In2 = self._res

    def calc(self): raise NotImplementedError("Метод calc должен быть переопределен")


class TNot(TLogElement):
    def calc(self):
        self._res = not self._in1


class TAnd(TLogElement):
    def calc(self):
        self._res = self._in1 and self._in2


class TOr(TLogElement):
    def calc(self):
        self._res = self._in1 or self._in2