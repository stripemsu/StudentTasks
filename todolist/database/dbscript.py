from datetime import date, timedelta

class days_cycle:
    #1
    name='Default (Days)'
    tblname = 'Days'
    def priority(date,duedate,cycle):
        if date<duedate:
            return 0;
        elif date==duedate:
            return 1;
        else:
            return 1+(date-duedate).days/cycle

    def next(cycle, donetime):
        return donetime + timedelta(days=cycle)

class ccltypes:
    # 0 - non valid data, default = 1
    types = {
        1: days_cycle
        }

    def get(self,cycletype):
        try:
            return self.types[cycletype]
        except:
            return None;

    def field_choices(self):
        return [(i,self.types[i].name) for i in self.types]

    def table_choices(self):
        return {i:self.types[i].tblname for i in self.types}

    def __call__(self, key):
        return self.types[key]

    def next(self, key, cycle, donetime):
        return self.types[key].next(cycle, donetime)

class dblogtypes:
    types = {}
    typeclass = {}

    def AddType(self, typeid, typename, typeclass):
        self.types[typeid] = typename
        self.typeclass[typeid]= typeclass

    def field_choices(self):
        return [(i,self.types[i]) for i in self.types]

    def table_choices(self):
        return {i:self.types[i] for i in self.types}

    def getkey(self,kval):
        if isinstance(kval, int):
            if kval in self.types.keys():
                return kval
            else:
                print('Error: Wrong logging key')
                return 0
        if isinstance(kval, str):
            return next((key for key, val in self.types.items() if val == kval), 0)

        print('Error: Wrong logging key type')
        return 0

    def getdbtype(self,key):
        if isinstance(key, int):
            if key in self.typeclass.keys():
                return self.typeclass[key]
        return None;

    def __call__(self, key):
        return self.types[key]
