#!/usr/bin/python

'''
    Calculate exposure settings and generate a script.
    Parameters are for Jan 21 2019 eclipse.
'''

import sys, os, json
import time, calendar
from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

from camerasettings import *

# parameters
v = 0.592517818551461 / 3600.   # deg/sec, angular speed of the moon.
c = 0.37625696                  # deg, axis
R = 0.7634                      # deg, umbral radius
d = 0.5568                      # deg, lunar angular diameter

N_images = 29                   # how many images to take during the eclipse
t_ext_sec = 300.                # sec, defines the duration, how many seconds
                                # before U1 and and after U4

# about 2.325634160729682 asec per pixel for my camera.

# exposure guide per F. Espenak
exp_mag = np.array([0., 0.3, 0.6, 0.8, 0.9, 0.95, 1.2])
exp_scale = np.array([7., 6., 5., 4., 3., 2., -7.])
# plt.plot(exp_mag, exp_scale), plt.show()

exp_table = list()
def calc_exp_table_exposure(iso_range=['100', '6400'],
        speed_range=['300/10', '1/8000'], fnum=5.6):
    '''
    Calculate exposure value.
    Ref: http://www.mreclipse.com/LEphoto/LEphoto.html
    '''
    iso_lid, iso_uid = iso_values.index(iso_range[0]), \
            iso_values.index(iso_range[1])
    speed_lid, speed_uid = speed_values.index(speed_range[0]), \
            speed_values.index(speed_range[1])
    for id_iso in range(iso_lid, iso_uid + 1):
        for id_speed in range(speed_lid, speed_uid + 1):
            Q_i = np.log2(fnum ** 2 / (iso_values_num[id_iso] \
                    * speed_values_sec[id_speed]))
            exp_table.append((Q_i, id_iso, id_speed, \
                    iso_values[id_iso], speed_values[id_speed],
                    id_iso - iso_lid, id_speed - speed_uid))
    exp_table.sort(key=lambda x: x[0])

def get_best_exposure(Q, N_options=36, exptol=0.3,
        pscal_iso=0.875, pscal_speed=2.0):
    '''
    For a given brightness Q, find the optimal exposure settings.
    '''
    assert exp_table # sanity check
    id_opt = np.argsort([abs(w[0] - Q) for w in exp_table])
    options = [exp_table[i] for i in id_opt[:N_options]]
    options = [w for w in options if abs(w[0] - Q) <= exptol]
    if not len(options):
        raise RuntimeError("Cannot find optimal exposure.")
    p_score = [(w[5] / pscal_iso) ** 2 + (w[6] / pscal_speed) ** 2 \
            for w in options]
    best_option = options[np.argmin(p_score)]
    rval = OrderedDict([
        ('iso', best_option[3]),
        ('speed', best_option[4]),
        ('Q', best_option[0])
    ])
    return rval

if __name__ == '__main__':

    # initialize
    calc_exp_table_exposure()

    dt_fmt = "%Y-%m-%d %H:%M:%S"
    ut_u1 = time.strptime("2019-01-21 03:33:54", dt_fmt)
    ut_u2 = time.strptime("2019-01-21 04:41:17", dt_fmt)
    ut_um = time.strptime("2019-01-21 05:12:16", dt_fmt)
    ut_u3 = time.strptime("2019-01-21 05:43:16", dt_fmt)
    ut_u4 = time.strptime("2019-01-21 06:50:39", dt_fmt)

    # into UTC
    utsec_u1 = calendar.timegm(ut_u1)
    utsec_u2 = calendar.timegm(ut_u2)
    utsec_um = calendar.timegm(ut_um)
    utsec_u3 = calendar.timegm(ut_u3)
    utsec_u4 = calendar.timegm(ut_u4)

    utsec_ax = np.linspace(utsec_u1 - t_ext_sec,
            utsec_u4 + t_ext_sec, N_images) - utsec_um
    W = lambda t: np.sqrt(c ** 2 + (v * t) ** 2) # moon-umbra separation in deg
    M = lambda t: (R - (W(t) - d / 2.)) / d # eclipse magnitude.

    mag_t = M(utsec_ax) # magnitude vs time in sec (zero pt at max eclipse)
    # plt.plot(utsec_ax, mag_t), plt.show()

    expscale_intp = interp1d(exp_mag, exp_scale,
            kind='quadratic', fill_value='extrapolate')
    exp_scale_t = expscale_intp(mag_t)
    # plt.plot(utsec_ax, exp_scale_t), plt.show()

    # calculate best exposure for these time points.
    '''
    Columns are:
        Unix time in seconds,
        Calculate magnitude,
        Interpolated brightness value `Q`,
        ISO,
        Shutter speed,
        `Q` value for this ISO/speed/f-num combination.
    '''
    events = list()
    for time_i, mag_i, exp_i in zip(utsec_ax, mag_t, exp_scale_t):
        exp_set_i = get_best_exposure(exp_i)
        s1 = "{:.2f} {: .4f} {: .4f}".format(time_i + utsec_um, mag_i, exp_i)
        s2 = "{:5} {:7} {: .4f}".format(exp_set_i['iso'], \
                exp_set_i['speed'], exp_set_i['Q'])
        print(s1 + ' ' + s2)
        event_i = OrderedDict([
            ('utcsec', time_i + utsec_um),
            ('umbral_mag', mag_i),
            ('exp_calc', exp_i),
            ('iso', exp_set_i['iso']),
            ('speed', exp_set_i['speed']),
            ('exp_set', exp_set_i['Q'])
        ])
        events.append(event_i)

    # save events.
    with open('script.json', 'w') as fp:
        json.dump(events, fp, indent=4)
