import pandas as pd
import numpy as np
from datetime import datetime
#def concat_clean_extract():
#    '''
#    Preprocesses original data by concatenating, cleaning unneeded columns and by extracting
#    more useful features from the already existing ones.
#    '''
#    # combine all data to one big frame with some adjustments

n_csv = 55
frame_all = pd.read_csv('data/Kickstarter000.csv')

# load all remaining csvs and concat data
for i in range(1, n_csv+1):
    file_str = 'data/Kickstarter{0:03d}.csv'.format(i)
    df = pd.read_csv(file_str)
    frame_all = pd.concat([frame_all, df])

frame_all.reset_index(inplace=True)
# change time related columns from UNIX epoch to datetime 
for col in ['created_at', 'launched_at', 'state_changed_at', 'deadline']:
    frame_all[col] = frame_all[col].apply(lambda s: datetime.utcfromtimestamp(s))

# remove duplicate (having the same id) entries 
frame_all.drop_duplicates(subset='id', inplace=True)

# derive durations in seconds from creation to launch, from launch to state_changed_at and from launch to deadline
frame_all['dur_inactive'] = (frame_all.launched_at-frame_all.created_at).apply(lambda td: td.total_seconds())
frame_all['dur_until_state_changed'] = (frame_all.state_changed_at-frame_all.launched_at).apply(lambda td: td.total_seconds())
frame_all['dur_active'] = (frame_all.deadline-frame_all.launched_at).apply(lambda td: td.total_seconds())
frame_all['dur_ratio'] = frame_all.eval('dur_until_state_changed/dur_active')

# extract category name ("Fine Art") and slug ("photography/fine art") from category column as new features
frame_all['cat_name'] = frame_all.category.apply(lambda s: s.split('"name":"')[1].split('"')[0])
frame_all['cat_slug'] = frame_all.category.apply(lambda s: s.split('"slug":"')[1].split('"')[0])

# extract name ("New York") of location, country ("AU"), state ("KY") and type ("Town")
frame_all['loc_name'] = frame_all.location.apply(lambda s: s if s is np.NaN else s.split('"name":"')[1].split('"')[0])
frame_all['loc_country'] = frame_all.location.apply(lambda s: s if s is np.NaN else s.split('"country":"')[1].split('"')[0])
frame_all['loc_state'] = frame_all.location.apply(lambda s: np.NaN if (s is np.NaN) or (len(s.split('"state":"')) == 1) else s.split('"state":"')[1].split('"')[0])
frame_all['loc_type'] = frame_all.location.apply(lambda s: s if s is np.NaN else s.split('"type":"')[1].split('"')[0])

# extract link to thumbnail photo
frame_all['photo_thumb'] = frame_all.photo.apply(lambda s: s.split('"thumb":"')[1].split('"')[0])
# extract link to large version of project photo
frame_all['photo_large'] = frame_all.photo.apply(lambda s: s.split('"1536x864":"')[1].split('"')[0])

# extract link to project website
frame_all['project_address'] = frame_all.urls.apply(lambda s: s.split('"project":"')[1].split('"')[0])

# extract link to profile photo 
frame_all['profile_photo'] = frame_all.profile.apply(lambda s: s.split('"default":"')[1].split('"')[0])

# extract id, name, profile website and thumbnail for the creator
frame_all['creator_name'] = frame_all.creator.apply(lambda s: s.split('"name":"')[1].split('"')[0])
frame_all['creator_id'] = frame_all.creator.apply(lambda s: int(s.split('"id":')[1].split(',')[0]))
frame_all['creator_thumb'] = frame_all.creator.apply(lambda s: s.split('"thumb":"')[1].split('"')[0])
frame_all['creator_address'] = frame_all.creator.apply(lambda s: s.split('"web":{"user":"')[1].split('"')[0])

# extract main and subcategories from category slug
frame_all['main_category'] = frame_all.cat_slug.apply(lambda s: s.split('/')[0])
frame_all['sub_category'] = frame_all.cat_slug.apply(lambda s: np.NaN if len(s.split('/')) == 1 else s.split('/')[1])

# "Money" features
# Calculate amount of surpass or not surpass (pledged - goal)
frame_all['goal_surpass'] = frame_all['pledged'] - frame_all['goal']
# Calculate share of surpassing or not surpassing
frame_all['goal_surpass_share'] = frame_all['goal_surpass'] / frame_all['goal']
# Convert goal_surpass into USD
frame_all['goal_surpass_usd'] = frame_all['goal_surpass'] * frame_all['static_usd_rate']
# Convert goal into USD
frame_all['goal_usd'] = frame_all['goal'] * frame_all['static_usd_rate']

# Extract features from Blurb and Name: length + number of words
# Calculate number of words in blurb
frame_all['blurb_words'] = frame_all['blurb'].str.split().str.len()
# Calculate number of characters in blurb
frame_all['blurb_len'] = frame_all['blurb'].str.len()
# Calculate number of characters in name
frame_all['name_len'] = frame_all['name'].str.len()
# Calculate number of words in name
frame_all['name_words'] = frame_all['name'].str.split().str.len()


# create baseline model and compute predictions based on it
df=frame_all.groupby(['main_category', 'state']).count().reset_index()
categories = frame_all.main_category.unique()
d = {}
for cat in categories:
    n_suc = df.query('state == "successful" and main_category == "{}"'.format(cat))['category'].values[0]
    n_fail = df.query('state == "failed" and main_category == "{}"'.format(cat))['category'].values[0]
    if n_suc/(n_suc+n_fail) > 0.5:
        d[cat] = 1
    else:
        d[cat] = 0

# now predict
dict_map = {'successful':1,'failed':0}
frame_all['state_bool'] = frame_all['state'].map(dict_map)
frame_all['baseline'] = frame_all['main_category'].map(d)

# delete obsolete features
frame_all.drop(['category', 'urls', 'profile', 'location', 'photo', 'creator'], axis=1, inplace=True)
frame_all.drop(['friends', 'is_backing', 'is_starred', 'permissions'], axis=1, inplace=True)
# drop unnamed first column
frame_all.drop(frame_all.columns[0], axis=1, inplace=True)

# remove rows with states other than successful or failed
frame_all = frame_all.query('state == "successful" or state == "failed"')

# change state_bool to int
frame_all.state_bool = frame_all.state_bool.astype('int') 

# fill some nans with empty strings
frame_all.creator_name.fillna(value='--', inplace=True)
frame_all.sub_category.fillna(value='--', inplace=True)

# now drop remaining nans entirely
frame_all.dropna(inplace=True)

# change categorical object/string columns to category
cat_features = ['country', 'cat_name', 'cat_slug', 'loc_name', 'loc_country', 'loc_state', 'loc_type',
'main_category', 'sub_category']
for feature in cat_features:
    frame_all[feature] = frame_all[feature].astype('category')

print('Total rows (unique project ids): ', len(frame_all))
frame_all.to_csv('data/Kickstarter_full.csv')