"""
solver.py
---------
Solves the Priority-Aware QUBO using classical and quantum-inspired solvers.

Supported methods (all with graceful fallbacks):
    - "neal"   : Neal Simulated Annealing (quantum-inspired, LOCAL)
    - "sa"     : dimod basic Simulated Annealing (LOCAL)
    - "tabu"   : Tabu Search (LOCAL)
    - "exact"  : Brute-force ExactSolver (LOCAL, tiny problems only)

Author: Fidha Ahamed
"""

import dimod


# --------------------------------------------------
# 1. SOLVE USING NEAL SIMULATED ANNEALING (RECOMMENDED)
# --------------------------------------------------

def solve_with_neal(bqm, num_reads=200):
    """
    Solve QUBO using D-Wave Neal Simulated Annealing.

    This is the recommended default solver. It faithfully replicates
    quantum annealing behaviour locally with configurable parameters.
    No API token required.

    Args:
        bqm (BinaryQuadraticModel)
        num_reads (int): Number of annealing runs

    Returns:
        best_sample (dict)
    """
    try:
        import neal
        sampler = neal.SimulatedAnnealingSampler()
        sampleset = sampler.sample(
            bqm,
            num_reads=num_reads,
            num_sweeps=1000,
            beta_range=[0.1, 10.0],
        )
    except ImportError:
        print("neal not installed. Falling back to dimod SA.")
        sampler = dimod.SimulatedAnnealingSampler()
        sampleset = sampler.sample(bqm, num_reads=num_reads)

    return sampleset.first.sample


# --------------------------------------------------
# 2. SOLVE USING BASIC SIMULATED ANNEALING (LOCAL)
# --------------------------------------------------

def solve_with_simulated_annealing(bqm, num_reads=100):
    """
    Solve the QUBO using dimod's built-in Simulated Annealing.

    Args:
        bqm (BinaryQuadraticModel)
        num_reads (int)

    Returns:
        best_sample (dict)
    """
    sampler = dimod.SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm, num_reads=num_reads)

    return sampleset.first.sample


# --------------------------------------------------
# 3. SOLVE USING TABU SEARCH (LOCAL)
# --------------------------------------------------

def solve_with_tabu(bqm, num_reads=100, timeout=1000):
    """
    Solve QUBO using D-Wave Tabu Search.

    No API token required. Good alternative to SA for benchmarking.

    Args:
        bqm (BinaryQuadraticModel)
        num_reads (int)
        timeout (int): Milliseconds per read

    Returns:
        best_sample (dict)
    """
    try:
        import tabu
        sampler = tabu.TabuSampler()
        sampleset = sampler.sample(bqm, num_reads=num_reads, timeout=timeout)
    except ImportError:
        print("tabu not installed. Falling back to dimod SA.")
        sampler = dimod.SimulatedAnnealingSampler()
        sampleset = sampler.sample(bqm, num_reads=num_reads)

    return sampleset.first.sample


# --------------------------------------------------
# 4. SOLVE USING EXACT SOLVER (SMALL PROBLEMS ONLY)
# --------------------------------------------------

def solve_exact(bqm):
    """
    Solve QUBO exactly via brute-force enumeration.

    WARNING: Only feasible for very small problems (<20 binary variables).
    Guarantees the global optimum.

    Args:
        bqm (BinaryQuadraticModel)

    Returns:
        best_sample (dict)
    """
    sampler = dimod.ExactSolver()
    sampleset = sampler.sample(bqm)

    return sampleset.first.sample


# --------------------------------------------------
# 5. DECODE SOLUTION INTO ROUTE SELECTION
# --------------------------------------------------

def decode_solution(sample, variable_map, vehicles):
    """
    Decode solver output into selected routes.

    Args:
        sample (dict): Binary solution from any solver
        variable_map (dict): (vid, route_idx) -> variable_name
        vehicles (list): List of vehicle dicts with candidate_routes

    Returns:
        selected_routes (dict): {vehicle_id: chosen_route_node_list}
    """
    selected_routes = {}

    for (vid, r_idx), var_name in variable_map.items():
        if sample.get(var_name, 0) == 1:
            # Safe lookup: handle both list and dict vehicle containers
            if isinstance(vehicles, list) and vid < len(vehicles):
                routes = vehicles[vid].get("candidate_routes", [])
            elif isinstance(vehicles, dict) and vid in vehicles:
                routes = vehicles[vid].get("candidate_routes", [])
            else:
                continue

            if r_idx < len(routes):
                selected_routes[vid] = routes[r_idx]

    return selected_routes


# --------------------------------------------------
# 6. COMPLETE SOLVER PIPELINE
# --------------------------------------------------

def solve_traffic_qubo(bqm, variable_map, vehicles, method="neal"):
    """
    Full solver pipeline. Routes the BQM to the appropriate solver
    and decodes the result into route selections.

    Args:
        bqm (BinaryQuadraticModel): The QUBO to solve
        variable_map (dict): Variable name mapping
        vehicles (list): Vehicle data with candidate routes
        method (str): One of:
            "neal"  - Neal SA, quantum-inspired (default, LOCAL)
            "sa"    - dimod basic SA (LOCAL)
            "tabu"  - Tabu Search (LOCAL)
            "exact" - Brute-force (LOCAL, tiny problems)

    Returns:
        selected_routes (dict): {vehicle_id: route_node_list}
    """
    if method == "neal":
        sample = solve_with_neal(bqm)
    elif method == "sa":
        sample = solve_with_simulated_annealing(bqm)
    elif method == "tabu":
        sample = solve_with_tabu(bqm)
    elif method == "exact":
        sample = solve_exact(bqm)
    else:
        print(f"Unknown method '{method}'. Falling back to Neal SA.")
        sample = solve_with_neal(bqm)

    selected_routes = decode_solution(sample, variable_map, vehicles)
    return selected_routes