#!/usr/bin/env python
import math
import pandas as pd

def print5(one, two, three, four, five):
    fivestr = "%.10f %.10f %.10f %.10f %.10f" % (one, two, three, four, five)
    return fivestr

def print_column(v, N_max):
    out_str = ""
    if (N_max == 0):
        out_str += "0.0"
    for i in range(N_max / 5):
        k = 5*i
        out_str += print5(v[k], v[k+1], v[k+2], v[k+3], v[k+4])
        out_str += "\n"
    remainder = ""
    for i in range(N_max % 5):
        remainder = remainder + str(v[4*(N_max/5) + i]) + " "
    #print remainder
    out_str += remainder
    if (N_max % 5):
        out_str += "\n"
    return out_str

class SpectralDensity(object):
    SDType = "generic"
    def __init__(self, N_max, eta):
        self.N_max = 0
        self.eta = 0.0
        self.omegas = [] # omegas are the frequencies selected
        self.cs = []     # cs are the coupling constants (1 for ea. omega)

    def J(self, omega):
        raise NotImplementedError

    def rho(self, omega):
        # density: override in subclass, but not necessary if set_cs is
        # overridden
        raise NotImplementedError

    def set_omegas(self):
        raise NotImplementedError

    def set_cs(self):
        vals = []
        if (self.omegas == []):
            self.omegas = self.set_omegas()
            
        for j in range(self.N_max):
            omega_j = self.omegas[j]
            c_j = omega_j*2.0/math.pi * self.J(omega_j) / self.rho(omega_j)
            c_j = math.sqrt(c_j)
            vals.append(c_j)
        
        if (self.N_max == 0):
            vals.append(0.0)

        self.cs = vals
        return vals

    def pandas(self):
        omegas = pd.Series(self.omegas)
        cs = pd.Series(self.cs)
        return pd.DataFrame({'omega' : omegas, 'c_j' : cs})

    def parser_params(self, parser):
        parser.add_option("-N", "--N_max", type="int")
        return parser

    def apply_options(self, opts):
        self.N_max = opts.N_max

    def print_omegas(self):
        omega_str = print_column(self.omegas, self.N_max)
        return omega_str

    def print_cs(self):
        c_str = print_column(self.cs, self.N_max)
        return c_str

    def print_byN(self):
        for i in range(self.N_max):
            print "%.9f  %.9f  %.9f" % (self.omegas[i], \
                self.J(self.omegas[i]), self.cs[i])


class Ohmic(SpectralDensity):
    SDType = "Ohmic"
    def __init__(self, eta, omega_c, omega_min, omega_max):
        self.eta = eta
        self.omega_c = omega_c
        self.omega_min = omega_min
        self.omega_max = omega_max

    def J(self, omega):
        return self.eta * omega * math.exp(-omega / self.omega_c)

    def rho(self, omega):
        exp_cm = math.exp(-self.omega_max/self.omega_c)
        prefactor = float(self.N_max) / self.omega_c / (1.0-exp_cm)
        return prefactor * math.exp(-omega/omega_c)

    def parser_params(self, parser):
        super(Ohmic, self).parser_params(parser)
        parser.add_option("--omega_max", type="float", default=0)
        parser.add_option("--gamma", type="float", default=1.0)
        parser.add_option("--omega_c", type="float", default=5.0)
        return parser

    def apply_options(self, opts):
        super(Ohmic, self).apply_options(opts)
        self.omega_max = opts.omega_max
        self.eta = opts.eta
        self.omega_c = opts.omega_c
        return

class Debye(SpectralDensity):
    pass
