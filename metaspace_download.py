import pandas as pd
from metaspace import SMInstance

def download_dataset_results(dataset_id, database=None, version=None):
    """
    Download the results of a specified dataset and save them as a CSV file.

    Args:
        dataset_id (str): The ID of the dataset to process. 
                          The ID is the last part of the dataset URL. 
                          For example, in the URL `https://metaspace2020.org/dataset/2022-08-05_17h28m56s`,
                          the `dataset_id` is `2022-08-05_17h28m56s`.
        database (str, optional): The name of the database to filter. If not provided, all databases will be included.
        version (str, optional): The version of the database to filter. If not provided, all versions will be included.

    Returns:
        pd.DataFrame: A DataFrame containing the results.

    Behavior:
        - If only `database` is provided and it has multiple versions, the results will be combined into one file named `{database}_all_versions.csv`.
        - If the `database` has only one version, the file will be named `{database}_{version}.csv`.
        - If no `database` is provided, it will download all the annotations file from all database and the file will be named `all_databases.csv`.
    """
    # Retrieve the dataset object
    sm = SMInstance()
    dataset = sm.dataset(id=dataset_id)

    # Step 1: Generate annotation statistics table
    databases = dataset.database_details
    # Extract database names and versions
    database_info = []
    for db in databases:
        db_str = str(db)
        name_version = db_str.split(":")[1:3]
        name_version = [nv.strip(">") for nv in name_version]  # Remove trailing '>'
        database_info.append(" ".join(name_version))

    # Check if the specified database exists
    if database:
        matched_databases = [db for db in database_info if db.startswith(database)]
        if not matched_databases:
            print(f"Could not find database: {database}")
            print("Available databases and versions:")
            for db in database_info:
                print(db)
            return None
        elif len(matched_databases) > 1 and version is None:
            print(f"Warning: Multiple versions found for database {database}.")
            print("Available versions:")
            for db in matched_databases:
                print(db)

    # Initialize the results DataFrame
    results_df = pd.DataFrame()
    
    # Process the specified database names and versions
    for db in database_info:
        name, ver = db.split()
        if (database is None or database == name) and (version is None or version == ver):
            print(f"Processing database: {name}, version: {ver}")
            result = dataset.results(database=(name, ver))
            result_df = pd.DataFrame(result)
            result_df["Database"] = name
            result_df["Version"] = ver
            results_df = pd.concat([results_df, result_df], ignore_index=True)
    
    # Extract the content between two '+' symbols in the `ion` column and prepend a '+'
    if 'ion' in results_df.columns:
        results_df['Adduct'] = results_df['ion'].str.extract(r'(\+[A-Za-z0-9]+)')
    # Rename the `intensity` column to `maxIntensity`
    if 'intensity' in results_df.columns:
        results_df.rename(columns={'intensity': 'maxIntensity'}, inplace=True)

    # Dynamically generate the CSV file name
    if database:
        matched_versions = [db.split()[1] for db in database_info if db.startswith(database)]
        if len(matched_versions) > 1:
            filename = f"{database}_all_versions.csv"
        else:
            filename = f"{database}_{matched_versions[0]}.csv"
    else:
        filename = "all_databases.csv"
    
    # Save the results to a CSV file
    results_df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")
    return results_df

if __name__ == "__main__":
    # Example usage
    dataset_id = "2022-08-05_17h28m56s"
    database = "KEGG"  # Optional, set to None to download all databases
    version = None  # Optional, set to None to include all versions

    # Call the function to download results
    data = download_dataset_results(dataset_id, database, version)

    # Print the resulting DataFrame's columns and column count
    if data is not None:
        print(data.columns)
        print(f"Number of columns: {len(data.columns)}")