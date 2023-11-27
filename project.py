from sympy import symbols, solve, Eq
import sys


class Parameters:
    def __init__(self):
        # Define all the parameters
        self.nu = 0.3       #Possion ratio
        self.E = 2.1e5      #Modulus of Elasticity MPa
        self.F1 = 0.72      #Design factor for pressure containment of Zone 1
        self.F2 = 0.5       #Design factor for pressure containment of Zone 2
        self.T = 1          #Temperature derating factor
        self.h = 71         #Water depth (m)
        self.rho = 1025     #Sea water Density (kg/m^3)
        self.g = 9.81       #grav acc.
        self.CA = 3.048     #Corrosion Allowance (mm)
        self.t_tol = 10 / 100 #Manufacturing wall thickness tolerance
        self.Pi = 19        #Net internal design pressure (MPa)
        self.delta = 0
        self.Fs1 = 0.72
        self.Fs2 = 0.8
        self.Fs3 = 0.9


def main():
    input = sys.argv
    check_input(input)
    grade = input[1]
    YS = check_grade(grade)
    Do = outer_diameter()
    t_int = internal_thickness(Do, YS)
    t_int.append(buckle_propogation(Do, YS))
    t_int.append(buckle_initiation(Do, YS))
    max_t = max(t_int)

    print("\n\n##### STANDARD CHECKS #####")
    wall_thickness_check(max_t)


def check_grade(grade):
    """Checks grade of pipe"""
    grade_dict = {
        "A25": (172, 310),
        "A": (207, 331),
        "B": (241, 414),
        "X42": (290, 414),
        "X46": (317, 434),
        "X52": (359, 455),
        "X56": (386, 490),
        "X60": (414, 517),
        "X65": (448, 531),
        "X70": (483, 565),
    }
    try:
        YS, UTS = grade_dict.get(grade)
    except (TypeError, UnboundLocalError) as error:
        sys.exit(
            "This grade is not available.\nGrades are A25, A, B, X42, X46, X52, X56, X60, X65, X70"
        )

    print("~" * 72)
    print("[Material Strength Parameters from API 5L] ")
    print(f"PIPELINE GRADE SELECTED - {grade}")
    print(f"Yield Strength (Minimum) = {YS} MPa")
    print(f"Ultimate Tensile Strength (Minimum) = {UTS} MPa")
    print("~" * 72)

    return YS


def check_input(input):
    """Checks CLI arguments"""
    if len(input) != 2:
        sys.exit(
            "Please provde a grade on the CLI.\nGrades are A25, A, B, X42, X46, X52, X56, X60, X65, X70"
        )
    return True


def outer_diameter():
    while True:
        try:
            inches = int(
                input("\nPlease enter the outer diameter (in inches) of the oil pipe: ")
            )
            return (int(inches) * 0.0254) * 1000  # convert inches to mm
        except ValueError:
            print("\nWarning: Please input an integer for the pipe outer diameter.")


def internal_thickness(Do, YS):
    """Pipeline thickness due to internal pressure"""
    p = Parameters()
    t_int = []
    t_int.append((p.Pi * Do) / (2 * p.F1 * p.T * YS))
    t_int.append((p.Pi * Do) / (2 * p.F2 * p.T * YS))

    print("~" * 72)
    print("[Pipe thickness due to internal pressure for Zone 1 and 2] ")
    print(f"Required wall thickness for Zone 1 = {t_int[0]:.4} mm")
    print(f"Required wall thickness for Zone 2 = {t_int[1]:.4} mm")
    print("~" * 72)

    return t_int


def buckle_propogation(Do, YS):
    """Pipeline thickness due to buckle propogation"""
    p = Parameters()
    t = symbols("t")
    P_bp = (1.5 * p.rho * p.g * p.h) / 10**6
    eqn = Eq(P_bp, 24 * YS * (t / Do) ** 2.4)  # Buckle Propagation formula
    t_bp = solve(eqn, t)  # solve for t
    tbp = t_bp[0]
    print("\n[Pipe thickness due to Buckle Propagation] ")
    print(f"Required wall thickness = {tbp} mm")
    return tbp


def buckle_initiation(Do, YS):
    """Pipeline thickness due to buckle propogation"""
    p = Parameters()
    t = symbols("t")
    P_bi = (1.5 * p.rho * p.g * p.h) / 10**6
    eqn = Eq(P_bi, 0.02 * p.E * (t / Do) ** 2.064)  # Buckle Propagation formula
    t_bi = solve(eqn, t)  # solve for t
    tbi = t_bi[0]
    print("\n[Pipe thickness due to Buckle Initiation] ")
    print(f"Required wall thickness = {tbi} mm")
    return tbi


def wall_thickness_check(max_t):
    print("\n\n[Minimum Nominal Pipe Wall Thickness Check (PTS 20.196) - Offshore]")
    if max_t > 9.27:
        print(f"PASS --> Nominal wall thickness is {max_t} mm")
        return True
    else:
        print(f"FAIL --> Nominal wall thickness is {max_t} mm ")
        return False


if __name__ == "__main__":
    main()
