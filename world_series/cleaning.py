import pandas as pd
import numpy as np
import os

pitchers = pd.DataFrame(columns = ['player', 'release_speed_10', 'release_speed_25', 'release_speed_mean',
                                   'release_speed_median', 'release_speed_75', 'release_speed_90', 
                                   '1', '2', '3', '4', '5', '6', '7', '8', '9', '11', '12', '13', '14'])
pitchers_full = pd.DataFrame()

for file in os.listdir('pitchers/'):
    df = pd.read_csv('pitchers/' + file) # reading in the file
    df = df.dropna(subset='pitch_type') # dropping index where pitch isn't available
    df = df.dropna(subset='zone') # dropping where zone isn't available

    batter = 0
    last_pitch = np.nan # sequence
    this_pitch = np.nan # sequence
    pitch_sequence = []
    pitch_pct = {} # two-pitch sequences and individual pitch dictionary

    # two pitch sequence percentages, pitch sequence = (slider --> fastball)
    for i in df.index:
        if df['batter'][i] != batter:
            batter = df['batter'][i]
            this_pitch = df['pitch_type'][i] # first pitch in an at-bat
        elif df['batter'][i] == batter:
            last_pitch = this_pitch
            this_pitch = df['pitch_type'][i]
            pitch_sequence.append((last_pitch, this_pitch)) # appending sequence to list

    uq_pitch_sequences = list(set(pitch_sequence)) # finding unique pitch sequences

    seq_counts = {} # how many times pitcher throws each sequence
    for seq in uq_pitch_sequences:
        count = pitch_sequence.count(seq) # how many times sequence is in list
        seq_counts[seq] = count

    for seq, count in zip(seq_counts, seq_counts.values()):
        pitch_pct[seq[0] + '-' + seq[1]] = count/sum(seq_counts.values()) # pitch sequence count as % of total

    # unique pitches percentages
    pitches = df['pitch_type'].tolist()
    uq_pitches = list(set(pitches)) # finding unique pitches

    pitch_counts = {}
    for pitch in uq_pitches:
        count = pitches.count(pitch) # how many times pitch is in list
        pitch_counts[pitch] = count

    for pitch, count in zip(pitch_counts, pitch_counts.values()):
        pitch_pct[pitch] = count/sum(pitch_counts.values()) # pitch count as % of total

    pitches = pd.DataFrame([pitch_pct])

    pitches['total_pitches'] = len(uq_pitches) # how many types of pitches can this pitcher throw?
    pitches['player'] = df['pitcher'].unique()

    release_speed = df['release_speed'].tolist() # what speed does this pitcher normally throw? release vs. effective,
    pitches['release_speed_10'] = np.percentile(release_speed, 10) # effective shows what the batter perceives the
    pitches['release_speed_25'] = np.percentile(release_speed, 25) # pitch speed is while release is what it actually
    pitches['release_speed_mean'] = np.mean(release_speed) # is
    pitches['release_speed_median'] = np.median(release_speed)
    pitches['release_speed_75'] = np.percentile(release_speed, 75)
    pitches['release_speed_90'] = np.percentile(release_speed, 90)

    zones = df['zone'].tolist() # where the ball was thrown within strike / ball zone
    uq_zones = list(set(zones)) # 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14

    zone_counts = {}
    for zone in uq_zones:
        count = zones.count(zone) # how many times does the pitch land in this zone?
        zone_counts[zone] = count

    for zone, count in zip(zone_counts, zone_counts.values()):
        pitches[str(int(zone))] = count/sum(zone_counts.values()) # zone count as % of total

    existing_sequences = pitchers.columns

    for column in pitches:
        if column not in existing_sequences: # if we haven't seen this column yet
            pitchers[column] = np.nan # add it to the df

    pitchers = pitchers.append(pitches, ignore_index=True) # appending new pitcher to full df
    pitchers_full = pitchers_full.append(df, ignore_index=True) # all of the pitches in one df

pitchers.fillna(0, inplace=True)
pitchers = pitchers[pitchers['release_speed_mean'] != 0.0]
