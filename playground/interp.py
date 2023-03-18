import pandas as pd

main_data = [
    (pd.to_datetime('2020-01-01'), 2.0, ),
    (pd.to_datetime('2020-01-05'), 5.0, ),
    (pd.to_datetime('2020-01-08'), 6.0, ),
]
main_df = pd.DataFrame(main_data, columns=['timestamp', 'value'])

overlay_data = [
    (pd.to_datetime('2020-01-04'), ),
    (pd.to_datetime('2020-01-05'), ),
    (pd.to_datetime('2020-01-07'), ),
]
overlay_df = pd.DataFrame(overlay_data, columns=['timestamp', ])

df = (pd.concat([overlay_df, main_df])
      .drop_duplicates(subset='timestamp', keep='last')
      .sort_values(by='timestamp')
      .set_index('timestamp')
      .astype(float)
      .interpolate(method='index'))
overlay_result = df.loc[overlay_df.timestamp] if df is not None else pd.DataFrame()
print(overlay_result)
