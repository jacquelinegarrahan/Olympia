import logging
import boto3
import os
import json
from datetime import datetime
from botocore.exceptions import ClientError
import torch
from olympia import db
from olympia import ROOT_DIR

# METHOD: upload_file
# DESCRIPTION: upload a file to s3
def upload_file(file_name, save_file):
    # Upload the file
    s3_client = boto3.client("s3")

    try:
        s3_client.upload_file(file_name, "olympia-files", save_file)

    except ClientError as e:
        logging.error(e)
        return False

    return True


# METHOD: download_file
# DESCRIPTION: download a file from S3
def download_file(file_name, save_path):
    # download the file
    s3_client = boto3.client("s3")

    try:
        s3_client.download_file("olympia-files", file_name, save_path)

    except ClientError as e:
        logging.error(e)
        return False

    return True


# METHOD: save_model
# DESCRIPTION: save model data to S3
def save_model(model, model_hash, model_settings, score, persist_local=False):

    # save locally
    local_model_path = f"{ROOT_DIR}/olympia/files/models/model_{model_hash}.pt"
    torch.save(model, local_model_path)

    upload_file(local_model_path, f"models/model_{model_hash}.pt")

    if not persist_local:
        os.remove(local_model_path)

    # save song into midis table
    db.insert(
        "models",
        {
            "model_hash": model_hash,
            "model_type": model_settings.model_type,
            "lstm_sequence_length": model_settings.sequence_length,
            "create_date": model_settings.create_date,
            "model_settings": model_settings.dict(),
            "instrument": model_settings.instrument,
            "output_diversity": score,
        },
    )


# METHOD: save_mapping
# DESCRIPTION: save mapping to s3
def save_mapping(mapping, model_hash, persist_local=False):

    # save locally
    local_mapping = f"{ROOT_DIR}/olympia/files/mappings/mapping_{model_hash}.json"
    with open(local_mapping, "w") as f:
        f.write(json.dumps(mapping))

    upload_file(local_mapping, f"mappings/mapping_{model_hash}.json")

    if not persist_local:
        os.remove(local_mapping)


# METHOD: get_model
# DESCRIPTION: get and load model
def get_model(model_hash):

    local_model_path = f"{ROOT_DIR}/olympia/files/models/model_{model_hash}.pt"
    # local_state_dict_path = f"{ROOT_DIR}/olympia/files/models/state_{model_hash}.pt"

    # download model and state dict
    if not os.path.exists(local_model_path):
        download_file(f"models/model_{model_hash}.pt", local_model_path)

    # download_file(f"models/state_{model_hash}.pt", local_state_dict_path)
    model = torch.load(local_model_path)

    # put model in eval state
    model.eval()

    return model


# METHOD: get_model
# DESCRIPTION: get and load model
def get_mapping(model_hash):

    local_mapping = f"{ROOT_DIR}/olympia/files/mappings/mapping_{model_hash}.json"

    if not os.path.exists(local_mapping):
        download_file(f"mappings/mapping_{model_hash}.json", local_mapping)

    mapping = None
    content = None
    with open(local_mapping) as f:
        content = f.read()

    if content:
        mapping = json.loads(content)

    return mapping


# METHOD: save_song
# DESCRIPTION: save song and associated data
def save_song(
    midi, settings, key, time_signature, quality_score, duration_model_hash, harmony_model_hash, sequence_model_hash
):

    # save local song
    local_song = f"{ROOT_DIR}/olympia/files/songs/{song_hash}.mid"

    # upload
    upload_file(local_song, f"songs/{song_hash}.mid")

    # save song into songs table in db
    db.insert(
        "songs",
        {
            "create_date": datetime.now().strftime("%H-%m-%d"),
            "song_settings": settings,
            "key": key,
            "time_signature": time_signature,
            "quality_score": quality_score,
            "duration_model_hash": duration_model_hash,
            "harmony_model_hash": harmony_model_hash,
            "sequence_model_hash": sequence_model_hash,
        },
    )
