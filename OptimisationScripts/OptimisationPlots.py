from matplotlib.pyplot import  subplots, show,legend, gca,bar,xticks, fill_between, minorticks_on,tick_params
from matplotlib.ticker import MaxNLocator
from plotly.graph_objects import Figure, Sankey
from numpy import array,zeros,size, floor,max

def wind_energy(self):
    # Initialising the subplots environment and employing the custom colour scheme. 
    fig, ax = subplots()
    cmap    = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.
    line_counter = 0
    legend_entry = ('Energy From Renewables','Demand Signal at Destination')

    # Addiing the energy produced by the turbine to the plot
    self.cap_factor = {'wind': [],
                      'solar': []}
    for s in self.instance.scenario:
        power_wind = array(len(self.instance.time))
        power_solar = array(len(self.instance.time))
        if self.instance.wind:
            power_wind =  array([self.instance.turbine_power[(st)] for st in self.instance.full_set for _ in range(st[2]) if st[0] == s])*int(self.instance.capacity_number_turbines.value)
            time = array([(st[1],st[2]) for st in self.instance.full_set for _ in range(st[2]) if st[0] == s])
            self.cap_factor['wind'].append(sum(power_wind)/(max(power_wind) * len(power_wind)))
        if self.instance.solar:
            power_solar = array([0.0036*self.instance.solar_power[(st)] for st in self.instance.full_set for _ in range(st[2]) if st[0] == s])*int(self.instance.capacity_solar.value)
            time = array([(st[1],st[2]) for st in self.instance.full_set for _ in range(st[2]) if st[0] == s])                        
            self.cap_factor['solar'].append(sum(power_solar)/(max(power_solar) * len(power_solar)))

        ax.plot(range(time[0][0],time[-1][0]+time[-1][1]),
               power_wind+power_solar,
                color = cmap[line_counter],
                linewidth = self.linewidth
                )

        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0
    
    # Updating the axes
    ax.set(xlabel = 'Time [h]',
           ylabel = 'Energy [GJ/h]',
           title = 'Renewable Energy against Time'
           )
    ax.set_ylim(bottom=0)
    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Updating the hyperaparmeters for the tick markers
    tick_params(which = 'minor',
                length = 2,
                width = 1,
                direction = 'out',
                labelsize = 0
                ) 
    
    # Displaying the plot
    show()
    pass

def grid_energy(self):

    # Initialising the subplots environment and employing the custom colour scheme. 
    fig, ax = subplots()
    cmap    = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.
    line_counter = 0
    # Addiing the energy produced by the turbine to the plot

    for s in self.instance.scenario:
        time = [(st[1],st[2]) for st in self.instance.full_set for _ in range(st[2]) if st[0] == s]
        ax.plot(range(time[0][0],time[-1][0]+time[-1][1]),
                array([self.instance.energy_grid[(s,t)].value for t in time]),
                color = cmap[line_counter],
                linewidth = self.linewidth
                )

        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0
    
    # Updating the axes
    ax.set(xlabel = 'Time [h]',
           ylabel = 'Energy [GJ/h]',
           title = 'Grid Energy against Time'
           )
    ax.set_ylim(bottom=0)
    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Updating the hyperaparmeters for the tick markers
    tick_params(which = 'minor',
                length = 2,
                width = 1,
                direction = 'out',
                labelsize = 0
                ) 
    
    # Displaying the plot
    show()
    pass

def curtailed_energy(self):

    # Initialising the subplots environment and employing the custom colour scheme. 
    fig, ax = subplots()
    cmap    = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.
    line_counter = 0
    # Addiing the energy produced by the turbine to the plot

    for s in self.instance.scenario:
        time = [(st[1],st[2]) for st in self.instance.full_set for _ in range(st[2]) if st[0] == s]
        if self.instance.grid_wheel:
            y = array([self.instance.energy_curtailed[(s,t)].value + self.instance.energy_wheeled[(s,t)].value for t in time])
        else:
            y = array([self.instance.energy_curtailed[(s,t)].value for t in time])
        ax.plot(range(time[0][0],time[-1][0]+time[-1][1]),
                y,
                color = cmap[line_counter],
                linewidth = self.linewidth
                )

        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0
    
    # Updating the axes
    ax.set(xlabel = 'Time [h]',
           ylabel = 'Energy [GJ/h]',
           title = 'Curtailed Energy against Time'
           )
    #ax.set_ylim(bottom=0)
    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Updating the hyperaparmeters for the tick markers
    tick_params(which = 'minor',
                length = 2,
                width = 1,
                direction = 'out',
                labelsize = 0
                ) 
    
    # Displaying the plot
    show()
    pass

def hydrogen_storage_tank_level(self):
    # Initialising the subplots environment and employing the custom colour scheme.
    fig, ax = subplots()
    cmap    = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.
    line_counter = 0
    
    for s in self.instance.scenario:
        time = [(st[1],st[2]) for st in self.instance.full_set for _ in range(st[2]) if st[0] == s]
        ax.plot(range(time[0][0],time[-1][0]+time[-1][1]),
                array([self.instance.gh2_storage[(s,t)].value for t in time]),
                color = cmap[line_counter],
                linewidth = self.linewidth
                )
        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0
        

    # Updating the axes
    ax.set(xlabel='Time [h]',
           ylabel='Hydrogen Storage at Origin [GJ]',
           title='Hydrogen Storage Against time'
           )
    ax.set_ylim(bottom=0)
    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()
    
    # Updating the hyperaparmeters for the tick markers
    tick_params(which='minor',
                length=2,
                width=1,
                direction='out',
                labelsize=0
                ) 
    
    # Displaying the plot
    show()
    pass

def origin_storage_tank_levels(self):
    # Initialising the subplots environment and employing the custom colour scheme.
    fig, ax = subplots()
    cmap    = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.
    line_counter = 0
    
    for s in self.instance.scenario:
        time = [(st[1],st[2]) for st in self.instance.full_set for _ in range(st[2]) if st[0] == s]
        for i in self.instance.vectors:
            ax.plot(range(time[0][0],time[-1][0]+time[-1][1]),
                    array([self.instance.vector_storage_origin[(s,t[0],t[1]),i].value for t in time]),
                    label = i,
                    color = cmap[line_counter],
                    linewidth = self.linewidth
                    )
        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0

    # Updating the axes
    ax.set(xlabel='Time [h]',
           ylabel='Vector Storage at Origin [TJ]',
           title='Origin Vector Storage Against time'
           )
    ax.set_ylim(bottom=0)
    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()
    
    # Updating the hyperaparmeters for the tick markers
    tick_params(which='minor',
                length=2,
                width=1,
                direction='out',
                labelsize=0
                ) 
    
    # Displaying the plot
    show()
    pass


def hydrogen_production(self):
    # Initialising the subplots environment and employing the custom colour scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.    
    line_counter = 0

    # As this will be a stacked plot, y is the array to which each plot is added to.
    for s in self.instance.scenario:
        time = [(st[1],st[2]) for st in self.instance.full_set for _ in range(st[2]) if st[0] == s]
        y = zeros(int(size(time)/2))
        
        for i in self.instance.electrolysers:
            # Plotting an infill for the stacked plot
            # Updating the y array
            y += array([self.instance.energy_electrolysers[(s,t[0],t[1]),i].value for t in time])
            
            # Plottin the line
            ax.plot(range(time[0][0],time[-1][0]+time[-1][1]),
                    y,
                    label = i, 
                    color = cmap[line_counter],
                    linewidth = self.linewidth
                    )
            
        
        line_counter += 1
    
        if line_counter >= len(cmap):
            line_counter = 0

    # Updating the axes
    ax.set(xlabel='Time [h]',
           ylabel='Hydrogen Production [GJ/h]',
        title='Hydrogen Production Against time'
        )
    ax.set_ylim(bottom=0)
    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()

    # Updating the hyperaparmeters for the tick markers
    tick_params(which='minor',
                length=2,
                width=1,
                direction='out',
                labelsize=0
                )
    
    # Displaying the plot
    show()
    pass

def vector_production(self):
    # Initialising the subplots environment and employing the custom colour scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.    
    line_counter = 0

    # As this will be a stacked plot, y is the array to which each plot is added to.
   
    
    for s in self.instance.scenario:
        time = [(st[1],st[4],st[5]) for st in self.instance.vector_set_time for _ in range(st[2]) if st[3] == s]
        y = zeros(int(size(time)/3))
        for i in self.instance.vectors:
            # Plotting an infill for the stacked plot
            # Updating the y array
            y += array([self.instance.energy_vector_production_flux[(s,t[1],t[2]),i].value for t in time])
            # Plottin the line
            ax.plot([t[0] for t in time],
                    y,
                    label = i, 
                    color = cmap[line_counter],
                    linewidth = self.linewidth
                    )
            
        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0
    
    # Updating the axes
    ax.set(xlabel='Time [h]',
           ylabel='Vector Production [GJ/h]',
           title='Vector Production Against time'
           )

    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()
    
    # Updating the hyperaparmeters for the tick markers
    tick_params(which='minor',
                length=2,
                width=1,
                direction='out',
                labelsize=0
                )
    
    # Displaying the plot
    show()
    pass

def active_trains(self):
    # Initialising the subplots environment and employing the custom colour scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.    
    line_counter = 0

    # As this will be a stacked plot, y is the array to which each plot is added to.
   
    
    for s in self.instance.scenario:
        time = [(st[1],st[4],st[5]) for st in self.instance.vector_set_time for _ in range(st[2]) if st[3] == s]
        y = zeros(int(size(time)/3))
        for i in self.instance.vectors:
            # Plotting an infill for the stacked plot
            # Updating the y array
            y += array([self.instance.number_active_trains[(s,t[1],t[2]),i].value for t in time]) 
            # Plottin the line
            ax.plot([t[0] for t in time],
                    y,
                    label = i, 
                    color = cmap[line_counter],
                    linewidth = self.linewidth
                    )
            
        line_counter += 1
        if line_counter >= len(cmap):
            line_counter = 0
    
    # Updating the axes
    ax.set(xlabel='Time [h]',
           ylabel='Number Active Trains',
           title='Number Active Trains Against time'
           )
    ax.set_ylim(bottom=0)

    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()
    
    # Updating the hyperaparmeters for the tick markers
    tick_params(which='minor',
                length=2,
                width=1,
                direction='out',
                labelsize=0
                )
    
    # Displaying the plot
    show()
    pass


def objective_cdf(self):
    # Initialising the subplots environment and employing the custom colour scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap 
    y = []
    
    for s in self.instance.scenario:
        discounted_demand = (8760 / (self.instance.end_time_index) * self.instance.amortisation_plant * sum(
            sum((self.instance.leaf_nodes[s,t,d]) * 
                    self.instance.energy_vector_production_flux[(s_v, t_v,d_v), q].value *d
                    for s,t,d,s_v,t_v,d_v in self.instance.vector_set_time if s_v == s)/ 120
            for q in self.instance.vectors
        ))
        y.append( 1000 * (self.instance.CAPEX.value + self.instance.OPEX[s].value) / discounted_demand)
    
    ax.hist(y, bins=7,alpha=0.7, color=cmap[0], edgecolor='black')
    # Adding a legend to the plot
    ax.legend()
    
    # Updating the axes
    ax.set(xlabel='Average Hydrogen (equivalent) Production [kg/h]',
           ylabel='Probability Density',
           title='Probability Conditioned Objective Values'
           )

    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    minorticks_on()
    
    # Updating the hyperaparmeters for the tick markers
    tick_params(which='minor',
                length=2,
                width=1,
                direction='out',
                labelsize=0
                )
    
    # Displaying the plot
    show()
    pass

def LCOH_contributions(self,threshold):
    self.instance.discounted_demand  = (8760 / (self.instance.end_time_index) * self.instance.amortisation_plant * sum(
            sum((self.instance.leaf_nodes[s,t,d]) * 
                    self.instance.energy_vector_production_flux[(s_v, t_v,d_v), q].value *d
                    for s,t,d,s_v,t_v,d_v in self.instance.vector_set_time)/ 120
            for q in self.instance.vectors
        )) / len(self.instance.scenario.data())

    # Producing lists, containing the different LCOH contributions
    categories  = ['Total LCOH']
    OPEX        = [(10**3)*sum(self.instance.OPEX[s].value/len(self.instance.scenario) for s in self.instance.scenario) / self.instance.discounted_demand]
    CAPEX       = [(10**3)*self.instance.CAPEX.value / self.instance.discounted_demand]
    if self.instance.wind:
        categories.append('Wind Turbines')
        OPEX.append((10**3)*self.instance.turbine_unit_operating_cost * self.instance.capacity_number_turbines.value * self.instance.amortisation_plant / self.instance.discounted_demand)
        CAPEX.append((10**3)*self.instance.turbine_unit_capital_cost * self.instance.capacity_number_turbines.value * self.instance.amortisation_turbine / self.instance.discounted_demand)
    
    if self.instance.solar:
        categories.append('Solar Panels')
        OPEX.append((10**3)*self.instance.solar_unit_operating_cost * self.instance.capacity_solar.value * self.instance.amortisation_plant / self.instance.discounted_demand)
        CAPEX.append((10**3)*self.instance.solar_unit_capital_cost * self.instance.capacity_solar.value * self.instance.amortisation_solar / self.instance.discounted_demand)
    if self.instance.grid_connection.value:
        if (10**3)*sum(self.instance.net_grid[s].value/len(self.instance.scenario) for s in self.instance.scenario) * self.instance.LCAP * self.instance.grid_energy_factor.value * (8760/self.instance.end_time_index) * self.instance.amortisation_plant / self.instance.discounted_demand >= threshold:
            categories.append("Grid Connection")
            OPEX.append((10**3)*sum(self.instance.net_grid[s].value/len(self.instance.scenario) for s in self.instance.scenario)  * self.instance.LCAP * self.instance.grid_energy_factor.value * (8760/self.instance.end_time_index) * self.instance.amortisation_plant / self.instance.discounted_demand)
            CAPEX.append(0)

    if (10**3)*self.instance.fuel_cell_unit_capital_cost * self.instance.capacity_HFC.value * self.instance.amortisation_fuel_cell / self.instance.discounted_demand >= threshold:
        categories.append("Fuel Cell")
        OPEX.append((10**3)*self.instance.fuel_cell_unit_operating_cost * self.instance.capacity_HFC.value * self.instance.amortisation_plant / self.instance.discounted_demand)
        CAPEX.append((10**3)*self.instance.fuel_cell_unit_capital_cost * self.instance.capacity_HFC.value * self.instance.amortisation_fuel_cell / self.instance.discounted_demand)

    for i in self.instance.electrolysers:
        if (10**3)*self.instance.electrolyser_unit_capital_cost[i] * self.instance.capacity_electrolysers[i].value * self.instance.amortisation_electrolysers[i]/ self.instance.discounted_demand >= threshold:
            categories.append(i+' Electrolysis')
            OPEX.append((10**3)*self.instance.electrolyser_unit_operating_cost[i] * self.instance.capacity_electrolysers[i].value * self.instance.amortisation_plant / self.instance.discounted_demand)
            CAPEX.append((10**3)*self.instance.electrolyser_unit_capital_cost[i] * self.instance.capacity_electrolysers[i].value * self.instance.amortisation_electrolysers[i]/ self.instance.discounted_demand)

    if (10**3)*(self.instance.hydrogen_storage_unit_capital_cost / self.instance.hydrogen_LHV) * self.instance.capacity_gH2_storage.value * self.instance.amortisation_hydrogen_storage / self.instance.discounted_demand >= threshold:
        categories.append('GH2 Storage')
        OPEX.append((10**3)*(self.instance.hydrogen_storage_unit_operating_cost / self.instance.hydrogen_LHV) * self.instance.capacity_gH2_storage.value * self.instance.amortisation_plant / self.instance.discounted_demand)
        CAPEX.append((10**3)*(self.instance.hydrogen_storage_unit_capital_cost / self.instance.hydrogen_LHV) * self.instance.capacity_gH2_storage.value * self.instance.amortisation_hydrogen_storage / self.instance.discounted_demand)
    
    for i in self.instance.vectors:
        if (10**3)*self.instance.vector_production_unit_capital_cost[i] * self.instance.capacity_vector_production[i] * self.instance.amortisation_vector_production[i] / self.instance.discounted_demand >= threshold:
            categories.append(i+' Production')
            OPEX.append((10**3)*self.instance.vector_production_unit_operating_cost[i] * self.instance.capacity_vector_production[i] * self.instance.amortisation_plant / self.instance.discounted_demand)
            CAPEX.append((10**3)*self.instance.vector_production_unit_capital_cost[i] * self.instance.capacity_vector_production[i] * self.instance.amortisation_vector_production[i] / self.instance.discounted_demand)

    for i in self.instance.vectors:
        if (10**3)*(self.instance.capacity_vector_storage_origin[i].value) * (self.instance.vector_storage_unit_capital_cost[i]* self.instance.amortisation_vector_storage[i]) / self.instance.discounted_demand >= threshold:
            categories.append(i+' Storage')
            OPEX.append((10**3)*(self.instance.capacity_vector_storage_origin[i].value ) * (self.instance.vector_storage_unit_operating_cost[i] * self.instance.amortisation_plant) / self.instance.discounted_demand)
            CAPEX.append((10**3)*(self.instance.capacity_vector_storage_origin[i].value) * (self.instance.vector_storage_unit_capital_cost[i] * self.instance.amortisation_vector_storage[i]) / self.instance.discounted_demand )
    
    # Initialising the subplots environment.
    fig, ax = subplots()
    
    # Plotting the bar chart    
    bar(categories, CAPEX, label='CAPEX',color=self.custom_cmap[0])
    bar(categories, OPEX, bottom=CAPEX, label='OPEX',color=self.custom_cmap[1])

    # Updating the axes    
    ax.set(ylabel='LCOH [$/kg]')

    # Updating plot settings    
    xticks(rotation = 45,ha='right')
    legend()
    minorticks_on()

    # Updating the hyperaparmeters for the tick markers
    tick_params(which = 'minor',
                length = 2,
                width = 1,
                direction = 'out',
                labelsize = 0
                ) 
    
    # Producing dictionaries of the CAPEX and OPEX breakdowns for the user
    self.CAPEX = dict(zip(categories, CAPEX))
    self.OPEX = dict(zip(categories, OPEX))
    
    # Displaying the plot
    show()
    pass

def sankey_diagram(self,threshold,height):

    normaliser  = sum(self.instance.demand_signal[t]*self.instance.time_duration[t] for t in self.instance.time)
    grid        = 0
    battery     = 0
    fuel_cell   = 0
    conversion  = 0

    labels = ["Blank",
              "Renewable Energy",
              "Low Wind Loss",
              "Electrical Energy"]
    connections = [(1,2,sum(self.instance.capacity_number_turbines.value * self.instance.time_duration[t]*(max(self.instance.turbine_power[t] for t in self.instance.time) - self.instance.turbine_power[t]) for t in self.instance.time) / normaliser),
                   (1,3,sum(self.instance.time_duration[t]*self.instance.capacity_number_turbines.value * self.instance.turbine_power[t]*self.instance.turbine_efficiency for t in self.instance.time) / normaliser)
                   ]
    
    if self.instance.grid_connection.value:
        grid += 1
        labels.append("Grid Energy")
        connections.append((3+grid,3, sum(self.instance.time_duration[t]*self.instance.energy_grid[t].value for t in self.instance.time)/ normaliser))
    
    if self.instance.battery.value:
        battery += 2
        labels.append("Battery Storage")
        connections.append((3+grid+battery-1, 3, sum(self.instance.time_duration[t]*self.instance.energy_battery_out[t].value for t in self.instance.time) / normaliser))
        connections.append((3,3+grid+battery-1,sum(self.instance.time_duration[t]*self.instance.energy_battery_in[t].value for t in self.instance.time) / normaliser))
        labels.append("Battery Inefficiency")
        connections.append((3+grid+battery-1,3+grid+battery,abs(sum(self.instance.time_duration[t]*(self.instance.energy_battery_in[t].value - self.instance.energy_battery_out[t].value)for t in self.instance.time)) / normaliser))

    if self.instance.fuel_cell.value:
        fuel_cell += 2
        labels.append("Fuel Cell")
        connections.append((2+grid+battery+fuel_cell,3,sum(self.instance.time_duration[t]*self.instance.energy_HFC[t].value for t in self.instance.time) / normaliser))
        connections.append((7+grid+battery+fuel_cell-1,3+grid+battery+fuel_cell-1,sum(self.instance.time_duration[t]*self.instance.energy_HFC_flux[t].value for t in self.instance.time)/normaliser))
        labels.append("Fuel Cell Inefficiency")
        connections.append((3+grid+battery+fuel_cell-1,3+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*(self.instance.energy_HFC_flux[t].value - self.instance.energy_HFC[t].value) for t in self.instance.time)/normaliser))
        
    labels.append("Curtailed Energy")
    connections.append((3, 4+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*self.instance.energy_curtailed[t].value for t in self.instance.time)/normaliser))

    labels.append("Electrolysis")
    connections.append((3,5+grid+battery+fuel_cell,sum(sum(self.instance.time_duration[t]*self.instance.energy_electrolysers[k,t].value for k in self.instance.electrolysers) for t in self.instance.time)/normaliser))

    labels.append("Gaseous Hydrogen Storage")
    connections.append((5+grid+battery+fuel_cell,6+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*self.instance.energy_gh2_in_store[t].value for t in self.instance.time)/normaliser))
    connections.append((5+grid+battery+fuel_cell,8+grid+battery+fuel_cell,sum(sum(self.instance.time_duration[t]*self.instance.energy_gh2_use[q,t].value for q in self.instance.vectors) for t in self.instance.time)/normaliser))

    labels.append("Electrolysis Losses")
    connections.append((5+grid+battery+fuel_cell,7+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*(sum(self.instance.energy_electrolysers[k,t].value for k in self.instance.electrolysers) - self.instance.energy_gH2_flux[t].value) for t in self.instance.time)/normaliser))

    labels.append("Vector Production")
    connections.append((3, 8+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*sum(self.instance.energy_penalty_vector_production[q,t].value for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    connections.append((6+grid+battery+fuel_cell,8+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.energy_gh2_rem[q,t].value for q in self.instance.vectors) for t in self.instance.time)/normaliser+sum(self.instance.time_duration[t]*sum(self.instance.vector_storage_origin[q,t].value*self.instance.bol_rate[q]*self.instance.bol_energy_penalty[q]*1000 for q in self.instance.vectors) for t in self.instance.time)/normaliser))

    labels.append("Origin Vector Storage")
    connections.append((8+grid+battery+fuel_cell,9+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser))
    
    labels.append("Fugitive Loss")
    connections.append((8+grid+battery+fuel_cell,10+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*(1-self.instance.vector_fugitive_efficiency[q]) for q in self.instance.vectors) for t in self.instance.time)/ normaliser))

    labels.append("Vector Production Efficiency Loss")
    connections.append((8+grid+battery+fuel_cell, 11+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*sum(self.instance.energy_penalty_vector_production[q,t].value for q in self.instance.vectors) for t in self.instance.time)/normaliser))

    labels.append("Shipping")
    connections.append((9+grid+battery+fuel_cell,12+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser))
    
    labels.append("Shipping Fuel")
    connections.append((12+grid+battery+fuel_cell,13+grid+battery+fuel_cell,(self.instance.journey_time  * 2 * sum(sum(sum(self.instance.time_duration[t]*self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time) * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser ))

    labels.append("Destination Vector Storage")
    connections.append((12+grid+battery+fuel_cell,14+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser - (sum(sum(sum(self.instance.time_duration[t]*self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time)* self.instance.journey_time  * 2 * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser - sum(self.instance.time_duration[t]*sum(self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q] for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    
    if self.instance.reconversion:
        labels.append("Reconversion")
    else:
        labels.append("Demand")
    connections.append((14+grid+battery+fuel_cell,15+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser - (sum(sum(sum(self.instance.time_duration[t]*self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time) * self.instance.journey_time  * 2 * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser - sum(self.instance.time_duration[t]*sum(self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q] for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    
    labels.append("Compression")
    connections.append((3,16+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*self.instance.energy_compression[t].value for t in self.instance.time) / normaliser))

    labels.append("Transmission Loss")
    connections.append((1,17+grid+battery+fuel_cell,(1-self.instance.turbine_efficiency)*sum(self.instance.time_duration[t]*self.instance.capacity_number_turbines.value * self.instance.turbine_power[t] for t in self.instance.time) / normaliser))

    labels.append("Compression Parasitic Loss")
    connections.append((5+grid+battery+fuel_cell,18+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*self.instance.energy_gH2_flux[t].value * (1-self.instance.compressor_effiency) for t in self.instance.time)/normaliser))

    if self.instance.reconversion:
        conversion += 1
        labels.append("Delivered H2")
        conversion += 1
        labels.append("Reconversion Loss")
        #connections.append((15+grid+battery+fuel_cell,18+conversion+grid+battery+fuel_cell, (sum(self.instance.time_duration[t]*sum((1-self.instance.reconversion_efficiency[q]) * self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser - (sum(sum(sum(self.instance.time_duration[t]*(1-self.instance.reconversion_efficiency[q]) *self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time)* self.instance.journey_time  * 2 * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser) - sum(self.instance.time_duration[t]*sum((1-self.instance.reconversion_efficiency[q])*self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q] for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser))
        #connections.append((15+grid+battery+fuel_cell,17+conversion+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser - (sum(sum(sum(self.instance.time_duration[t]*self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time) * self.instance.journey_time  * 2 * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser - sum(self.instance.time_duration[t]*sum(self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q] for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser - (sum(self.instance.time_duration[t]*sum((1-self.instance.reconversion_efficiency[q]) * self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser - (sum(sum(sum(self.instance.time_duration[t]*(1-self.instance.reconversion_efficiency[q]) *self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time)* self.instance.journey_time  * 2 * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser) - sum(self.instance.time_duration[t]*sum((1-self.instance.reconversion_efficiency[q])*self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q] for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser))
        connections.append((15+grid+battery+fuel_cell,17+conversion+grid+battery+fuel_cell,sum(self.instance.demand_signal[t]*self.instance.time_duration[t] for t in self.instance.time)/normaliser))
        connections.append((15+grid+battery+fuel_cell,18+conversion+grid+battery+fuel_cell,sum(sum(self.instance.energy_vector_consumption_flux[q,t].value*self.instance.time_duration[t]*((1-self.instance.reconversion_efficiency[q])/self.instance.reconversion_efficiency[q]) for t in self.instance.time) for q in self.instance.vectors)/normaliser))

    labels.append("Vector Production Synthetic Loss")
    connections.append((8+grid+battery+fuel_cell,19+conversion+grid+battery+fuel_cell,(sum(self.instance.time_duration[t]*sum((1-self.instance.vector_synthetic_efficiency[q])*(self.instance.energy_vector_production_flux[q,t].value / self.instance.vector_synthetic_efficiency[q])for q in self.instance.vectors) for t in self.instance.time)/normaliser)))
    
    labels.append("Waiting Ship BOL")
    connections.append((14+grid+battery+fuel_cell,20+conversion+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q]for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser))

    labels.append("BOL Management")
    labels.append("BOL Management Penalty")
    connections.append((21+conversion+grid+battery+fuel_cell,22+conversion+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.vector_storage_origin[q,t].value*self.instance.bol_rate[q]*self.instance.bol_energy_penalty[q]*1000 for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    connections.append((21+conversion+grid+battery+fuel_cell,8+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.vector_storage_origin[q,t].value*self.instance.bol_rate[q]*self.instance.vector_calorific_value[q]*1000 for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    connections.append((8+grid+battery+fuel_cell,21+conversion+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.vector_storage_origin[q,t].value*self.instance.bol_rate[q]*self.instance.vector_calorific_value[q]*1000 for q in self.instance.vectors) for t in self.instance.time)/normaliser+sum(self.instance.time_duration[t]*sum(self.instance.vector_storage_origin[q,t].value*self.instance.bol_rate[q]*self.instance.bol_energy_penalty[q]*1000 for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    
    fig = Figure(data=[Sankey(
            arrangement='freeform',
            node = dict(
            pad = 30,
            thickness =15,
            line = dict(color = "black", width = 0.2),
            label = labels,           #22
            color=self.custom_cmap),
            link = dict(
            source = list(map(lambda x: x[0], connections)), # indices correspond to labels, eg A1, A2, A1, B1, ...
            target = list(map(lambda x: x[1], connections)),
            value = list(map(lambda x: 0 if x[2] <= threshold else x[2], connections)),
            color=['#708090']*50
        ))])

    fig.update_layout(title_text="Supply Chain Sankey Diagram",
                      font_family="Times New Roman",
                      font_color="black",
                      font_size=16,
                      title_font_family="Times New Roman",
                      title_font_color="black",
                      )
    
    fig.update_layout( autosize=False, width=1350, height=height)
    fig.show(scale=6)
    pass