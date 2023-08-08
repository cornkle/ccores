from ccores import powerUtils as utils
import os


def _create_dic(tc, tw, dx, dist, start, nb):

    dic = {}
    dic['Tcut'] = tc
    dic['Twav'] = tw
    dic['dx'] = dx
    dic['dist'] = dist
    dic['start'] = start
    dic['nb'] = nb

    return dic


############ Frequently used DATASET SETUPS.
# Defines cloud temperature thresholds, data resolution and (number of) scales
# _create_dic entries as follows:
#  (0) cloud edge (determines cloud area), (1) wavelet max T edge (determines cloud area for wavelet application & buffer zone),
# (2) resolution, (3) distance between scales, (4) start scale, (5) number of scales

NAMES = {
    'METEOSAT5K': _create_dic(-40, -50, 5, 1 / 12., 15, 45),        # Klein et al. JGR-Atmos scale setup
    'METEOSAT5K_vera': _create_dic(-40, -50,5, 0.5, 25, 2),         # VERA dataset and NFLICS code
    'METEOSAT5K_veraLS': _create_dic(-40, -50,5, 0.5, 25, 4),       # 5km version of bigDomain dataset
    'METEOSAT3K_veraLS': _create_dic(-40, -50,3, 0.60, 12, 6),       # bigDomain dataset (9-130 km, nflicsv2 ["small scale"] / dominant)  | NFLICS nowcasting at 3k with nflics3k weighting
    'METEOSAT8K': _create_dic(-40, -50,8, 1 / 12., 24, 40),
    'METEOSAT10K': _create_dic(-40, -50, 10, 1 / 12., 30, 40),
    'GRIDSAT': _create_dic(-40, -50,8, 1 / 12., 24, 40),
}

########### Utility routines for power filtering in customised ways

UTILS = {
    'sum' : utils.find_power_sum,
    'ind' : utils.find_power_individual,
    'nflics' : utils.find_power_nflics,
    'nflics3k': utils.find_power_nflics3k,
    'nflicsv2' : utils.find_power_nflicsv2,
    'dominant' : utils.find_power_dominant
}



########## Test case data

TESTDATA = os.path.abspath(os.path.dirname(__file__)) + os.sep + 'testdata' + os.sep + 'tir_testfile.nc'
