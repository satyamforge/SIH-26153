import os
import glob
import numpy as np
import pandas as pd
import joblib


class LiveTrafficSimulator:

    def __init__(
        self,
        dataset_folder="dataset",
        model_path="model/attack_detector.pkl",
        feature_path="model/features.pkl",
        batch_size=1000
    ):

        self.dataset_folder = dataset_folder
        self.batch_size = batch_size

        # Load trained model
        self.model = joblib.load(model_path)

        # Load expected features
        self.features = joblib.load(feature_path)

        # Find CSV files
        self.csv_files = glob.glob(
            os.path.join(dataset_folder, "*.csv")
        )

        if not self.csv_files:
            raise FileNotFoundError(
                "No CSV files found inside dataset folder."
            )

        # Current traffic source
        self.current_file = None

        # Current dataframe
        self.df = None

        # Current position in traffic
        self.position = 0

        # Random number generator
        self.rng = np.random.default_rng()

        # Automatically start with a random file
        self.select_new_file()


    def select_new_file(self):

        """
        Select a new CIC-IDS2017 traffic source.
        """

        self.current_file = self.rng.choice(
            self.csv_files
        )

        print(
            "Selected traffic source:",
            os.path.basename(self.current_file)
        )

        # Load dataset
        self.df = pd.read_csv(
            self.current_file,
            low_memory=False
        )

        self.df.columns = self.df.columns.str.strip()

        # Shuffle starting position so every simulation
        # does not start at exactly the same place.
        if len(self.df) > self.batch_size:

            self.position = self.rng.integers(
                0,
                len(self.df) - self.batch_size
            )

        else:
            self.position = 0


    def prepare_features(self, batch):

        """
        Convert network traffic into the 70 features
        expected by the trained Random Forest.
        """

        X = pd.DataFrame(index=batch.index)

        for feature in self.features:

            if feature in batch.columns:

                X[feature] = pd.to_numeric(
                    batch[feature],
                    errors="coerce"
                )

            else:

                # Missing feature
                X[feature] = 0

        # Remove invalid values
        X = X.replace(
            [np.inf, -np.inf],
            np.nan
        )

        X = X.fillna(0)

        return X


    def get_next_batch(self):

        """
        Return the next simulated traffic batch.

        Returns:
            probabilities
            traffic_count
            source_name
        """

        # If we reached the end,
        # start another traffic source.
        if (
            self.df is None
            or self.position >= len(self.df)
        ):

            self.select_new_file()


        end_position = min(
            self.position + self.batch_size,
            len(self.df)
        )

        batch = self.df.iloc[
            self.position:end_position
        ].copy()

        self.position = end_position

        # Convert traffic to model features
        X = self.prepare_features(batch)

        # AI prediction
        probabilities = self.model.predict_proba(
            X
        )[:, 1]

        return (
            probabilities,
            len(batch),
            os.path.basename(self.current_file)
        )


    def reset(self):

        """
        Start a completely new simulation.
        """

        self.select_new_file()