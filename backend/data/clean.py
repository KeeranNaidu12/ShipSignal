import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def clean():
    # Load the raw dataset
    print("Loading dataset...")
    df = pd.read_csv('data/vgsales.csv')
    print(f"Original shape: {df.shape}")

    # Check and drop rows with missing year values
    print("\nChecking missing values:")
    print(df.isnull().sum())
    df = df.dropna(subset=['Year'])
    print(f"After dropping missing years: {df.shape}")

    # Fill missing publisher values
    df['Publisher'] = df['Publisher'].fillna('Unknown')
    print(f"Filled missing publishers: {df['Publisher'].isna().sum()} remaining")

    # Convert year to integer
    df['Year'] = df['Year'].astype(int)

    # Show year distribution and cap at 2016
    print("\nYear distribution (tail):")
    print(df['Year'].value_counts().sort_index().tail(10))
    df = df[df['Year'] <= 2016]
    print(f"After capping at 2016: {df.shape}")

    # Check for and remove exact duplicate rows
    print("\nChecking for exact duplicates...")
    before = df.shape[0]
    df = df.drop_duplicates()
    print(f"Removed {before - df.shape[0]} exact duplicate rows.")

    # Document deduplication
    print("\nDeduplication Documentation")
    print("==========================")
    dup_groups = df[df.duplicated(subset=['Name', 'Platform', 'Genre'], keep=False)]
    if dup_groups.empty:
        print("No duplicate Name+Platform+Genre groups found.")
    else:
        print("Duplicate Name+Platform+Genre groups before deduplication:")
        print(dup_groups[['Name', 'Platform', 'Genre', 'Year', 'Global_Sales']].sort_values(['Name', 'Platform', 'Genre', 'Year']).to_string())
        for game in ['Madden NFL 13', 'Need for Speed: Most Wanted']:
            game_dups = dup_groups[dup_groups['Name'] == game]
            if not game_dups.empty:
                print(f"\n{game} duplicates before deduplication:")
                print(game_dups[['Name', 'Platform', 'Genre', 'Year', 'Global_Sales']].to_string())

    # Merge duplicate Name+Platform+Genre rows by summing sales
    print("\nMerging duplicate Name+Platform+Genre rows...")
    df = df.groupby(
        ['Name', 'Platform', 'Genre', 'Year', 'Publisher'],
        as_index=False
    ).agg({
        'NA_Sales':    'sum',
        'EU_Sales':    'sum',
        'JP_Sales':    'sum',
        'Other_Sales': 'sum',
        'Global_Sales':'sum',
    })
    print(f"After merging: {df.shape}")
    print("Sample — Need for Speed: Most Wanted:")
    nfs = df[df['Name'] == 'Need for Speed: Most Wanted']
    print(nfs[['Name', 'Platform', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Global_Sales']].to_string())

    # Consolidate platforms into 6 groups
    print("\nConsolidating platforms into 6 groups...")
    platform_map = {
        'PS4': 'PlayStation', 'PS3': 'PlayStation', 'PS2': 'PlayStation',
        'PS': 'PlayStation', 'PSP': 'PlayStation', 'PSV': 'PlayStation',
        'XOne': 'Xbox', 'X360': 'Xbox', 'XB': 'Xbox',
        'Wii': 'Nintendo', 'WiiU': 'Nintendo', 'DS': 'Nintendo',
        '3DS': 'Nintendo', 'GBA': 'Nintendo', 'SNES': 'Nintendo',
        'N64': 'Nintendo', 'GC': 'Nintendo',
        'PC': 'PC',
    }
    df['Platform'] = df['Platform'].map(lambda x: platform_map.get(x, 'Other'))
    print(f"Platforms after mapping: {df['Platform'].unique()}")
    print(f"Platform distribution:\n{df['Platform'].value_counts()}")

    # Filter to valid genres only
    print("\nFiltering to valid genres only...")
    print(f"Genres before filter: {df['Genre'].unique()}")
    print(f"Genre counts before filter:\n{df['Genre'].value_counts()}")
    valid_genres = [
        'Action', 'Adventure', 'Fighting', 'Misc', 'Platform',
        'Puzzle', 'Racing', 'Role-Playing', 'Shooter',
        'Simulation', 'Sports', 'Strategy'
    ]
    df = df[df['Genre'].isin(valid_genres)]
    print(f"Genres after filter: {df['Genre'].unique()}")
    print(f"After genre filter: {df.shape}")
    print(f"Genre distribution:\n{df['Genre'].value_counts()}")

    # Add decade column for trend analysis
    print("\nAdding decade column for trend analysis...")
    df['Decade'] = (df['Year'] // 10 * 10).astype(int)
    print(f"Decade distribution:\n{df['Decade'].value_counts().sort_index()}")

    # Cleaning summary
    print(f"\n{'='*40}")
    print(f"CLEANING SUMMARY")
    print(f"{'='*40}")
    print(f"Original rows:  16598")
    print(f"Final rows:     {df.shape[0]}")
    print(f"Rows removed:   {16598 - df.shape[0]}")
    print(f"Genres:         {df['Genre'].nunique()}")
    print(f"Platforms:      {df['Platform'].nunique()}")
    print(f"Year range:     {df['Year'].min()} - {df['Year'].max()}")
    print(f"{'='*40}")

    # Save cleaned dataset
    print("\nSaving cleaned dataset...")
    df.to_csv('data/cleaned_vgsales.csv', index=False)
    print("Cleaning complete — saved to data/cleaned_vgsales.csv")

if __name__ == "__main__":
    clean()