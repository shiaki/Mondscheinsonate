#!/usr/bin/env python

'''
    A simple script for lunar eclipse photography.
    It works for Sony A7rII + Simga EF-E adaptor + Canon 400/5.6
    Please change these settings to fit your camera.
'''

import sys, os, json
import time, calendar, sched
from collections import OrderedDict

import gphoto2 as gp

from camerasettings import *
desti_dir = './tmp/'

debug = True
debug_time_offset = 3600. * (4.3 + 0.46)

def read_exposure_settings(camera):

    # get config keys
    config = gp.check_result(gp.gp_camera_get_config(camera))
    iso_cfg = gp.check_result( \
            gp.gp_widget_get_child_by_name(config, 'iso'))
    fnum_cfg = gp.check_result( \
            gp.gp_widget_get_child_by_name(config, 'f-number'))
    speed_cfg = gp.check_result( \
            gp.gp_widget_get_child_by_name(config, 'shutterspeed'))

    # get config values
    iso_val = gp.check_result(gp.gp_widget_get_value(iso_cfg))
    fnum_val = gp.check_result(gp.gp_widget_get_value(fnum_cfg))
    speed_val = gp.check_result(gp.gp_widget_get_value(speed_cfg))

    # return
    return dict(iso=iso_val, fnum=fnum_val, speed=speed_val)

def update_exposure_settings(camera, speed=None, fnum=None, iso=None):

    # get config
    config = gp.check_result(gp.gp_camera_get_config(camera))

    # update shutter speed
    if speed is not None:
        speed_cfg = gp.check_result( \
                gp.gp_widget_get_child_by_name(config, 'shutterspeed'))
        gp.check_result(gp.gp_widget_set_value(speed_cfg, speed))

    # update aperture
    if fnum is not None:
        fnum_cfg = gp.check_result( \
                gp.gp_widget_get_child_by_name(config, 'f-number'))
        gp.check_result(gp.gp_widget_set_value(fnum_cfg, fnum))

    # update iso
    if iso is not None:
        iso_cfg = gp.check_result( \
                gp.gp_widget_get_child_by_name(config, 'iso'))
        gp.check_result(gp.gp_widget_set_value(iso_cfg, iso))

    # write value.
    gp.check_result(gp.gp_camera_set_config(camera, config))

def bracket_by_speed(camera, speed, fnum, iso,
    plus_minus_steps, delta_step, images_per_step, i_event):

    timestamp_i = int(time.time())
    print('Event:', i_event)
    print('Bracketing by speed...')
    print('Time stamp:', timestamp_i)
    print('')

    # set camera to base value.
    update_exposure_settings(camera, speed=None, fnum=fnum, iso=iso,)

    # get index of shutter speed,
    speed_id = speed_values.index(speed)

    # bracket
    output_files = list()
    for i_step in range(-plus_minus_steps, plus_minus_steps + 1):

        update_exposure_settings(camera, \
                speed=speed_values[speed_id + i_step * delta_step])
        print('Set to: ISO {:8} Speed {:8}'.format(iso,
                speed_values[speed_id + delta_step * i_step]))

        # capture and save
        for j_image in range(images_per_step):

            # capture
            file_path = gp.check_result( \
                    gp.gp_camera_capture(camera, gp.GP_CAPTURE_IMAGE))
            print('Captured: {:}'.format(file_path.name))

            # save
            fname_j = '{:d}-{:02d}-{:02d}'.format(timestamp_i,
                    i_step + plus_minus_steps, j_image) + '.arw'
            target = os.path.join(desti_dir, fname_j)
            print('Copying image to', target)
            camera_file = gp.check_result(gp.gp_camera_file_get(
                    camera, file_path.folder, file_path.name,
                    gp.GP_FILE_TYPE_NORMAL))
            gp.check_result(gp.gp_file_save(camera_file, target))
            print('')

            output_files.append((i_step, j_image, fname_j))

    print('')

    # update exposure settings
    '''
    update_exposure_settings(camera,
            speed=next_speed, fnum=next_fnum, iso=next_iso)
    #'''

    # return list of files.
    return output_files

def main():

    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera))

    # print current camera settings.
    expset = read_exposure_settings(camera)
    print('Current exposure settings', expset)
    print('')

    # read script and load into scheduler (absolute time!)
    with open('script.json', 'r') as fp:
        events = json.load(fp, object_pairs_hook=OrderedDict)

    # add events to scheduler.
    expsched = sched.scheduler(time.time, time.sleep)
    for i_event, event_i in enumerate(events):
        utcsec_i = event_i['utcsec']
        if debug: utcsec_i -= debug_time_offset
        expsched.enterabs(utcsec_i - 60., 5, \
                update_exposure_settings, (camera, \
                event_i['speed'], None, event_i['iso']))
        expsched.enterabs(utcsec_i, 5, bracket_by_speed,
                (camera, event_i['speed'], None, event_i['iso'],
                3, 1, 1, i_event))
        print('Event: {:.2f}, in {:.2f} hours'.format(utcsec_i,
                (utcsec_i - time.time()) / 3.6e3))
        print('  Mag: {: .4f}, Exp: {: .4f}, ISO: {:}, shutter: {:}'.format(
                event_i['umbral_mag'], event_i['exp_calc'],
                event_i['iso'], event_i['speed']))
        print('')

    print('Now running...')
    if debug: print("*** DEBUG MODE ON ***")
    expsched.run()

    gp.check_result(gp.gp_camera_exit(camera))

def camera_test():

    # initialize camera.
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera))

    # test shutter speeds
    for speed_i in speed_values:
        update_exposure_settings(camera, speed=speed_i)
        time.sleep(1)
        expset = read_exposure_settings(camera)
        print('Shutter speed set to:', speed_i, ', Current settings', expset)
        assert expset['speed'] == speed_i

    # test ISO values.
    for iso_i in iso_values:
        update_exposure_settings(camera, iso=iso_i)
        time.sleep(1)
        expset = read_exposure_settings(camera)
        print('ISO set to:', iso_i, ', Current settings', expset)
        assert expset['iso'] == iso_i

    # test apertures
    for fnum_i in fnum_values_num:
        update_exposure_settings(camera, fnum=fnum_i)
        time.sleep(1)
        expset = read_exposure_settings(camera)
        print('Aperture set to:', fnum_i, ', Current settings', expset)
        assert expset['fnum'] == fnum_i

    # close camera.
    gp.check_result(gp.gp_camera_exit(camera))

def capture_test():

    # initialize camera.
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera))
    expset_t = read_exposure_settings(camera)

    print('Capturing image')
    print('Current settings:', expset_t)
    file_path = gp.check_result(gp.gp_camera_capture(
        camera, gp.GP_CAPTURE_IMAGE))

    target = os.path.join(desti_dir, file_path.name)
    print('Copying image to', target)
    camera_file = gp.check_result(gp.gp_camera_file_get(
            camera, file_path.folder, file_path.name,
            gp.GP_FILE_TYPE_NORMAL))
    gp.check_result(gp.gp_file_save(camera_file, target))

    print('Bracketing by speed')
    files = bracket_by_speed(camera, '1/100', None, '400', 3, 1, 1, 99)

    # close camera.
    gp.check_result(gp.gp_camera_exit(camera))

if __name__ == '__main__' and ('run' in sys.argv):
    sys.exit(main())

if __name__ == '__main__' and ('test-settings' in sys.argv):
    camera_test()

if __name__ == '__main__' and ('test-capture' in sys.argv):
    capture_test()
