import click
import numbers
import numpy as np

from benchopt.util import is_matched
from benchopt.util import product_param
from benchopt.util import list_benchmark_solvers
from benchopt.util import list_benchmark_datasets
from benchopt.util import get_benchmark_objective


def validate_benchmark(benchmark):
    try:
        get_benchmark_objective(benchmark)
    except RuntimeError:
        raise click.BadParameter(
            f"The folder '{benchmark}' does not contain `objective.py`.\n"
            "Make sure you provide the path to a valid benchmark."
        )


def _validate_patterns(all_names, patterns, name_type='dataset'):
    """Check that all provided patterns match at least one name.
    """
    if patterns is None:
        return

    # Check that the provided patterns match at least one dataset.
    invalid_patterns = []
    for p in patterns:
        matched = any([is_matched(name, [p]) for name in all_names])
        if not matched:
            invalid_patterns.append(p)

    # If some patterns did not matched any dataset, raise an error
    if len(invalid_patterns) > 0:
        all_names = '- ' + '\n- '.join(all_names)
        raise click.BadParameter(
            f"Patterns {invalid_patterns} did not matched any {name_type}.\n"
            f"Available {name_type}s are:\n{all_names}"
        )


def validate_dataset_patterns(benchmark, dataset_patterns):
    """Check that all provided patterns match at least one dataset"""

    # List all dataset strings.
    datasets = list_benchmark_datasets(benchmark)
    all_datasets = []
    for dataset_class in datasets:
        for dataset_parameters in product_param(dataset_class.parameters):
            all_datasets.append(
                dataset_class._get_parametrized_name(**dataset_parameters)
            )

    _validate_patterns(all_datasets, dataset_patterns, name_type='dataset')


def validate_solver_patterns(benchmark, solver_patterns):
    """Check that all provided patterns match at least one solver"""

    # List all dataset strings.
    solver = list_benchmark_solvers(benchmark)
    all_solvers = []
    for solver_class in solver:
        for solver_parameters in product_param(solver_class.parameters):
            all_solvers.append(
                solver_class._get_parametrized_name(**solver_parameters)
            )

    _validate_patterns(all_solvers, solver_patterns, name_type='solver')


def solver_supports_dataset(solver, dataset):
    # Check that the solver is compatible with the given dataset
    if (getattr(dataset, 'is_sparse', False)
            and not getattr(solver, 'support_sparse', True)):
        return False

    return True


def check_random_state(seed):
    """Turn seed into a np.random.RandomState instance

    Parameters
    ----------
    seed : None, int or instance of RandomState
        If seed is None, return the RandomState singleton used by np.random.
        If seed is an int, return a new RandomState instance seeded with seed.
        If seed is already a RandomState instance, return it.
        Otherwise raise ValueError.
    """
    if seed is None or seed is np.random:
        return np.random.mtrand._rand
    if isinstance(seed, numbers.Integral):
        return np.random.RandomState(seed)
    if isinstance(seed, np.random.RandomState):
        return seed
    raise ValueError('%r cannot be used to seed a numpy.random.RandomState'
                     ' instance' % seed)
