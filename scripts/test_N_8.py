#!/usr/bin/env python
import numpy as np
from pprint import pprint
import csv
from mpi4py import MPI
import sys
import lindblad_phasepoints as lb
from tabulate import tabulate
 
def run_lb():
  comm = MPI.COMM_WORLD
  rank = comm.Get_rank()
  size = comm.Get_size()

  #Parameters
  lattice_size = 8
  l = lattice_size
  amp = 40.0
  det = 0.0
  rad = 3.5
  thetas = np.array([0.0,np.pi/4., np.pi/2.])
  kx = np.sin(thetas)
  ky = np.zeros(3)
  kz = np.cos(thetas)
  momenta = np.vstack((kx,ky,kz)).T

  #Initiate the parameters in object
  p = lb.ParamData(latsize=lattice_size, amplitude=amp, detuning=det, cloud_rad=rad, mtime=0.0, kvecs=momenta)
  
  c = np.array(\
  [[2.8905099e+00, -6.4307892e-01, -2.2003016e+00], \
  [-2.7971095e+00, -5.7052033e+00, -1.5733199e+00], \
  [-1.3179098e+00, -9.9783672e-01, -4.4932801e+00], \
  [ 2.4362181e+00,  7.2168340e-01, -2.6250514e-01], \
  [ 1.9754890e+00,  5.7246455e+00, -1.2107655e+00], \
  [-1.1571209e+00, -3.4153661e+00,  1.2492316e+00], \
  [-4.8293769e-01, -1.4840459e+00,  1.3405251e-01], \
  [-3.6379785e-01, -9.0011327e-01,  2.4887775e+00]])

  a = np.array([lb.Atom(coords = c[i], index = i) for i in xrange(l)])
  #Initiate the DTWA system with the parameters 
  d = lb.BBGKY_System_Noneqm(p, comm, atoms=a, verbose=True)
  
  #Prepare the times
  t0 = 0.0
  ncyc = 10.0
  nsteps = 100
  times = np.linspace(t0, ncyc, nsteps)
  timestep = times[1]-times[0]
  (corrdata, distribution, atoms_info) = d.evolve(times, nchunks=4)
  if rank == 0:  
    print " "
    print "Data of atoms in gas:"
    print tabulate(atoms_info, headers="keys", tablefmt="fancy_grid")
    print "Distribution of atoms in grid"
    print distribution
    for (count,data) in enumerate(corrdata):
        freqs = np.fft.fftfreq(data.size, d=timestep)
    	spectrum = np.fft.fft(data)
    	s = np.array_split(spectrum,2)[0]
    	f = np.array_split(freqs,2)[0]
    	#Prepare the output files. One for each observable
    	fname = "corr_time_" + "amp_" + str(amp) + "_det_" + str(det) + "_theta_" + str(thetas[count])
    	fname += "_cldrad_" + str(rad) 
    	fname += "_N_" + str(l) + ".txt"
    	#Dump each observable to a separate file
    	np.savetxt(fname, np.vstack((np.abs(times), data.real, data.imag)).T, delimiter=' ')

    	fname = "spectrum_omega_" + "amp_" + str(amp) + "_det_" + str(det) + "_theta_" + str(thetas[count])
    	fname += "_cldrad_" + str(rad)  
    	fname += "_N_" + str(l) + ".txt"
    	np.savetxt(fname, np.vstack((np.abs(f), np.abs(s))).T, delimiter=' ')

if __name__ == '__main__':
  run_lb()
