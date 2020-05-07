import hashlib
import json
import statistics
from olympia import db

# METHOD: get_model_hash
# DESCRIPTION: utility function for getting model hash
def get_model_hash(model_settings):
    hashed = hashlib.md5(json.dumps(model_settings.dict()).encode("utf-8"))
    model_hash = hashed.hexdigest()

    return model_hash


# METHOD: get_iod
# DESCRIPTION: returns the index of dispersion of a list
def get_iod(value_list):

    # use sample variance calculation
    var = statistics.variance(value_list)
    mean = statistics.mean(value_list)

    return var / mean


# METHOD: load_model_settings
# DESCRIPTION: load settings given a model hash
def load_model_settings(model_hash):

    query = """
    SELECT model_settings FROM models
    WHERE model_hash = :model_hash 
    """
    params = {"model_hash": model_hash}

    results = db.execute_query(query, params).fetchone()
    if results.model_settings:
        return json.loads(results.model_settings)
    else:
        return None
