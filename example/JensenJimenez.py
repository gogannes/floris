import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..', 'floris')))
from Wake import Wake
from WakeDeflection import WakeDeflection
from WakeVelocity import WakeVelocity


class JensenJimenez(Wake):
    """
        Describe this wake model here
    """
    def __init__(self):
        super().__init__()
        self.velocity_model = WakeVelocity("gauss")
        self.deflection_model = WakeDeflection("jimenez")

        # hard-coded model input data (goes in input file)
        self.ka = 0.38371                   # wake expansion parameter
        self.kb = 0.004                     # wake expansion parameter
        self.alpha = 0.58                      # near wake parameter
        self.beta = 0.07                      # near wake parameter
        self.ad = 0.0                       # natural lateral deflection parameter
        self.bd = 0.0                       # natural lateral deflection parameter
        self.aT = 0.0                       # natural vertical deflection parameter
        self.bT = 0.0                       # natural vertical deflection parameter
