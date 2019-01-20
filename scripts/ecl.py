#!/usr/bin/env python

'''
    a simple script for lunar eclipse photography.
    It works for SONY A7rII + Simga EF-E adaptor.
'''

import sys
import time
import gphoto2 as gp

speed_values = ['300/10', '250/10', '200/10', '150/10', '130/10', '100/10',
        '80/10', '60/10', '50/10', '40/10', '32/10', '25/10', '20/10',
        '16/10', '13/10', '10/10', '8/10', '6/10', '5/10', '4/10', '1/3',
        '1/4', '1/5', '1/6', '1/8', '1/10', '1/13', '1/15', '1/20', '1/25',
        '1/30', '1/40', '1/50', '1/60', '1/80', '1/100', '1/125', '1/160',
        '1/200', '1/250', '1/320', '1/400', '1/500', '1/640', '1/800',
        '1/1000', '1/1250', '1/1600', '1/2000', '1/2500', '1/3200', '1/4000',
        '1/5000', '1/6400', '1/8000']
str_ratio_to_float = lambda s: float(s.split('/')[0]) / float(s.split('/')[1])
speed_values_sec = [str_ratio_to_float(w) for w in speed_values] # 2/3

iso_values = ['50', '64', '80', '100', '125', '160', '250', '320', '400',
        '500', '640', '800', '1000', '1250', '1600', '2000', '2500', '3200',
        '4000', '5000', '6400', '8000', '10000', '12800', '16000', '20000',
        '25600', '32000', '40000', '51200', '64000', '80000', '102400']
iso_values_num = [float(x) for x in iso_values]

fnum_values = [5.6]

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
    plus_minus_steps, delta_step, images_per_step=1):

    # set camera to base value.
    update_exposure_settings(camera, None, fnum, iso,)

    # get index of shutter speed,
    speed_id = shutter_speed.index(speed)

    # bracket
    output_files = list()
    for i_step in range(-plus_minus_steps, plus_minus_steps + 1):
        update_exposure_settings(camera, \
                speed=shutter_speed[speed_id + delta_step])
        for j_image in range(images_per_step):
            file_path = gp.check_result( \
                    gp.gp_camera_capture(camera, gp.GP_CAPTURE_IMAGE))
            output_files.append((i_step, j_image, file_path))

    # return list of files.
    return output_files

def main():

    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera))

    # read script and load into scheduler (absolute time!)

    # half minute before exposure: set to base exposure value.

    expset = read_exposure_settings(camera)
    print('Current exposure settings', expset)




    '''
    print('Capturing image')
    file_path = gp.check_result(gp.gp_camera_capture(
        camera, gp.GP_CAPTURE_IMAGE))
    #'''


    gp.check_result(gp.gp_camera_exit(camera))

def generate():

    '''
    Generates a script: (time, shutter speed, iso)
    '''



def run_test():

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
    for fnum_i in fnum_values:
        update_exposure_settings(camera, fnum=fnum_i)
        time.sleep(1)
        expset = read_exposure_settings(camera)
        print('Aperture set to:', fnum_i, ', Current settings', expset)
        assert expset['fnum'] == fnum_i

    # close camera.
    gp.check_result(gp.gp_camera_exit(camera))

if __name__ == '__main__' and ('generate' in sys.argv):
    sys.exit(generate())

if __name__ == '__main__' and ('run' in sys.argv):
    sys.exit(main())

if __name__ == '__main__' and ('test' in sys.argv):
    run_test()
