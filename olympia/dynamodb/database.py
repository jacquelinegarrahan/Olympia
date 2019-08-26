import boto3
from olympia import CONFIGS

class DBConnection():

    dynamodb = boto3.resource('dynamodb')
    midi_table = None
    models_table = None


    def __init__(self):
        #try to populate the midi table
        try:
            self.midi_table = Table("midis")
        except Exception as e:
            print("Midi Table doesn't exist.")

        #try to populate the models table
        try:
            self.model_table = Table("models")
        except Exception as e:
            print("Model Table doesn't exist.")

        #try to populate the songs table
        try:
            self.model_table = Table("songs")
        except Exception as e:
            print("Song Table doesn't exist.")

    def create_midi_table(self):
        """
        Create database for midi files
        Midis will be characterized by song names, artists, time signatures, and genre
        """

        table = self.dynamodb.create_table(
            TableName='midis',
            KeySchema=[
                {
                    'AttributeName': 'url',
                    'KeyType': 'RANGE'
                },
                {
                    'AttributeName': 'midi_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'song_name',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'artist',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'date_added',
                    'KeyType': 'RANGE'
                },
                {
                    'AttributeName': 'key',
                    'KeyType': 'RANGE'
                },
                {
                    'AttributeName': 'time_signature',
                    'KeyType': 'RANGE'
                },
                {
                    'AttributeName': 'genre',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'url',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'midi_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'song_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'artist',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'date_added',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'key',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'time_signature',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'genre',
                    'AttributeType': 'S'
                }
                ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
        )

    def create_models_table(self):
        """
        Create database for model builds
        """

        table = self.dynamodb.create_table(
            TableName='models',
            KeySchema=[
                {
                    'AttributeName': 'model_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'model_type',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'lstm_sequence_length',
                    'KeyType': 'range'
                },
                {
                    'AttributeName': 'model_settings',
                    'KeyType': 'hash'
                },
                {
                    'AttributeName': 'training_midis',
                    'KeyType': 'hash'
                },
                {
                    'AttributeName': 'instrument',
                    'KeyType': 'hash'
                },
                {
                    'AttributeName': 'n_training_notes',
                    'KeyType': 'range'
                },
                {
                    'AttributeName': 'score',
                    'KeyType': 'range'
                },
                {
                    'AttributeName': 'output_diversity',
                    'KeyType': 'range'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'model_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'model_type',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'lstm_sequence_length',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'model_settings',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'training_midis',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'instrument',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'n_training_notes',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'score',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'output_diversity',
                    'AttributeType': 'N'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
        )
    

    def create_song_table(self):
        """
        Creat database for song files
        For tracking generated songs
        """

        table = self.dynamodb.create_table(
            TableName='songs',
            KeySchema=[
                {
                    'AttributeName': 'song_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'duration_model',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'sequence_model',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'harmony_model',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'create_date',
                    'KeyType': 'RANGE'
                },
                {
                    'AttributeName': 'key',
                    'KeyType': 'RANGE'
                },
                {
                    'AttributeName': 'time_signature',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'quality_score',
                    'KeyType': 'Range'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'song_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'duration_model',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'sequence_model',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'harmony_model',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'create_date',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'key',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'time_signature',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'quality_score',
                    'AttributeType': 'N'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
        )



if __name__ == '__main__':
    db = DBConnection()
    db.create_midi_table()
    db.create_models_table()
    db.create_song_table()