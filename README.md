# INTRODUCTION
Olympia was built for the purpose of exploring the creative potential of machines in music composition. At it's current iteration, Olympia generates multi-part midi clips using an ensemble of neural networks trained on songs mined from free online music repositories (midiworld.com, freemidi.com). Beyond a machine learning exercise, Olympia is intended to be a collaborative platform for music composition between humans and machines. The modeling engine uses the music21 project (https://web.mit.edu/music21) extensively in processing and compiling songs. Output from the Olmypia engine has been crafted into tracks, which may be found at the soundcloud link below. Pretrained models are included in this repository; however, the schema for this project can be found in olympia/db_schema.

# SCRAPING
Olympia is currently set up to scrape midiworld.com and freemidi.com for midi files. The scraped songs are decomposed into instrument parts and each part is assigned a scored based on the index of dispersion of the notes contained in that part

# MODELS
For the creative neural network workflow, the model ensemble contains models governing duration, note progression, and larger sequence structure. A set of music theory rules are used for constraining the output. LSTM models were attractive for this application because of the differential memory structures in the LSTM cell. The sigmoid layer of an LSTM network allows for the ability to forget past information, while the forget gate allows for the determination of relational relevance between steps in the time series. For example, a resolution tone three time steps back may be more significant than a consonant directly proceeding a note. Applying these concepts in generative music may account for the differential impact of recency on composition. 

In order to maximize the diversity of the models, the loss function was swapped for a creative measure of output diversity. Given a randomized start progression selected from the training data, how diverse is x steps of the model output. Convergence was then measured on the maximized diversity

# SETUP
To use visualization tools, need to install pyaudio:
 ` brew install portaudio`
`sudo apt-get install python3-pyaudio`