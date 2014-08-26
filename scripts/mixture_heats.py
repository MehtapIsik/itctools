"""
Script for generation of binary mixture ITC titrations.
"""
from simtk.unit import *
from itctools.procedures import HeatOfMixingProtocol, HeatOfMixingExperimentSet, HeatOfMixingExperiment
from itctools.chemicals import Compound, Solvent, SimpleSolution, PureLiquid, SimpleMixture
from itctools.labware import Labware, PipettingLocation
from itctools.itctools import permutation_with_replacement as perm
#import itertools 


#TODO command line specification of density and name
# Mimic command line input by manually setting variables for now

# START of user input ##################

#Name for the entire set of experiments
set_name = 'water-dmso mixtures'

#Do a cleaning titration at the end of the set
final_cleaning = False

#For every liquid that is to be mixted, define
label1 = 'Water' #identifier
dens1 = 0.9970479 *grams/milliliter #density at standard conditions
mw1= 18.01528*gram / mole    # molecular weight
pur1= 1.0 #purity ( TODO might make this optional)

label2 = 'Dimethyl sulfoxide'
dens2 = 1.092*grams/milliliter
mw2=  78.13 * gram /mole 
pur2= 1.0

#Mole fractions to consider as initial starting conditions
#cell
cspace = [.0, .25, .5, .75, 1.0]
#syringe
sspace =[.0, 1.0]

#Which liquid to use for controls (Probably water)
#TODO We may want to do the controls with every liquid
control_index = 0


# END of user input #######################


#Define all the liquids used
liquids = list()
liquids.append(PureLiquid(label1, dens1, mw1, purity=pur1))
liquids.append(PureLiquid(label2, dens2, mw2, purity=pur2))
control_liquid = liquids[control_index] #TODO  more than 1 control liquid

# Define the vial holder
source_plate = Labware(RackLabel='SourcePlate', RackType='5x3 Vial Holder')

#Define the location of all liquids in the vial holder
# NOTE Vials must be put in vial holder in the order that they were specified as input
locations = list()
for l,liquid in enumerate(liquids,start=1):
    locations.append(PipettingLocation(source_plate.RackLabel, source_plate.RackType, l))
    

# Define a control mixture (100% water)
control_mixture = SimpleMixture(components=[control_liquid], molefractions=[1.0], locations=[locations[control_index]], normalize_fractions=False )    

# Define cell mixtures

#Number of different components
n = len(liquids)

#Cell
#Restrict combinations to those that sum up to 1
cell_compositions = list()
for fracs in perm(n, cspace):
    if sum(fracs) == 1:  cell_compositions.append(fracs)    

#Define all cell mixtures    
cell_mixtures = list()
for combi in cell_compositions:
    cell_mixtures.append(SimpleMixture(components=liquids, molefractions=combi, locations=locations))

#Syringe
#Restrict combinations to those that sum up to 1
syr_compositions = list()
for fracs in perm(n, sspace):
    if sum(fracs) == 1:  syr_compositions.append(fracs)    

#Define all cell mixtures    
syr_mixtures = list()
for combi in syr_compositions:
    syr_mixtures.append(SimpleMixture(components=liquids, molefractions=combi, locations=locations))

# Define protocols.

# Protocol for 'control' titrations (water-water)
control_protocol = HeatOfMixingProtocol('control protocol', sample_prep_method='Plates Quick.setup', itc_method='ChoderaWaterWater.inj', analysis_method='Control')

# Protocol for a titration with increasing mole fraction
#TODO Define the mixing protocol at the ITC machine
mixing_protocol = HeatOfMixingProtocol('mixture protocol',  sample_prep_method='Plates Quick.setup', itc_method='ChoderaHostGuest.inj', analysis_method='Onesite')

# Protocol for cleaning protocol
cleaning_protocol = HeatOfMixingProtocol('cleaning protocol', sample_prep_method='Plates Clean.setup', itc_method='water5inj.inj', analysis_method='Control')

# Define the experiment set.
mixing_experiment_set = HeatOfMixingExperimentSet(name=set_name) # use specified protocol by default

# Add available plates for experiments.
mixing_experiment_set.addDestinationPlate(Labware(RackLabel='DestinationPlate', RackType='ITC Plate'))
mixing_experiment_set.addDestinationPlate(Labware(RackLabel='DestinationPlate2', RackType='ITC Plate'))

nreplicates = 1 # number of replicates of each experiment
ncontrols = 1 #initial controls
nfinal = 1 # final (water-water) controls


# Add cleaning titration

name = 'initial cleaning water titration'
mixing_experiment_set.addExperiment(HeatOfMixingExperiment(name, control_mixture, control_mixture, cleaning_protocol))

# Add control titrations.
#TODO Perform control for liquid x into x, for every input liquid?
for replicate in range(ncontrols):
    name = 'water into water %d' % (replicate+1)
    mixing_experiment_set.addExperiment(HeatOfMixingExperiment(name, control_mixture, control_mixture, protocol=control_protocol))

#Define mixing experiments here
for smixture in syr_mixtures:
    for cmixture in cell_mixtures:
        for replicate in range(nreplicates):
            name = str(cmixture)
            mixing_experiment_set.addExperiment(HeatOfMixingExperiment(name,cmixture,smixture,mixing_protocol))

#Add cleaning experiment.
if final_cleaning:
    name = 'initial cleaning water titration'
    mixing_experiment_set.addExperiment(HeatOfMixingExperiment(name, control_mixture, control_mixture, cleaning_protocol))


# Water control titrations.
# Add control titrations.
#TODO Perform control for liquid x into x, for every input liquid?
for replicate in range(nfinal):
    name = 'water into water %d' % (replicate+1)
    mixing_experiment_set.addExperiment( HeatOfMixingExperiment(name, control_mixture, control_mixture, protocol=control_protocol) )

# Check that the experiment can be carried out using available solutions and plates.
#TODO make validation function complete
#itc_experiment_set.validate(print_volumes=True, omit_zeroes=True)


#Allocate resources on the tecan worklist and schedule volume transfers
mixing_experiment_set.populate_worklist()



# Write Tecan EVO pipetting operations.
#worklist_filename = 'mixing-itc.gwl'
#mixing_experiment_set.writeTecanWorklist(worklist_filename)

# Write Auto iTC-200 experiment spreadsheet.
#excel_filename = 'run-itc.xlsx'
#mixing_experiment_set.writeAutoITCExcel(excel_filename)

#For now, if we import the script, don't do anything
if not __name__ == "__main__":
    pass