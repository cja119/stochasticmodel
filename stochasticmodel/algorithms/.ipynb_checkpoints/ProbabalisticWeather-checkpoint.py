import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import random
from matplotlib import rcParams


class ProbabilisticWeatherModel:
    def __init__(self, file_path, n_samples, n_points, n_bins=3):
        self.file_path = file_path
        self.weather_data = pd.read_pickle(file_path)
        self.samples = []
        self.sample_means = []
        self.n_bins = n_bins
        self.indexed_bins = {f'Bin {i+1}': [] for i in range(n_bins)}
        self.monte_carlo_samples(n_samples, n_points)
        self.calculate_sample_means()
        data = np.array(self.sample_means)
        self.mean = np.mean(data)
        self.std_dev = np.std(data)
        rcParams['font.family'] = 'serif'
        rcParams['font.serif'] = ['CMU Serif'] + rcParams['font.serif']
        rcParams['figure.dpi'] = 150
        self.colors = [
            "#232333", "#000080", "#0000CD", "#008080", "#232333",
            "#C71585", "#DC143C", "#006400", "#40E0D0", "#EE82EE",
            "#7B68EE", "#FF0000", "#FF8C00", "#00FF7F", "#F5F5F5",
            "#00BFFF", "#F0E68C", "#AFEEEE", "#FFB6C1", "#E6E6FA",
            "#FA8072", "#FFA500", "#98FB98"
        ]
        self.alpha = 0.75
        self.linewidth = 1.25
        self.ks_test()
        self.bin_samples()

    def monte_carlo_samples(self, n_samples, n_points):
        df = self.weather_data.copy()
        max_start_index = len(df) - n_points
        df_hold = df.copy()
        maxiter = n_samples * 10
        itercount = 0
        while len(self.samples) <= n_samples:
            start_index = np.random.randint(0, max_start_index + 1)
            sample = df.iloc[start_index:start_index + n_points]
            df.drop(df.index[start_index:start_index + n_points], inplace=True)

            if not sample.empty and not sample.isnull().values.any() and len(sample) == n_points:
                self.samples.append(sample)
            itercount += 1
            if itercount > maxiter:
                print('Not enough values, having to re-sample the original dataset to generate more samples.')
                df = df_hold.copy()
                itercount = 0

    def calculate_sample_means(self):
        self.sample_means = [sample.mean().values[0] / 11.88 for sample in self.samples]

    def plot_histogram(self):
        plt.hist(self.sample_means, bins=20, edgecolor='black')
        plt.xlim(0, 1)
        plt.title('Histogram of Sample Means')
        plt.xlabel('Mean Value')
        plt.ylabel('Frequency')
        plt.show()

    def ks_test(self):
        data = np.array(self.sample_means)
        stat, p_value = stats.kstest(data, 'norm', args=(self.mean, self.std_dev))
        print(f"KS Statistic: {stat}")
        print(f"P-value: {p_value}")

        alpha = 0.05
        if p_value > alpha:
            print('Sample follows a normal distribution (fail to reject H0)')
        else:
            print('Sample does not follow a normal distribution (reject H0)')

    def plot_discretized_normal_distribution(self):
        data = np.array(self.sample_means)
        plt.hist(self.sample_means, bins=10, edgecolor='black', density=True, alpha=0.6, color='g')

        xmin, xmax = plt.xlim()
        x = np.linspace(0, 1, 100)
        p = stats.norm.pdf(x, self.mean, self.std_dev)
        plt.plot(x, p, 'k', linewidth=2)

        mean = self.mean
        std_dev = self.std_dev

        bin_edges = np.linspace(0, 1, self.n_bins + 1) + (self.mean - 0.5)
        bin_edges[0], bin_edges[-1] = 0, 1  # Ensure the bins are within the range [0, 1]
        bin_heights = [
            stats.norm.cdf(bin_edges[i + 1], mean, std_dev) - stats.norm.cdf(bin_edges[i], mean, std_dev)
            for i in range(len(bin_edges) - 1)
        ]
        bin_edges = np.array(bin_edges)
        bin_heights = np.array(bin_heights) / (bin_edges[1:] - bin_edges[:-1])

        for i in range(len(bin_edges) - 1):
            plt.bar(
                (bin_edges[i] + bin_edges[i + 1]) / 2, bin_heights[i],
                width=bin_edges[i + 1] - bin_edges[i], alpha=0.5, color='b', edgecolor='black'
            )

        title = "Fit results: mu = %.2f,  std = %.2f" % (mean, std_dev)
        plt.title(title)
        plt.xlabel('Mean Value')
        plt.ylabel('Density')
        plt.show()

    def bin_samples(self):
        bin_edges = np.linspace(0, 1, self.n_bins + 1) + (self.mean - 0.5)
        bin_edges[0], bin_edges[-1] = 0, 1  # Ensure the bins are within the range [0, 1]
        bin_labels = [f'Bin {i+1}' for i in range(self.n_bins)]
        self.bin_labels = bin_labels
        bin_probabilities = [
            stats.norm.cdf(bin_edges[i + 1], self.mean, self.std_dev) - stats.norm.cdf(bin_edges[i], self.mean, self.std_dev)
            for i in range(len(bin_edges) - 1)
        ]
        self.bin_probabilities = [i / sum(bin_probabilities) for i in bin_probabilities]
        for sample in self.samples:
            sample_mean = sample.mean().values[0] / 11.88
            for i in range(len(bin_edges) - 1):
                if bin_edges[i] <= sample_mean < bin_edges[i + 1]:
                    self.indexed_bins[bin_labels[i]].append(sample)
                    break

    def generate_probabilistic_samples(self, n_stages, n_stochastics, stage_duration, master_branches):
        self.n_stages = n_stages
        self.n_stochastics = n_stochastics
        self.stage_duration = stage_duration
        samples = {}
        probabilities = np.ones((n_stochastics ** n_stages, n_stages + 1))
        master_branches_count = np.zeros(n_stages + 1, dtype=int)
        
        # Precompute the random samples for each bin to avoid repeated sampling
        precomputed_samples = {label: random.sample(self.indexed_bins[label], n_stochastics) for label in self.bin_labels}
        
        for s in range(n_stochastics ** n_stages):
            for t in range((n_stages + 1) * stage_duration):
                stage = t // stage_duration
                if master_branches[(s, stage)] == 1:
                    if t % stage_duration == 0:
                        bin_label = self.bin_labels[master_branches_count[stage]]
                        random_sample = precomputed_samples[bin_label][master_branches_count[stage]]
                        if t >= stage_duration:
                            probabilities[s, stage] = probabilities[s, stage - 1] * self.bin_probabilities[master_branches_count[stage]]
                        master_branches_count[stage] += 1
                        if master_branches_count[stage] >= n_stochastics:
                            master_branches_count[stage] = 0
                    samples[(s, t)] = random_sample.iloc[t % stage_duration][0]
                else:
                    if t % stage_duration == 0:
                        probabilities[s, stage] = probabilities[s - 1, stage]
                    samples[(s, t)] = samples[(s - 1, t)]
        
        self.samples = samples
        self.probabilities = probabilities[:, -1]

    def plot_samples(self):
        count = 0
        for s in range(self.n_stochastics ** self.n_stages):
            sample_values = [self.samples[(s, t)] for t in range((self.n_stages + 1) * self.stage_duration)]
            plt.plot(sample_values, label=f'Sample {s+1}', color=self.colors[count])
            count += 1
            if count >= len(self.colors):
                count = 0
        plt.title('Probabilistic Samples')
        plt.xlabel('Time')
        plt.ylabel('Sample Value')
        plt.show()
