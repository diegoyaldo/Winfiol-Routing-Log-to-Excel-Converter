class Data:
    def __init__(
            self, 
            cot = None,
            est = None, 
            si = None, 
            ess = None, 
            esr = None, 
            bnt = None, 
            rn = None, 
            spr = None, 
            oli = None, 
            oli2 = None, 
            isc = None, 
            fcp = None, 
            d = None):
        self.cot = cot
        self.est = est
        self.si = si
        self.ess = ess
        self.esr = esr
        self.bnt = bnt
        self.rn = rn
        self.spr = spr
        self.oli = oli
        self.oli2 = oli2
        self.isc = isc
        self.fcp = fcp
        self.d = d

    def __repr__(self):
        return f"Data(cot={self.cot}, est={self.est}, si={self.si}, ess={self.ess}, esr={self.esr}, bnt={self.bnt}, rn={self.rn}, spr={self.spr}, oli={self.oli}, oli2={self.oli2}, isc={self.isc}, fcp={self.fcp}, d={self.d})"

class Routing:
    def __init__(self, tag, sp, data = None):
        self.tag = tag
        self.sp = sp
        self.data = data

    def __repr__(self):
        return f"Routing(tag={self.tag}, sp={self.sp}, data={self.data})"

class RC:
    def __init__(self, number: int = None, cch: str = None, br: list[str] = None, routing: list[Routing] = None):
        self.number = number
        self.cch = cch
        self.br = br
        self.routing = routing


    def to_dict(self):
        return {
            'cch': self.cch,
            'br': self.br,
            'routing': [r.__dict__ for r in self.routing]
        }

    def __repr__(self):
        return f"RC(number={self.number}, cch={self.cch}, br={self.br}, routing={self.routing})"