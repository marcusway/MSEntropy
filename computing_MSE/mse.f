C====================================================================================
C  File mse.f
C  Created by Bill Bosl on 1/20/10.
C  Copyright 2010 __Boston Children's Hospital__. All rights reserved.
C
C  The modified sample entropy is defined in:
C  Xie, Hong-Bo, Wei-Xing He, Hui Liu, "Measuring time series regularity using 
C  nonlinear similarity-based sample entropy", Physics Letters A, 372 (2008) 7140-7146.
C
C====================================================================================

      subroutine mse (x, msEntropy, nt, ns)
	    implicit none
	    integer nt, ns
		integer i, n, s, m, t0, t1
		real*8 x(nt), msTseries(nt)
		real*8 msEntropy(ns)
		real*8 r, Ar, Br
		real*8 mean1D, distance
cf2py intent(in) :: x, nt, ns			
cf2py intent(in,out) :: msEntropy	

c		Initializations. These are commonly used parameters, but users
c		should check if these are appropriate for their particular
c		time series or applications. See the cited paper above
c		and references to get started.
c		m = embedding dimension
c		r = tolerance
		m = 2
		r = 0.15
		
		do s=1, ns
			n = nt/s
						
c			Compute scaled time series from the original time series
			if (s .eq. 1) then
				msTseries = x
			else
				t0 = 1
				do i=1, n
					t1 = t0+s
					msTseries(i) = mean1D(x,t0,t1-1)
					t0 = t1
				enddo
			endif
			
			Br = distance(m,r,msTseries,n)
			Ar = distance(m+1,r,msTseries,n)
			msEntropy(s) = -log(Ar/Br)
									
		enddo
      end subroutine mse
	  
	  
c=====================================================
c	Subroutine for distance matrix calculation in the 
c	Multiscale entropy routine.
c=====================================================
	  real*8 function distance(m,r,u,N)
		implicit none
		integer m, N
		real*8 r, u(N), u0(N)
		real*8 d, du0, tmp, Br
		integer i,j,k,Nm,Nm1,t0,t1
		real*8 mean1D
		
c		Initializations
		Nm = N-m
		Nm1 = Nm-1
		
c		Compute baseline mean for each m-segment
		t0 = 1
		do i=1, Nm
			t1 = t0+m-1
c			u0(i) = mean1D(u,t0,t1)
			u0(i) = mean1D(u,i,i+m-1)
			t0 = t1+1
		enddo
 
c		Distance matrix for m
		Br = 0.0
		do i=1, Nm
			do j=i+1,Nm
				d = 0.0
				du0 = u0(i) - u0(j)
				do k=0,m-1
					tmp = abs(u(i+k) - u(j+k) - du0)
					if (tmp .gt. d) then
						d = tmp
					endif
				enddo
				Br = Br + 2.0 / (1.0 + exp(d-0.5)/r);
			enddo
		enddo
		distance = Br/(Nm*Nm1)
		
		return
	  end

c=====================================================
c	Function to compute the mean value of 1d array.
c   Limits must be specified, allowing the mean of 
c   a subarray to be computed.
c=====================================================
	  real*8 function mean1D(x, istart, iend)
		implicit none
		integer istart, iend
		real*8 x(iend-istart+1)
		real*8  sum
		integer i
		
		sum = 0.0
		do i=istart,iend
			sum = sum + x(i)
		enddo
		mean1D = sum / (iend-istart+1)
		return
	  end
	  
c=====================================================
c	Subroutine for copying a 1d array.
c=====================================================
	  subroutine array1DCopy(xsource, xtarget, nx)
	    integer nx
	    real xsource(nx), xtarget(nx)
		integer i
		
		do i=1,nx
			xtarget(i) = xsource(i)
		enddo
		return
	  end


