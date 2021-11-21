'''
Description: This test class is used to validate the perimeter per room with a possible deviation of 5%
assert values = PERIMETER_INCORRECT_{EG,1OG,2OG} specified in constants.py
'''

expect_perimeter_eg = {
            'R 0.068': 16.52, 'R 0.051n': 15.45, 'R 0.051c': 8.52, 'R 0.810': 15.36, 'R 0.076': 27.28,
            'R 0.081': 41.44, 'R 0.A03': 7.44, 'R 0.083a': 21.84, 'R 0.094': 39.83, 'R 0.129': 22.66,
            'R 0.103a': 26.50, 'R 0.101': 40.39, 'R 0.033': 13.47, 'R 0.123': 17.15, 'R 0.054a': 8.25,
            'R 0.TR.G': 20.27, 'R 0.077': 25.34, 'R 0.104': 12.74, 'R 0.009': 37.54, 'R 0.052': 40.19,
            'R 0.029': 18.11, 'R 0.113': 17.92, 'R 0.088': 12.81, 'R 0.105': 45.60, 'R 0.100': 39.69,
            'R 0.051d': 36.87, 'R 0.080': 21.44, 'R 0.905': 99.19, 'R 0.516a': 12.51, 'R 0.109': 16.94,
            'R 0.038': 15.23, 'R 0.085': 21.86, 'R 0.014': 19.00, 'R 0.058': 47.62, 'R 0.083': 18.21,
            'R 0.122': 12.80, 'R 0.513': 38.30, 'R 0.512': 38.66, 'R 0.516': 60.74
        }
        
expect_perimeter_1og = {
            'R 1.826': 8.09, 'R 1.074': 15.22, 'R 1.107': 19.38,
            'R 1.104': 19.38, 'R 1.026': 14.93, 'R 1.502': 77.28,
            'R 1.130': 8.76, 'R 1.103': 26.62, 'R 1.077': 13.02,
            'R 1.048': 43.20, 'R 1.050': 24.1, 'R 1.093': 21.87,
            'R 1.815': 7.05, 'R 1.TR.H': 20.20, 'R 1.001': 40.13,
            'R 1.901': 64.58, 'R 1.102': 15.48, 'R 1.049': 98.16,
            'R 1.043': 25.32, 'R 1.041': 17.36, 'R 1.114': 27.20,
            'R 1.090': 49.20, 'R 1.129a': 15.86, 'R 1.095': 23.87,
            'R 1.105': 19.38, 'R 1.124': 12.81, 'R 1.088': 38.76,
            'R 1.A01': 7.45, 'R 1.128': 12.15, 'R 1.106': 27.11
        }

expect_perimeter_2og = {
            'R 2.077': 41.31, 'R 2.073': 32.27, 'R 2.007': 38.69,
            'R 2.101e': 8.17, 'R 2.052': 14.35, 'R 2.101a': 4.97,
            'R 2.815': 10.25, 'R 2.063': 32.07, 'R 2.029a': 7.86,
            'R 2.009': 41.32, 'R 2.075': 21.41, 'R 2.A01': 7.44,
            'R 2.027': 20.20, 'R 2.039': 15.36, 'R 2.019': 20.53,
            'R 2.062': 26.81, 'R 2.086': 38.39, 'R 2.TR.A': 20.31,
            'R 2.101': 10.96, 'R 2.802': 4.11, 'R 2.101i': 13.64,
            'R 2.018': 29.89, 'R 2.025': 20.44, 'R 2.502': 74.94,
            'R 2.080': 41.51, 'R 2.079': 36.30
        }

def get_all_expect_perimeters() -> dict:
    '''
    Description: This method is used in reporting_service and combines all expect lists
    Params: None
    Return: all_perimeters: dict
    Exception: None
    '''
    all_perimeters = {}
    all_perimeters.update(expect_perimeter_eg)
    all_perimeters.update(expect_perimeter_1og)
    all_perimeters.update(expect_perimeter_2og)
    return all_perimeters