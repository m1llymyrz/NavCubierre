program rkf3d
  implicit none
  real(8) :: ti, step, final_dist, fl, o_x, o_y, o_z, d_x, d_y, d_z, dist_3d, t_time, t_step
  real(8) :: st(3), k_1(3), k_2(3), k_3(3), k_4(3) ! used for rk4, 3 coordinates used
  real(8) :: p1, p2, p3, v_max, c_val, a_max ! parameters
  integer :: iter, max_i
  p1 = 2.0d0
  p2 = 1.0d0
  p3 = 0.5d0
  v_max = 100.0d0
  c_val = 0.1d0
  a_max = 10.0d0
  t_step = 1.0d0
  step = t_step * 3600.0d0 * 24.0d0 * 365.0d0
! Coordinates come directly from python code.

! Initialize variables.
  dist_3d = 0.0d0
  final_dist = 0.0d0
  st = 0.0d0
  ti = 0.0d0
  fl = 0.0d0
  t_time = 0.0d0
  max_i = 1000

! Main loop: RK4 integration
  do iter = 1, max_i
    k_1 = step * calc_deriv(ti, st, final_dist, p1, p2, p3, a_max)
    k_2 = step * calc_deriv(ti + 0.5d0 * step, st + 0.5d0 * k_1, final_dist, p1, p2, p3, a_max)
    k_3 = step * calc_deriv(ti + 0.5d0 * step, st + 0.5d0 * k_2, final_dist, p1, p2, p3, a_max)
    k_4 = step * calc_deriv(ti + step, st + k_3, final_dist, p1, p2, p3, a_max)
    st = st + (k_1 + 2.0d0 * k_2 + 2.0d0 * k_3 + k_4) / 6.0d0

! Apply out 100c velocity limit
    st(2) = min(max(st(2), -v_max), v_max)
    ti = ti + step
    fl = fl + step * abs(st(3))
    if (abs(st(1) - final_dist) <= 1.0d-6) exit
  end do

  t_time = ti / (3600.0 * 24.0 * 365.0)

! Output results that get fed back to python code
  write(*, '(A,F15.6)') "Distance:", dist_3d
  write(*, '(A,F15.6)') "Total Time:", t_time
  write(*, '(A,F15.6)') "Fuel:", fl

contains
! Derivative function; solve the euler-lagrange equation
  function calc_deriv(time, state, f_dist, p_a1, p_a2, p_b2, max_accel) result(derivs)
    implicit none
    real(8) :: time, state(3), derivs(3), f_dist, p_a1, p_a2, p_b2, max_accel
    real(8) :: dist, vel, accel, jrk, t_accel

    dist = state(1)
    vel = state(2)
    accel = state(3)

    t_accel = -(c_val / p_a1) * (dist - f_dist)
    accel = min(max(t_accel, -max_accel), max_accel) ! This is the limit enforced.
    jrk = (p_a2 / p_b2) * accel ! jerk movement taken into account during acceleration
    derivs(1) = vel
    derivs(2) = accel
    derivs(3) = jrk
  end function

! Calculates values for visulaization purposes- path between stars x, y, and z coords
  subroutine init_sim(orig_x, orig_y, orig_z, dest_x, dest_y, dest_z)
    implicit none
    real(8) :: orig_x, orig_y, orig_z, dest_x, dest_y, dest_z

    o_x = orig_x
    o_y = orig_y
    o_z = orig_z
    d_x = dest_x
    d_y = dest_y
    d_z = dest_z

! Calculate initial values
    dist_3d = sqrt((d_x - o_x)**2 + (d_y - o_y)**2 + (d_z - o_z)**2)
    final_dist = dist_3d
    st = 0.0d0
    ti = 0.0d0
    fl = 0.0d0
    t_time = 0.0d0
    max_i = 10000
  end subroutine

end program rkf3d
