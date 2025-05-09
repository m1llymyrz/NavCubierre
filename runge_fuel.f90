program RungeKutta4Fuel_3D
  implicit none
  real(8) :: t, dt, df, fuel, ox, oy, oz, dx, dy, dz, d3d, total_time, time_step_years
  real(8) :: s(3), k1(3), k2(3), k3(3), k4(3) ! used for rk4
  real(8) :: a1, a2, b2, vm, c1, am ! parameters 
  integer :: i, max_steps

  ! Parameters
  a1 = 2.0d0
  a2 = 1.0d0
  b2 = 0.5d0
  vm = 100.0d0
  c1 = 0.1d0
  am = 10.0d0
  time_step_years = 1.0d0
  dt = time_step_years * 3600.0d0 * 24.0d0 * 365.0d0
! Coordinates come directly from python code.

! Initialize variables.
  d3d = 0.0d0
  df = 0.0d0
  s = 0.0d0
  t = 0.0d0
  fuel = 0.0d0
  total_time = 0.0d0
  max_steps = 1000

! Main loop: RK4 integration
  do i = 1, max_steps
    k1 = dt * calculate_derivatives(t, s, df, a1, a2, b2, am)
    k2 = dt * calculate_derivatives(t + 0.5d0 * dt, s + 0.5d0 * k1, df, a1, a2, b2, am)
    k3 = dt * calculate_derivatives(t + 0.5d0 * dt, s + 0.5d0 * k2, df, a1, a2, b2, am)
    k4 = dt * calculate_derivatives(t + dt, s + k3, df, a1, a2, b2, am)
    s = s + (k1 + 2.0d0 * k2 + 2.0d0 * k3 + k4) / 6.0d0

! Apply velocity limit
    s(2) = min(max(s(2), -vm), vm)
    t = t + dt
    fuel = fuel + dt * abs(s(3))
    if (abs(s(1) - df) <= 1.0d-6) exit

  end do

  if (i >= max_steps) then
    write(*,*) "Maximum steps reached. Solution may not have converged."
  endif

! Calculate total time in years.
  total_time = t / (3600.0 * 24.0 * 365.0)

! Output results that get fed back to python code
  write(*, '(A,F15.6)') "Distance:", d3d
  write(*, '(A,F15.6)') "Total Time:", total_time
  write(*, '(A,F15.6)') "Fuel:", fuel

contains
! Derivative function
  function calculate_derivatives(time, state, final_dist, a1_local, a2_local, b2_local, max_acceleration_local) result(derivs)
    implicit none
    real(8) :: time, state(3), derivs(3), final_dist, a1_local, a2_local, b2_local, max_acceleration_local
    real(8) :: distance, velocity, acceleration, jerk, target_acceleration

    distance = state(1)
    velocity = state(2)
    acceleration = state(3)

    target_acceleration = -(c1 / a1_local) * (distance - final_dist)
    acceleration = min(max(target_acceleration, -max_acceleration_local), max_acceleration_local) ! This is the limit enforced.
    jerk = (a2_local / b2_local) * acceleration ! jerk movement taken into account during acceleration
    derivs(1) = velocity
    derivs(2) = acceleration
    derivs(3) = jerk
  end function
  
! Calculates values for visulaization purposes- path between stars x, y, and z coords
  subroutine initialize_simulation(origin_x, origin_y, origin_z, destination_x, destination_y, destination_z)
    implicit none
    real(8) :: origin_x, origin_y, origin_z, destination_x, destination_y, destination_z
    
    ox = origin_x
    oy = origin_y
    oz = origin_z
    dx = destination_x
    dy = destination_y
    dz = destination_z
    
! Calculate initial values
    d3d = sqrt((dx - ox)**2 + (dy - oy)**2 + (dz - oz)**2)
    df = d3d
    s = 0.0d0
    t = 0.0d0
    fuel = 0.0d0
    total_time = 0.0d0
    max_steps = 10000    
  end subroutine

end program RungeKutta4Fuel_3D
