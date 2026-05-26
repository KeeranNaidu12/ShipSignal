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
    print("Checking missing values:")
    print(df.isnull().sum())
    df = df.dropna(subset=['Year'])
    print(f"After dropping missing years: {df.shape}")

    # Fill missing publisher values
    df['Publisher'] = df['Publisher'].fillna('Unknown')
    print(f"Filled missing publishers: {df['Publisher'].isna().sum()} remaining")

    # Convert year to integer
    df['Year'] = df['Year'].astype(int)

    # Show year distribution and cap at 2016
    print("Year distribution (tail):")
    print(df['Year'].value_counts().sort_index().tail(10))
    df = df[df['Year'] <= 2016]
    print(f"After capping at 2016: {df.shape}")

    # Check for and remove exact duplicate rows
    print("Checking for exact duplicates...")
    before = df.shape[0]
    df = df.drop_duplicates()
    print(f"Removed {before - df.shape[0]} exact duplicate rows.")

    # Document deduplication: show all duplicate Name+Platform+Genre groups before and after
    print()
    print("Deduplication Documentation")
    print("==========================")
    # Find all duplicate Name+Platform+Genre groups
    dup_groups = df[df.duplicated(subset=['Name', 'Platform', 'Genre'], keep=False)]
    if dup_groups.empty:
        print("No duplicate Name+Platform+Genre groups found.")
    else:
        print("All duplicate Name + Platform + Genre groups before deduplication:")
        print(dup_groups[['Name', 'Platform', 'Genre', 'Year', 'Global_Sales']].sort_values(['Name', 'Platform', 'Genre', 'Year']).to_string())
        # Show Madden NFL 13 and Need for Speed: Most Wanted specifically if present
        for game in ['Madden NFL 13', 'Need for Speed: Most Wanted']:
            game_dups = dup_groups[dup_groups['Name'] == game]
            if not game_dups.empty:
                print()
                print(f"{game} duplicates before deduplication:")
                print(game_dups[['Name', 'Platform', 'Genre', 'Year', 'Global_Sales']].to_string())

    print()
    print("Merging duplicate Name+Platform+Genre rows (keeping highest Global_Sales, dropping others with different years)...")
    df = df.sort_values('Global_Sales', ascending=False)
    df = df.drop_duplicates(subset=['Name', 'Platform', 'Genre'], keep='first')

    # Show after deduplication for all affected games
    if dup_groups.empty:
        print("No duplicates to show after deduplication.")
    else:
        print()
        print("All duplicate Name+Platform+Genre groups after deduplication:")
        print(df[df['Name'].isin(dup_groups['Name'])][['Name', 'Platform', 'Genre', 'Year', 'Global_Sales']].sort_values(['Name', 'Platform', 'Genre', 'Year']).to_string())
        for game in ['Madden NFL 13', 'Need for Speed: Most Wanted']:
            game_after = df[df['Name'] == game]
            if not game_after.empty:
                print()
                print(f"{game} after deduplication:")
                print(game_after[['Name', 'Platform', 'Genre', 'Year', 'Global_Sales']].to_string())
    print("==========================\n")

    df = df.groupby(['Name', 'Platform', 'Genre', 'Year'], as_index=False).agg({
        'Publisher': 'first',
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

    # Map platforms to broader groups for analysis
    print("Consolidating platforms into 6 groups...")
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
    print("Platforms after mapping:", df['Platform'].unique())



    # Add decade column for trend analysis
    print("Adding decade column for trend analysis...")
    df['Decade'] = (df['Year'] // 10 * 10).astype(int)
    print("Decade distribution:")
    print(df['Decade'].value_counts().sort_index())

    # Print cleaning summary
    print()
    print("CLEANING SUMMARY")
    print("================")
    print(f"Original rows:  16598")
    print(f"Final rows:     {df.shape[0]}")
    print(f"Rows removed:   {16598 - df.shape[0]}")
    print(f"Genres:         {df['Genre'].nunique()}")
    print(f"Platforms:      {df['Platform'].nunique()}")
    print(f"Year range:     {df['Year'].min()} - {df['Year'].max()}")
    print("================")

    # Save cleaned dataset
    print()
    print("Saving cleaned dataset...")
    df.to_csv('data/cleaned_vgsales.csv', index=False)
    print("Cleaning complete. Saved to data/cleaned_vgsales.csv")

if __name__ == "__main__":
    clean()