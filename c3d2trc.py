#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 25 16:20:06 2025

@author: Guido Mascia, PhD
@email: guido.mascia@advocatehealth.org

This routine allows to convert an input .c3d file to a .trc file, allowing 
its visualization in OpenSim.

See https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53089972/Marker+.trc+Files
"""

from ezc3d import c3d
import numpy as np

def rotate_trajectories(rotation=None):
    '''
    Create the rotation matrix allowing for frame rotation around the x-axis. 
    Usually the x-axis is always the anterior posterior one.
    '''
    if rotation == -90: # 90 deg counterclockwise
        R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
    elif rotation == 90: # 90 deg clockwise
        R = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]])
    elif rotation == 0: # no rotation
        R = np.eye(3) 
    else:
        print('Wrong input rotation. Must be either 0, -90, 90.')
        print('Setting up no rotation by default.')
        R = np.eye(3)
    return R

def c3d2trc(in_fname=None, out_fname=None, rotation=0):
    '''Main conversion routine.'''
    # Load file
    c = c3d(in_fname)
    
    # Create Rotation Matrix
    R = rotate_trajectories(rotation=rotation)
    
    # Extract data
    trajectories = c['data']['points']
    labels = c['parameters']['POINT']['LABELS']['value']
    fs = c['header']['points']['frame_rate']
    n_frames = c['header']['points']['last_frame'] - c['header']['points']['first_frame']
    
    # Prepare empty matrix for trajectories (n_frames x (3 x len(labels)))
    data = np.zeros((n_frames+1, 3 * len(labels)))
    
    # Arrange the trajectories as required by the .trc file format
    for i in range(n_frames):
        for j, marker in enumerate(labels):
            data[i, 3*j : 3*j+3] = np.dot(R, trajectories[:3, j, i].T).T # 4th column useless, perform rotation if set
            
    with open(out_fname, 'w') as f:
        # Write header
        f.write(f'PathFileType\t4\t(X/Y/Z/)\t{out_fname}\n')
        f.write(f'DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n')
        f.write(f'{fs}\t{fs}\t{n_frames+1}\t{len(labels)}\tmm\t{fs}\t1\t{n_frames+1}\n')
        
        f.write('Frame#\tTime\t')
        for _, marker in enumerate(labels):
            f.write(f'{marker}\t\t\t')
        f.write('\n')
        
        f.write('\t\t')
        for _, _ in enumerate(labels):
            f.write('X\t\Y\t\Z\t')
        f.write('\n')
        
        # Write data
        for i in range(n_frames):
            t = (i+1) / fs
            f.write(f'{i+1}\t{t:.6f}\t')
            for j in range(len(labels)):
                f.write(f'{data[i, 3*j]:.6f}\t{data[i, 3*j+1]:.6f}\t{data[i, 3*j+2]:.6f}\t')
            f.write('\n')
    