import numpy as np
from scipy.sparse import csr_matrix


# Function to assert if elements are covered at a decent proportion
def check_if_covered(
        subset,
        superset,
        subset_name="features",
        superset_name="resource",
        prop_missing_allowed=99,
        verbose=False):
    """Assert `np.all(np.isin(subset, superset))` with a more readable error
    message """
    subset = np.asarray(subset)
    is_missing = ~np.isin(subset, superset)
    prop_missing = np.sum(is_missing) / len(subset)
    x_missing = " ,".join([x for x in subset[is_missing]])

    if prop_missing > prop_missing_allowed:
        msg = (
            f"Allowed proportion ({prop_missing_allowed}) of missing "
            f"{subset_name} elements exceeded ({prop_missing:.2f}). "
        )
        raise ValueError(msg + f"{x_missing} missing from {superset_name}")
    if verbose:
        print(f"{x_missing} found in {superset_name} but missing from "
              f"{subset_name}!")


# Helper Function to check if the matrix is in the correct format
def check_mat(x, verbose=False):
    # convert to sparse csr matrix
    if not isinstance(x, csr_matrix):
        if verbose:
            print("Converting mat to CSR format")
        x = csr_matrix(x).copy()

    # Check for empty features
    msk_features = np.sum(x != 0, axis=0).A1 == 0
    n_empty_features = np.sum(msk_features)
    if n_empty_features > 0:
        if verbose:
            print("{0} features of mat are empty, they will be removed.".format(
                n_empty_features))
        x = x[:, ~msk_features]

    # Check for empty samples
    msk_samples = np.sum(x != 0, axis=1).A1 == 0
    n_empty_samples = np.sum(msk_samples)
    if n_empty_samples > 0:
        if verbose:
            print("{0} samples of mat are empty, they will be removed.".format(
                n_empty_samples))
        x = x[:, ~msk_features]

    # Check if log-norm
    _sum = np.sum(x.data[0:100])
    if _sum == np.floor(_sum):
        if verbose:
            print("Make sure that normalized counts are passed!")

    # Check for non-finite values
    if np.any(~np.isfinite(x.data)):
        raise ValueError(
            """mat contains non finite values (nan or inf), please set them 
            to 0 or remove them.""")

    return x


# Helper function to replace a substring in string and append to list
def _append_replace(x, l):
    l.append(x)
    return x.replace('_', '')


# format variable names
def format_vars(var_names, verbose=False):
    changed = []
    var_names = [_append_replace(x, changed) if ('_' in x) else x for x in
                 var_names]
    changed = ' ,'.join(changed)
    if verbose & (len(changed) > 0):
        print(f"Replace underscores (_) with blank in {changed}", )
    return var_names


def filter_resource(resource, var_names):
    """
    Filter interactions for which vars are not present.

    Note that here I remove any interaction that /w genes that are not found
    in the dataset. Note that this is not necessarily the case in liana-r.
    There, I assign the expression of those with missing subunits to 0, while
    those without any subunit present are implicitly filtered.

    """
    # Remove those without any subunit
    resource = resource[(np.isin(resource.ligand, var_names)) &
                        (np.isin(resource.receptor, var_names))]

    # Only keep interactions /w complexes for which all subunits are present
    missing_comps = resource[['_' in x for x in resource['interaction']]].copy()
    missing_comps['all_units'] = \
        missing_comps['ligand_complex'] + '_' + missing_comps[
            'receptor_complex']

    # Get those not with all subunits
    missing_comps = missing_comps[np.logical_not(
        [all([x in var_names for x in entity.split('_')])
         for entity in missing_comps.all_units]
    )]
    # Filter them
    return resource[~resource.interaction.isin(missing_comps.interaction)]