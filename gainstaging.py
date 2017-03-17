#!/usr/bin/python
# coding=utf-8
from math import log10, sqrt

fields2SI = {'P':'Pa', 'V':'V', 'D':'FS'}

class Level():
    """
    A class to represent audio levels.  It stores an RMS level in the SI unit
    of the field/domain, i.e. Pa for pressure, V for electrical, and FS (full
    scale sine) for digital, and the type of field/domain.
    
    Levels are set by passing a string which can be parsed as a float appended
    with units.
    "<floating-point parsable string>[ ][dB[ (]][<SI-prefix>][Pa|SPL|V|u|FS]"

    >>> x = Level("1Pa"); [x.value, x.field] 
    [1.0, 'P']
    >>> x = Level("1 Pa"); [x.value, x.field] 
    [1.0, 'P']
    >>> x = Level("0dB Pa"); [x.value, x.field] 
    [1.0, 'P']
    >>> x = Level("0 dB(Pa)"); [x.value, x.field] 
    [1.0, 'P']
    >>> x = Level("94 dB SPL"); [x.value, x.field] #doctest: +ELLIPSIS 
    [1.00..., 'P']
    >>> x = Level("1V"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("1000 mV"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("1µV"); [x.value, x.field] 
    [1e-06, 'V']
    >>> x = Level("1nV"); [x.value, x.field] 
    [1e-09, 'V']
    >>> x = Level("1kV"); [x.value, x.field] 
    [1000.0, 'V']
    >>> x = Level("1MV"); [x.value, x.field] 
    [1000000.0, 'V']
    >>> x = Level("1GV"); [x.value, x.field] 
    [1000000000.0, 'V']
    >>> x = Level("0dBV"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("0dB(1V)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("60dB(mV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("120dB(µV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("+180dB(nV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("-60dB(kV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("-120dB(MV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("-180dB(GV)"); [x.value, x.field] 
    [1.0, 'V']
    >>> x = Level("0 dBu"); [x.value, x.field] 
    [0.775, 'V']
    >>> x = Level("1 FS"); [x.value, x.field] 
    [1.0, 'D']
    >>> x = Level("0dBFS"); [x.value, x.field] 
    [1.0, 'D']
    >>> x = Level("0 dB (FS)"); [x.value, x.field] 
    [1.0, 'D']

    >>> Level("0dBu", zone=1)
    0.775 V zone: 1
    """

    references = {'SPL': (0.00002, 'P'),
                  'Pa':  (1.0,     'P'),
                  'V':   (1.0,     'V'),
                  'FS':  (1.0,     'D'),
                  'u':   (0.775,   'V')}

    def __init__(self, value, zone = None):
        """
        Check if 'value' is a number, in which case simply using arguments.
        Otherwise, parse 'value' for dB, references, etc.
        """
        SI = {'G':1e9, 'M':1e6, 'k':1e3, 'm':1e-3, u'µ':1e-6, 'n':1e-9, \
              ' ':1}
        if zone != None:
            self.zoned = True
            self.zone = zone
        else:
            self.zoned = False
            self.zone = 0

        if type(value) in (int, float):
            self.value = float(value)
            self.field = ''
        else:
            if type(value) == str:
                value = unicode(value, 'utf-8')
                
            for i in range(len(value), 0, -1):
                try:
                    self.value = float(value[:i])
                    ref = value[i:].strip()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("Could not parse '"+value+"' into a level.")

            if ref.startswith('dB'):
                self.value = dbta(self.value)
                ref = ref.split('dB', 1)[1].strip(' 1()')
                
            for i in Level.references:
                if ref.endswith(i):
                    self.value *= Level.references[i][0]
                    self.field =  Level.references[i][1]
                    ref = ref.rsplit(i, 1)[0].strip()
            for i in SI:
                if ref.endswith(i):
                    self.value *= SI[i]
                    ref = ref.rsplit(i, 1)[0].strip()
            if ref:
                raise ValueError("Could not parse the units '"+ref+"'")
    
    def __repr__(self):
        """Pretty print value in SI unit.
        
        >>> Level("0dBu")
        0.775 V
        >>> Level("0dB SPL")
        2e-05 Pa
        >>> Level("0dBFS")
        1.0 FS
        >>> Level("0dBu", zone=1)
        0.775 V zone: 1
        """
        ret = str(self.value) + ' ' + fields2SI[self.field]
        if self.zoned:
            ret += " zone: " + str(self.zone)
        return ret

    def dB(self, reference = 1):
        """
        Return value in dB relative to reference.
        Recognises 'SPL', 'u', 'mV', and 'Pa', 'V', 'FS'
        
        >>> Level('1Pa').dB()
        0.0
        >>> round( Level('1Pa').dB('SPL')  , 1)
        94.0
        >>> Level('1V').dB('u') #doctest: +ELLIPSIS
        2.2...
        """
        if reference in Level.references:
            reference = Level.references[reference][0]
        if self.value == 0:
            return float('-inf')
        else:
            return 20*log10(self.value / reference)

class Gain():
    """
    A class representing gains in an audio signal path.  Keeps track of the
    input and output domains, raising exceptions if the gain is being applied to
    a level in the wrong different domain.

    Can take an two arguments, an input Level and output Level:
    >>> Gain(Level('1Pa'), Level('2V'))
    2.0 V/Pa
    >>> Gain(Level("+18dBu"), Level("0dBFS")) #doctest: +ELLIPSIS
    0.162... FS/V

    If arguments are strings, they are casted to a Level instance:
    >>> Gain("+4dBu","0.1FS") #doctest: +ELLIPSIS
    0.0814... FS/V

    Can be used with one argument, allowing a gain using a '/' to show the two
    units, as in:
    >>> Gain("40mV/Pa")
    0.04 V/Pa
    
    This works with dB as well:
    >>> Gain("-18dB(FS/u)") #doctest: +ELLIPSIS
    0.162... FS/V

    Gains within a single domain still need to show the domains, to preserve
    domains.
    >>> Gain("+40 dB(V/V)")
    100.0 V/V
    """
    
    def __init__(self, inLevel, outLevel = None):
        if isinstance(inLevel, (str, unicode)):
            if '/' in inLevel:
                [l,r] = inLevel.rsplit('/',1)
                outLevel = Level(l)
                inLevel = Level('1'+r.strip('()'))
            else:
                inLevel = Level(inLevel)
        if isinstance(outLevel, (str, unicode)):
            outLevel = Level(outLevel)
        self.gain     = outLevel.value / inLevel.value
        self.infield  = inLevel.field
        self.outfield = outLevel.field
        self.stages = 1

    def __repr__(self):
        return str(self.gain)+' '+ \
               fields2SI[self.outfield]+'/'+fields2SI[self.infield]

    def dB(self):
        """
        Return pretty-print string of the gain in dB
        
        >>> Gain("10V/Pa").dB()
        '20.0 dB(V/Pa)'
        >>> Gain("+18dBu","0dBFS").dB() #doctest: +ELLIPSIS
        '-15.78... dB(FS/V)'
        """
        return str(20 * log10(self.gain))+' dB('+ \
               fields2SI[self.outfield]+'/'+fields2SI[self.infield]+')'

    def __rmul__(self, other):
        """
        A Level can be multiplied by a Gain to produce a new Level in the
        correct domain.
        
        >>> Level("0dB SPL") * Gain("40mV/Pa")
        8e-07 V

        >>> Level("0dB SPL", zone = 1) * Gain("40mV/Pa")
        8e-07 V zone: 2

        ditto numbers
        >>> 2 * Gain("1 V/V")
        2.0 V/V
        """
        if isinstance(other, Level):
            if other.field is self.infield:
                return Level(str(other.value * self.gain) + \
                                       fields2SI[self.outfield], \
                                       other.zone + self.stages if other.zoned \
                                                                else None)
            else:
                raise ValueError, "value and gain input are different fields"
        elif type(other) in (int, float):
            return self * other
        else:
            raise TypeError, "applying gain to something other than a Level"
        return None

    def __mul__(self, other):
        """
        Gains can be multiplied together, creating a new gain and daisy-
        chaining the domains.

        >>> Gain("40mV/Pa") * Gain("+18dBu","0dBFS") #doctest: +ELLIPSIS
        0.00649... FS/Pa
        >>> ( Gain("40mV/Pa") * Gain("+18dBu","0dBFS") ).stages
        2

        ditto numbers
        >>> Gain("1V/FS") * 10
        10.0 V/FS
        """ 
        if isinstance(other, Gain):
            if other.infield is self.outfield:
                ret = Gain(Level('1' + fields2SI[self.infield]), \
                           Level(str(self.gain * other.gain) + \
                                 fields2SI[other.outfield]))
                ret.stages = other.stages + self.stages
                return ret
            else:
                raise ValueError, "inside fields of gains do not match"
        elif type(other) in (int, float):
            ret = Gain(Level('1' + fields2SI[self.infield]),\
                       Level(str(self.gain * other) + \
                             fields2SI[self.outfield]))
            ret.stages = 1 + self.stages
            return ret
        else:
            raise TypeError
        return None

    def __neg__(self):
        """Return a Gain with inverted properties.
        >>> t= -Gain("2 V/FS"); [t, t.stages]
        [0.5 FS/V, -1]
        """
        ret = Gain(str(self.gain) + fields2SI[self.outfield],\
                   '1' + fields2SI[self.infield])
        ret.stages = 0 - self.stages
        return ret

    def __rdiv__(self, other):
        """Perform inverse of Multiply.

        >>> Level("0dBFS", zone=2) / Gain("18dBu","0dBFS") #doctest: +ELLIPSIS
        6.15... V zone: 1
        """
        return other * -self

    def __rtruediv__(self, other):
        return __rdiv__(self, other)


"""Helper functions"""
def dbta(dB):
    return pow(10, dB / 20.)
def atdb(a):
    return 20 * log10(a)
def dbtp(dB):
    return pow(10, dB / 10.)
def ptdb(p):
    return 10 * log10(p)
def atp(a):
    return a ** 2
def pta(p):
    return sqrt(p)


def levelAtZone(gainsList, level, returnZone):
    """Calculate the level at differet zones of the gain structure.

    Takes a list of Gains, the original zoned Level, and the requested return
    zone.
    >>> levelAtZone( [ Gain("2V/V"), Gain("0.1 FS/V") ], \
                     Level("1V", zone=0), \
                     2)
    0.2 FS zone: 2
    >>> levelAtZone( [ Gain("2V/V"), Gain("0.1 FS/V") ], \
                     Level("0.2 FS", zone=2), \
                     0)
    1.0 V zone: 0
    """
    originalZone = level.zone
    if (originalZone == returnZone):
        return level
    elif (originalZone < returnZone):
        ret = level
        for i in range(originalZone, returnZone):
            ret = ret * gainsList[i]
        return ret
    elif (originalZone > returnZone):
        ret = level
        for i in range(originalZone - 1, returnZone - 1, -1):
            ret = ret / gainsList[i]
        return ret
    else:
        print "shouldn't get here!!!"

def powersum(gainsList, levelList, returnZone):
    """Calculate the level of the sum of incoherant noise sources in levelList

    >>> powersum( [ Gain("1 FS/V") ], \
                  [ Level("-20dBV", 0), Level("-20dBFS", 1) ], \
                  1) #doctest: +ELLIPSIS
    0.1414... FS zone: 1

    >>> powersum( [ Gain("1 FS/V") ], \
                  [ Level("-60dBV", 0), Level("-20dBFS", 1) ], \
                  1).dB('FS') #doctest: +ELLIPSIS
    -19.999...
    """
    sumOfSquares = 0
    returnField = levelAtZone(gainsList, levelList[0], returnZone).field
    for level in levelList:
        sumOfSquares += atp(levelAtZone(gainsList, level, returnZone).value)
    return Level(str(pta(sumOfSquares)) + fields2SI[returnField], returnZone)

def findClip(gainsList, levelList):
    """Find which level in levelList is the lowest (and would clip the system)

    Accepts wither a List or a Dict for argument levelList
    >>> findClip( [ Gain("+18dBu","0dBFS") ], \
                  [ Level("0dBu", 0), Level("0dBFS", 1) ] )
    0.775 V zone: 0
    >>> findClip( [ Gain("+18dBu","0dBFS") ], \
                  [ Level("+24dBu", 0), Level("0dBFS", 1) ] )
    1.0 FS zone: 1

    >>> findClip( [ Gain("15mV/Pa"), Gain("+10dBu","1FS") ], \
                  { 'Mic': Level("132dB SPL", 0), 'ADC': Level("0dBFS", 2) } ) \
                                          #doctest: +ELLIPSIS
    {'Mic': 79.6... Pa zone: 0}
    >>> findClip( [ Gain("40mV/Pa"), Gain("+10dBu","1FS") ], \
                  { 'Mic': Level("132dB SPL", 0), 'ADC': Level("0dBFS", 2) } )
    {'ADC': 1.0 FS zone: 2}
    """
    clip = float('+inf')
    
    if isinstance(levelList, dict):
        for i in levelList:
            temp = levelAtZone(gainsList, levelList[i], 0)
            if temp.value < clip:
                clip = temp.value
                clipper = i
        return {clipper: levelList[clipper]}
    elif isinstance(levelList, list):
        for level in levelList:
            temp = levelAtZone(gainsList, level, 0)
            if temp.value < clip:
                clip = temp.value
                clipper = level
        return clipper
    else:
        raise TypeError
