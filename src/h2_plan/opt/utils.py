"""
This module contains the plotting functions for the stochastic model.
"""
from matplotlib.pyplot import (
    subplots, show, legend, gca, bar, xticks, fill_between, minorticks_on, tick_params
)
from matplotlib.ticker import MaxNLocator
from numpy import array, zeros, size, floor, max


def wind_energy(self):
    """
    Plot the energy produced by wind and solar turbines over time.
    """
    # Initialize the subplots environment and employ the custom color scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap

    # Initialize a line counter to update the legend entry and color.
    line_counter = 0

    # Initialize capacity factor dictionary for wind and solar.
    self.cap_factor = {'wind': [], 'solar': []}

    # Loop through each scenario to plot energy data.
    for s in self.instance.scenario:
        power_wind = array(len(self.instance.time))
        power_solar = array(len(self.instance.time))

        # Calculate wind energy if wind turbines are present.
        if self.instance.wind:
            power_wind = array([
                self.instance.turbine_power[(st)] for st in self.instance.full_set
                for _ in range(st[2]) if st[0] == s
            ]) * int(self.instance.capacity_number_turbines.value)
            time = array([
                (st[1], st[2]) for st in self.instance.full_set
                for _ in range(st[2]) if st[0] == s
            ])
            self.cap_factor['wind'].append(
                sum(power_wind) / (max(power_wind) * len(power_wind))
            )

        # Calculate solar energy if solar panels are present.
        if self.instance.solar:
            power_solar = array([
                0.0036 * self.instance.solar_power[(st)] for st in self.instance.full_set
                for _ in range(st[2]) if st[0] == s
            ]) * int(self.instance.capacity_solar.value)
            time = array([
                (st[1], st[2]) for st in self.instance.full_set
                for _ in range(st[2]) if st[0] == s
            ])
            self.cap_factor['solar'].append(
                sum(power_solar) / (max(power_solar) * len(power_solar))
            )

        # Plot the combined wind and solar energy.
        ax.plot(
            range(time[0][0], time[-1][0] + time[-1][1]),
            power_wind + power_solar,
            color=cmap[line_counter],
            linewidth=self.linewidth
        )

        # Update the line counter.
        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0

    # Update the axes labels and title.
    ax.set(
        xlabel='Time [h]',
        ylabel='Energy [GJ/h]',
        title='Renewable Energy against Time'
    )
    ax.set_ylim(bottom=0)

    # Update plot settings.
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Update the hyperparameters for the tick markers.
    tick_params(
        which='minor',
        length=2,
        width=1,
        direction='out',
        labelsize=0
    )

    # Display the plot.
    show()


def grid_energy(self):
    """
    Plot the energy supplied by the grid over time.
    """
    # Initialize the subplots environment and employ the custom color scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap

    # Initialize a line counter to update the legend entry and color.
    line_counter = 0

    # Loop through each scenario to plot grid energy data.
    for s in self.instance.scenario:
        time = [
            (st[1], st[2]) for st in self.instance.full_set
            for _ in range(st[2]) if st[0] == s
        ]
        ax.plot(
            range(time[0][0], time[-1][0] + time[-1][1]),
            array([self.instance.energy_grid[(s, t)].value for t in time]),
            color=cmap[line_counter],
            linewidth=self.linewidth
        )

        # Update the line counter.
        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0

    # Update the axes labels and title.
    ax.set(
        xlabel='Time [h]',
        ylabel='Energy [GJ/h]',
        title='Grid Energy against Time'
    )
    ax.set_ylim(bottom=0)

    # Update plot settings.
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Update the hyperparameters for the tick markers.
    tick_params(
        which='minor',
        length=2,
        width=1,
        direction='out',
        labelsize=0
    )

    # Display the plot.
    show()


def curtailed_energy(self):
    """
    Plot the curtailed energy over time.
    """
    # Initialize the subplots environment and employ the custom color scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap

    # Initialize a line counter to update the legend entry and color.
    line_counter = 0

    # Loop through each scenario to plot curtailed energy data.
    for s in self.instance.scenario:
        time = [
            (st[1], st[2]) for st in self.instance.full_set
            for _ in range(st[2]) if st[0] == s
        ]
        if self.instance.grid_wheel:
            y = array([
                self.instance.energy_curtailed[(s, t)].value +
                self.instance.energy_wheeled[(s, t)].value for t in time
            ])
        else:
            y = array([
                self.instance.energy_curtailed[(s, t)].value for t in time
            ])
        ax.plot(
            range(time[0][0], time[-1][0] + time[-1][1]),
            y,
            color=cmap[line_counter],
            linewidth=self.linewidth
        )

        # Update the line counter.
        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0

    # Update the axes labels and title.
    ax.set(
        xlabel='Time [h]',
        ylabel='Energy [GJ/h]',
        title='Curtailed Energy against Time'
    )

    # Update plot settings.
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Update the hyperparameters for the tick markers.
    tick_params(
        which='minor',
        length=2,
        width=1,
        direction='out',
        labelsize=0
    )

    # Display the plot.
    show()


def hydrogen_storage_tank_level(self):
    """
    Plot the hydrogen storage tank level over time.
    """
    # Initialize the subplots environment and employ the custom color scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap

    # Initialize a line counter to update the legend entry and color.
    line_counter = 0

    # Loop through each scenario to plot hydrogen storage data.
    for s in self.instance.scenario:
        time = [
            (st[1], st[2]) for st in self.instance.full_set
            for _ in range(st[2]) if st[0] == s
        ]
        ax.plot(
            range(time[0][0], time[-1][0] + time[-1][1]),
            array([self.instance.gh2_storage[(s, t)].value for t in time]),
            color=cmap[line_counter],
            linewidth=self.linewidth
        )

        # Update the line counter.
        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0

    # Update the axes labels and title.
    ax.set(
        xlabel='Time [h]',
        ylabel='Hydrogen Storage at Origin [GJ]',
        title='Hydrogen Storage Against Time'
    )
    ax.set_ylim(bottom=0)

    # Update plot settings.
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Update the hyperparameters for the tick markers.
    tick_params(
        which='minor',
        length=2,
        width=1,
        direction='out',
        labelsize=0
    )

    # Display the plot.
    show()

def origin_storage_tank_levels(self):
    """
    Plots the storage levels of vectors at the origin over time.
    """
    # Initialize the subplots environment and apply the custom color scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap

    # Line counter to cycle through colors.
    line_counter = 0

    for s in self.instance.scenario:
        # Extract time intervals for the current scenario.
        time = [(st[1], st[2]) for st in self.instance.full_set for _ in range(st[2]) if st[0] == s]
        for i in self.instance.vectors:
            # Plot the storage levels for each vector.
            ax.plot(
                range(time[0][0], time[-1][0] + time[-1][1]),
                array([self.instance.vector_storage_origin[(s, t[0], t[1]), i].value for t in time]),
                label=i,
                color=cmap[line_counter],
                linewidth=self.linewidth
            )
        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0

    # Update the axes.
    ax.set(
        xlabel='Time [h]',
        ylabel='Vector Storage at Origin [TJ]',
        title='Origin Vector Storage Against Time'
    )
    ax.set_ylim(bottom=0)

    # Update plot settings.
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Update the hyperparameters for the tick markers.
    tick_params(
        which='minor',
        length=2,
        width=1,
        direction='out',
        labelsize=0
    )

    # Display the plot.
    show()


def hydrogen_production(self):
    """
    Plots the hydrogen production over time.
    """
    # Initialize the subplots environment and apply the custom color scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap

    # Line counter to cycle through colors.
    line_counter = 0

    for s in self.instance.scenario:
        # Extract time intervals for the current scenario.
        time = [(st[1], st[2]) for st in self.instance.full_set for _ in range(st[2]) if st[0] == s]
        y = zeros(int(size(time) / 2))

        for i in self.instance.electrolysers:
            # Update the y array for stacked plotting.
            y += array([self.instance.energy_electrolysers[(s, t[0], t[1]), i].value for t in time])

            # Plot the hydrogen production.
            ax.plot(
                range(time[0][0], time[-1][0] + time[-1][1]),
                y,
                label=i,
                color=cmap[line_counter],
                linewidth=self.linewidth
            )

        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0

    # Update the axes.
    ax.set(
        xlabel='Time [h]',
        ylabel='Hydrogen Production [GJ/h]',
        title='Hydrogen Production Against Time'
    )
    ax.set_ylim(bottom=0)

    # Update plot settings.
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Update the hyperparameters for the tick markers.
    tick_params(
        which='minor',
        length=2,
        width=1,
        direction='out',
        labelsize=0
    )

    # Display the plot.
    show()


def vector_production(self):
    """
    Plots the production of vectors over time.
    """
    # Initialize the subplots environment and apply the custom color scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap

    # Line counter to cycle through colors.
    line_counter = 0

    for s in self.instance.scenario:
        # Extract time intervals for the current scenario.
        time = [(st[1], st[4], st[5]) for st in self.instance.vector_set_time for _ in range(st[2]) if st[3] == s]
        y = zeros(int(size(time) / 3))

        for i in self.instance.vectors:
            # Update the y array for stacked plotting.
            y += array([self.instance.energy_vector_production_flux[(s, t[1], t[2]), i].value for t in time])

            # Plot the vector production.
            ax.plot(
                [t[0] for t in time],
                y,
                label=i,
                color=cmap[line_counter],
                linewidth=self.linewidth
            )

        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0

    # Update the axes.
    ax.set(
        xlabel='Time [h]',
        ylabel='Vector Production [GJ/h]',
        title='Vector Production Against Time'
    )

    # Update plot settings.
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Update the hyperparameters for the tick markers.
    tick_params(
        which='minor',
        length=2,
        width=1,
        direction='out',
        labelsize=0
    )

    # Display the plot.
    show()


def active_trains(self):
    """
    Plots the number of active trains over time.
    """
    # Initialize the subplots environment and apply the custom color scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap

    # Line counter to cycle through colors.
    line_counter = 0

    for s in self.instance.scenario:
        # Extract time intervals for the current scenario.
        time = [(st[1], st[4], st[5]) for st in self.instance.vector_set_time for _ in range(st[2]) if st[3] == s]
        y = zeros(int(size(time) / 3))

        for i in self.instance.vectors:
            # Update the y array for stacked plotting.
            y += array([self.instance.number_active_trains[(s, t[1], t[2]), i].value for t in time])

            # Plot the number of active trains.
            ax.plot(
                [t[0] for t in time],
                y,
                label=i,
                color=cmap[line_counter],
                linewidth=self.linewidth
            )

        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0

    # Update the axes.
    ax.set(
        xlabel='Time [h]',
        ylabel='Number Active Trains',
        title='Number Active Trains Against Time'
    )
    ax.set_ylim(bottom=0)

    # Update plot settings.
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Update the hyperparameters for the tick markers.
    tick_params(
        which='minor',
        length=2,
        width=1,
        direction='out',
        labelsize=0
    )

    # Display the plot.
    show()


def objective_cdf(self):
    """
    Plots the cumulative distribution function (CDF) of the objective values.
    """
    # Initialize the subplots environment and apply the custom color scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap
    y = []

    for s in self.instance.scenario:
        # Calculate the discounted demand.
        discounted_demand = (
            (8760 / self.instance.end_time_index) *
            self.instance.amortisation_plant *
            sum(
                sum(
                    (self.instance.leaf_nodes[s, t, d]) *
                    self.instance.energy_vector_production_flux[(s_v, t_v, d_v), q].value * d
                    for s, t, d, s_v, t_v, d_v in self.instance.vector_set_time if s_v == s
                ) / 120
                for q in self.instance.vectors
            )
        )
        y.append(1000 * (self.instance.CAPEX.value + self.instance.OPEX[s].value) / discounted_demand)

    # Plot the histogram of objective values.
    ax.hist(y, bins=7, alpha=0.7, color=cmap[0], edgecolor='black')

    # Add a legend to the plot.
    ax.legend()

    # Update the axes.
    ax.set(
        xlabel='Average Hydrogen (equivalent) Production [kg/h]',
        ylabel='Probability Density',
        title='Probability Conditioned Objective Values'
    )

    # Update plot settings.
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Update the hyperparameters for the tick markers.
    tick_params(
        which='minor',
        length=2,
        width=1,
        direction='out',
        labelsize=0
    )

    # Display the plot.
    show()

def LCOH_contributions(self, threshold):
    """
    Plot the Levelized Cost of Hydrogen (LCOH) contributions as a bar chart.

    Args:
        threshold (float): Minimum contribution value to include in the chart.
    """
    # Calculate discounted demand
    self.instance.discounted_demand = (
        (8760 / self.instance.end_time_index)
        * self.instance.amortisation_plant
        * sum(
            sum(
                (self.instance.leaf_nodes[s, t, d])
                * self.instance.energy_vector_production_flux[(s_v, t_v, d_v), q].value
                * d
                for s, t, d, s_v, t_v, d_v in self.instance.vector_set_time
            )
            / 120
            for q in self.instance.vectors
        )
    ) / len(self.instance.scenario.data())

    # Initialize categories and contributions
    categories = ["Total LCOH"]
    OPEX = [
        (10**3)
        * sum(self.instance.OPEX[s].value / len(self.instance.scenario) for s in self.instance.scenario)
        / self.instance.discounted_demand
    ]
    CAPEX = [(10**3) * self.instance.CAPEX.value / self.instance.discounted_demand]

    # Add wind turbine contributions
    if self.instance.wind:
        categories.append("Wind Turbines")
        OPEX.append(
            (10**3)
            * self.instance.turbine_unit_operating_cost
            * self.instance.capacity_number_turbines.value
            * self.instance.amortisation_plant
            / self.instance.discounted_demand
        )
        CAPEX.append(
            (10**3)
            * self.instance.turbine_unit_capital_cost
            * self.instance.capacity_number_turbines.value
            * self.instance.amortisation_turbine
            / self.instance.discounted_demand
        )

    # Add solar panel contributions
    if self.instance.solar:
        categories.append("Solar Panels")
        OPEX.append(
            (10**3)
            * self.instance.solar_unit_operating_cost
            * self.instance.capacity_solar.value
            * self.instance.amortisation_plant
            / self.instance.discounted_demand
        )
        CAPEX.append(
            (10**3)
            * self.instance.solar_unit_capital_cost
            * self.instance.capacity_solar.value
            * self.instance.amortisation_solar
            / self.instance.discounted_demand
        )

    # Add grid connection contributions
    if self.instance.grid_connection.value:
        grid_contribution = (
            (10**3)
            * sum(self.instance.net_grid[s].value / len(self.instance.scenario) for s in self.instance.scenario)
            * self.instance.LCAP
            * self.instance.grid_energy_factor.value
            * (8760 / self.instance.end_time_index)
            * self.instance.amortisation_plant
            / self.instance.discounted_demand
        )
        if grid_contribution >= threshold:
            categories.append("Grid Connection")
            OPEX.append(grid_contribution)
            CAPEX.append(0)

    # Add fuel cell contributions
    fuel_cell_contribution = (
        (10**3)
        * self.instance.fuel_cell_unit_capital_cost
        * self.instance.capacity_HFC.value
        * self.instance.amortisation_fuel_cell
        / self.instance.discounted_demand
    )
    if fuel_cell_contribution >= threshold:
        categories.append("Fuel Cell")
        OPEX.append(
            (10**3)
            * self.instance.fuel_cell_unit_operating_cost
            * self.instance.capacity_HFC.value
            * self.instance.amortisation_plant
            / self.instance.discounted_demand
        )
        CAPEX.append(fuel_cell_contribution)

    # Add electrolyser contributions
    for i in self.instance.electrolysers:
        electrolyser_contribution = (
            (10**3)
            * self.instance.electrolyser_unit_capital_cost[i]
            * self.instance.capacity_electrolysers[i].value
            * self.instance.amortisation_electrolysers[i]
            / self.instance.discounted_demand
        )
        if electrolyser_contribution >= threshold:
            categories.append(f"{i} Electrolysis")
            OPEX.append(
                (10**3)
                * self.instance.electrolyser_unit_operating_cost[i]
                * self.instance.capacity_electrolysers[i].value
                * self.instance.amortisation_plant
                / self.instance.discounted_demand
            )
            CAPEX.append(electrolyser_contribution)

    # Add gaseous hydrogen storage contributions
    gh2_storage_contribution = (
        (10**3)
        * (self.instance.hydrogen_storage_unit_capital_cost / self.instance.hydrogen_LHV)
        * self.instance.capacity_gH2_storage.value
        * self.instance.amortisation_hydrogen_storage
        / self.instance.discounted_demand
    )
    if gh2_storage_contribution >= threshold:
        categories.append("GH2 Storage")
        OPEX.append(
            (10**3)
            * (self.instance.hydrogen_storage_unit_operating_cost / self.instance.hydrogen_LHV)
            * self.instance.capacity_gH2_storage.value
            * self.instance.amortisation_plant
            / self.instance.discounted_demand
        )
        CAPEX.append(gh2_storage_contribution)

    # Add vector production contributions
    for i in self.instance.vectors:
        vector_production_contribution = (
            (10**3)
            * self.instance.vector_production_unit_capital_cost[i]
            * self.instance.capacity_vector_production[i]
            * self.instance.amortisation_vector_production[i]
            / self.instance.discounted_demand
        )
        if vector_production_contribution >= threshold:
            categories.append(f"{i} Production")
            OPEX.append(
                (10**3)
                * self.instance.vector_production_unit_operating_cost[i]
                * self.instance.capacity_vector_production[i]
                * self.instance.amortisation_plant
                / self.instance.discounted_demand
            )
            CAPEX.append(vector_production_contribution)

    # Add vector storage contributions
    for i in self.instance.vectors:
        vector_storage_contribution = (
            (10**3)
            * self.instance.capacity_vector_storage_origin[i].value
            * self.instance.vector_storage_unit_capital_cost[i]
            * self.instance.amortisation_vector_storage[i]
            / self.instance.discounted_demand
        )
        if vector_storage_contribution >= threshold:
            categories.append(f"{i} Storage")
            OPEX.append(
                (10**3)
                * self.instance.capacity_vector_storage_origin[i].value
                * self.instance.vector_storage_unit_operating_cost[i]
                * self.instance.amortisation_plant
                / self.instance.discounted_demand
            )
            CAPEX.append(vector_storage_contribution)

    # Initialize the subplots environment
    fig, ax = subplots()

    # Plot the bar chart
    bar(categories, CAPEX, label="CAPEX", color=self.custom_cmap[0])
    bar(categories, OPEX, bottom=CAPEX, label="OPEX", color=self.custom_cmap[1])

    # Update the axes
    ax.set(ylabel="LCOH [$/kg]")

    # Update plot settings
    xticks(rotation=45, ha="right")
    legend()
    minorticks_on()

    # Update the hyperparameters for the tick markers
    tick_params(
        which="minor",
        length=2,
        width=1,
        direction="out",
        labelsize=0,
    )

    # Produce dictionaries of the CAPEX and OPEX breakdowns for the user
    self.CAPEX = dict(zip(categories, CAPEX))
    self.OPEX = dict(zip(categories, OPEX))

    # Display the plot
    show()
    pass
