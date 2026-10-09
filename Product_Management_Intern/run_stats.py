import pandas as pd
import numpy as np

df = pd.read_csv(r'd:\Josh Talks\Product_Management_Intern\q2_dataset.csv')
print(f'Total rows in raw dataset: {len(df)}')

# Handle rows
clean = df.dropna(subset=['duration', 'time_taken_by_user']).copy()
clean['time_ratio'] = clean['time_taken_by_user'] / clean['duration']

c_sub25 = (clean['time_ratio'] < 0.25).sum()
c_sub50 = (clean['time_ratio'] < 0.50).sum()
c_sub75 = (clean['time_ratio'] < 0.75).sum()
c_sub100 = (clean['time_ratio'] < 1.00).sum()
c_high_cps = (clean['segment_character_per_second'] > 20).sum()
c_extreme_cps = (clean['segment_character_per_second'] > 40).sum()
c_zero = (clean['time_taken_by_user'] <= 0).sum()
nan_whisper = df['whisper_text'].isna().sum()

print(f'Clean rows analyzed: {len(clean)}')
print(f'Rows where time_taken < 0.25 * duration: {c_sub25} ({c_sub25/len(clean)*100:.2f}%)')
print(f'Rows where time_taken < 0.50 * duration: {c_sub50} ({c_sub50/len(clean)*100:.2f}%)')
print(f'Rows where time_taken < 0.75 * duration: {c_sub75} ({c_sub75/len(clean)*100:.2f}%)')
print(f'Rows where time_taken < 1.00 * duration: {c_sub100} ({c_sub100/len(clean)*100:.2f}%)')
print(f'Rows with CPS > 20 chars/sec: {c_high_cps} ({c_high_cps/len(clean)*100:.2f}%)')
print(f'Rows with CPS > 40 chars/sec: {c_extreme_cps} ({c_extreme_cps/len(clean)*100:.2f}%)')
print(f'Rows with time_taken <= 0: {c_zero}')
print(f'Rows where whisper_text is NaN: {nan_whisper} ({nan_whisper/len(df)*100:.2f}%)')

# Examine edit behaviors when whisper_text is available
has_whisper = clean[clean['whisper_text'].notna()].copy()
print(f'\nRows with non-null whisper_text: {len(has_whisper)}')

# Exact match between whisper_text and user_text
has_whisper['is_identical'] = has_whisper['whisper_text'].str.strip() == has_whisper['user_text'].str.strip()
print(f'Identical text submissions: {has_whisper["is_identical"].sum()} ({has_whisper["is_identical"].mean()*100:.2f}%)')

# Flagged as edited == Yes but text is identical
fake_yes = has_whisper[(has_whisper['is_edited'] == 'Yes') & (has_whisper['is_identical'])]
print(f'Reported is_edited=Yes but text identical (or only whitespace diff): {len(fake_yes)}')

# Speed-runners who did NOT edit (rubber-stampers)
rubber_stampers = has_whisper[(has_whisper['is_edited'] == 'No') & (has_whisper['time_ratio'] < 0.75)]
print(f'Rubber-stampers (is_edited=No & time_ratio < 0.75): {len(rubber_stampers)} ({len(rubber_stampers)/len(has_whisper)*100:.2f}%)')
