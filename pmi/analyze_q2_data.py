import pandas as pd
import numpy as np
import json
import os

df = pd.read_csv(r"d:\Josh Talks\pmi\q2_dataset.csv")

total_rows = len(df)
total_users = df['user_id'].nunique()

print(f"Total rows: {total_rows}")
print(f"Total unique users: {total_users}")

# Basic clean up for numeric
df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
df['time_taken_by_user'] = pd.to_numeric(df['time_taken_by_user'], errors='coerce')
df['segment_character_per_second'] = pd.to_numeric(df['segment_character_per_second'], errors='coerce')

# is_edited clean up
# Check values in is_edited
print("is_edited value counts:")
print(df['is_edited'].value_counts(dropna=False))

# Standardize is_edited to boolean
df['is_edited_bool'] = df['is_edited'].astype(str).str.lower().isin(['true', 'yes', '1'])

# Calculate ratio of time taken to audio duration
df['time_ratio'] = df['time_taken_by_user'] / df['duration'].replace(0, np.nan)

# Text length comparison
df['whisper_len'] = df['whisper_text'].astype(str).str.len()
df['user_len'] = df['user_text'].astype(str).str.len()
df['len_diff'] = df['user_len'] - df['whisper_len']
df['abs_len_diff'] = df['len_diff'].abs()

# 1. Pattern 1: Rapid / Unlistened Submissions (time_taken_by_user < duration)
rapid_subs = df[df['time_taken_by_user'] < df['duration']]
extreme_rapid = df[df['time_taken_by_user'] < 0.5 * df['duration']]
sub_1sec = df[df['time_taken_by_user'] <= 1.0]

print("\n--- Speed & Audio Playback Patterns ---")
print(f"Tasks where time_taken < duration: {len(rapid_subs)} ({len(rapid_subs)/total_rows*100:.2f}%)")
print(f"Tasks where time_taken < 0.5 * duration: {len(extreme_rapid)} ({len(extreme_rapid)/total_rows*100:.2f}%)")
print(f"Tasks where time_taken <= 1.0s: {len(sub_1sec)} ({len(sub_1sec)/total_rows*100:.2f}%)")

# 2. Pattern 2: Blind Rubber-stamping (Zero Edits + Extremely Fast)
zero_edit = df[~df['is_edited_bool']]
zero_edit_fast = df[(~df['is_edited_bool']) & (df['time_taken_by_user'] < df['duration'])]

print("\n--- Rubber-Stamping / Zero Edit Patterns ---")
print(f"Tasks with is_edited == False: {len(zero_edit)} ({len(zero_edit)/total_rows*100:.2f}%)")
print(f"Tasks with is_edited == False AND time_taken < duration: {len(zero_edit_fast)} ({len(zero_edit_fast)/total_rows*100:.2f}%)")

# 3. Pattern 3: Impossible Character Velocity (CPS)
cps_desc = df['segment_character_per_second'].describe(percentiles=[0.5, 0.75, 0.9, 0.95, 0.99])
print("\n--- Segment Character Per Second (CPS) ---")
print(cps_desc)
extreme_cps = df[df['segment_character_per_second'] > 25.0]
ultra_cps = df[df['segment_character_per_second'] > 50.0]
print(f"Tasks with CPS > 25 (Exceeds world champion typing speed): {len(extreme_cps)} ({len(extreme_cps)/total_rows*100:.2f}%)")
print(f"Tasks with CPS > 50: {len(ultra_cps)} ({len(ultra_cps)/total_rows*100:.2f}%)")

# 4. Pattern 4: Text Vandalism / Truncation / Gibberish
# User submits very short text when whisper was long
severe_truncation = df[(df['whisper_len'] > 20) & (df['user_len'] < 5)]
print("\n--- Text Vandalism / Truncation ---")
print(f"Severe truncation (Whisper > 20 chars, User < 5 chars): {len(severe_truncation)} ({len(severe_truncation)/total_rows*100:.2f}%)")

# User Level Aggregation
user_agg = df.groupby('user_id').agg(
    total_tasks=('recording_url', 'count'),
    mean_duration=('duration', 'mean'),
    mean_time_taken=('time_taken_by_user', 'mean'),
    median_time_taken=('time_taken_by_user', 'median'),
    edit_rate=('is_edited_bool', 'mean'),
    mean_cps=('segment_character_per_second', 'mean'),
    max_cps=('segment_character_per_second', 'max'),
    unlisten_rate=('time_ratio', lambda s: (s < 1.0).mean())
).reset_index()

print("\n--- User Aggregation Summary ---")
print(user_agg.describe())

# Save summary stats to json
stats_out = {
    "total_tasks": int(total_rows),
    "total_unique_users": int(total_users),
    "edited_tasks_count": int(df['is_edited_bool'].sum()),
    "unedited_tasks_count": int((~df['is_edited_bool']).sum()),
    "tasks_time_less_than_duration": int(len(rapid_subs)),
    "tasks_time_less_than_half_duration": int(len(extreme_rapid)),
    "tasks_time_sub_1sec": int(len(sub_1sec)),
    "tasks_cps_above_25": int(len(extreme_cps)),
    "tasks_cps_above_50": int(len(ultra_cps)),
    "severe_truncation_count": int(len(severe_truncation)),
    "mean_duration": float(df['duration'].mean()),
    "median_duration": float(df['duration'].median()),
    "mean_time_taken": float(df['time_taken_by_user'].mean()),
    "median_time_taken": float(df['time_taken_by_user'].median()),
    "mean_cps": float(df['segment_character_per_second'].mean()),
    "p95_cps": float(df['segment_character_per_second'].quantile(0.95)),
    "p99_cps": float(df['segment_character_per_second'].quantile(0.99))
}

with open(r"d:\Josh Talks\pmi\q2_stats_summary.json", "w", encoding="utf-8") as f:
    json.dump(stats_out, f, indent=2)

print("\nSaved stats to d:\\Josh Talks\\pmi\\q2_stats_summary.json")
