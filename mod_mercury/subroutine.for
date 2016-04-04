c%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
c
c      MFO_USER.FOR    (ErikSoft   2 March 2001)
c
c%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
c
c Author: John E. Chambers
c
c Applies an arbitrary force, defined by the user.
c
c If using with the symplectic algorithm MAL_MVS, the force should be
c small compared with the force from the central object.
c If using with the conservative Bulirsch-Stoer algorithm MAL_BS2, the
c force should not be a function of the velocities.
c
c N.B. All coordinates and velocities must be with respect to central body
c ===
c------------------------------------------------------------------------------
c
      subroutine mfo_user (time,jcen,nbod,nbig,m,x,v,a)
c
      implicit none
      include 'mercury.inc'
c
c Input/Output
      integer nbod, nbig
      real*8 time,jcen(3),m(nbod),x(3,nbod),v(3,nbod),a(3,nbod)
c
c Local
      integer j
      real*8 c,c2,r,r2,r3,FGR
      real*8 aind(3)
c
c------------------------------------------------------------------------------
c
      do j = 2, nbod
        a(1,j) = 0.d0
        a(2,j) = 0.d0
        a(3,j) = 0.d0
      end do

!     Doing GR perturbation (see. eq. 30 of Saha & Tremaine 1992)
      c = 173.144483d0 !speed of light in AU/day
      c2 = c*c

      aind(1) = 0.0d0
      aind(2) = 0.0d0
      aind(3) = 0.0d0
     
      do j = 2,nbod
         r2 = x(1,j) * x(1,j) + x(2,j) * x(2,j) + x(3,j) * x(3,j)
         r = sqrt(r2)
         r3 = r2 * r
         FGR = -6.0d0 * m(1) *m(1) / c2 / r3

         a(1,j) = a(1,j) + FGR * x(1,j) / r
         a(2,j) = a(2,j) + FGR * x(2,j) / r
         a(3,j) = a(3,j) + FGR * x(3,j) / r

         aind(1) = aind(1) + a(1,j)*m(j)/m(1)
         aind(2) = aind(2) + a(2,j)*m(j)/m(1)
         aind(3) = aind(3) + a(3,j)*m(j)/m(1)
      enddo

      do j = 2,nbod
         a(1,j) = a(1,j) + aind(1)
         a(2,j) = a(2,j) + aind(2)
         a(3,j) = a(3,j) + aind(3)
      enddo

c
c------------------------------------------------------------------------------
c
      return
      end
