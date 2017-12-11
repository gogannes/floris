"""
Copyright 2017 NREL

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

from BaseObject import BaseObject
import numpy as np
from VisualizationManager import VisualizationManager


class FlowField(BaseObject):
    """
        Describe FF here
    """

    def __init__(self,
                 wake_combination=None,
                 wind_speed=None,
                 shear=None,
                 veer=None,
                 turbulence_intensity=None,
                 turbine_map=None,
                 characteristic_height=None,
                 wake=None):
        super().__init__()
        self.viz_manager = VisualizationManager()
        self.wake_combination = wake_combination
        self.wind_speed = wind_speed
        self.shear = shear
        self.veer = veer
        self.turbulence_intensity = turbulence_intensity
        self.turbine_map = turbine_map

        self.characteristicHeight = characteristic_height
        self.wake = wake

        self.grid_x_resolution = 200
        self.grid_y_resolution = 200
        self.grid_z_resolution = 50

        if self._valid():
            self.x, self.y, self.z = self._discretize_domain()
            self.u_field = self._constant_flowfield(self.wind_speed)

    def _valid(self):
        """
            Do validity check
        """
        valid = True
        if not super().valid():
            return False
        if self.characteristicHeight <= 0:
            valid = False
        return valid

    def _discretize_domain(self):
        coords = [coord for coord, _ in self.turbine_map.items()]
        x = [coord.x for coord in coords]
        y = [coord.y for coord in coords]
        xmin, xmax = min(x), max(x)
        ymin, ymax = min(y), max(y)

        turbines = [turbine for _, turbine in self.turbine_map.items()]
        maxDiameter = max([turbine.rotorDiameter for turbine in turbines])
        hubHeight = turbines[0].hubHeight

        x = np.linspace(xmin - 2 * maxDiameter, xmax + 10 * maxDiameter, self.grid_x_resolution)
        y = np.linspace(ymin - 2 * maxDiameter, ymax + 2 * maxDiameter, self.grid_y_resolution)
        z = np.linspace(0, 2 * hubHeight, self.grid_z_resolution)
        return np.meshgrid(x, y, z, indexing="xy")

    def _field_velocity_at_coord(self, target_coord, field):
        coords = [coord for coord, _ in self.turbine_map.items()]
        x = [coord.x for coord in coords]
        y = [coord.y for coord in coords]
        xmin, xmax = min(x), max(x)
        ymin, ymax = min(y), max(y)

        turbines = [turbine for _, turbine in self.turbine_map.items()]
        maxDiameter = max([turbine.rotorDiameter for turbine in turbines])

        x_range = (xmin - 2 * maxDiameter, xmax + 10 * maxDiameter, self.grid_x_resolution)
        y_range = (ymin - 2 * maxDiameter, ymax + 2 * maxDiameter, self.grid_y_resolution)

        dx = (x_range[1] - x_range[0]) / self.grid_x_resolution
        dy = (y_range[1] - y_range[0]) / self.grid_y_resolution

        xindex = int((target_coord.x + 2 * maxDiameter) / dx) + 1
        yindex = int((target_coord.y + 2 * maxDiameter) / dy)

        return field[yindex, xindex, 25]

    def _constant_flowfield(self, constant_value):
        xmax, ymax, zmax = self.x.shape[0], self.y.shape[1], self.z.shape[2]
        return np.full((xmax, ymax, zmax), constant_value)

    def _compute_turbine_velocity_deficit(self, x, y, z, turbine, coord, deflection, wake, flowfield):
        velocity_function = self.wake.get_velocity_function()
        return velocity_function(x, y, z, turbine, coord, deflection, wake, flowfield)

    def _compute_turbine_wake_deflection(self, x, turbine, coord):
        deflection_function = self.wake.get_deflection_function()
        return deflection_function(x, turbine, coord)

    # Public methods

    def calculate_wake(self):
        # TODO: rotate layout here
        # TODO: sort in ascending order of x coord

        # calculate the velocity deficit and wake deflection on the mesh
        u_wake = np.zeros(self.u_field.shape)
        for coord, turbine in self.turbine_map.items():
            # update the turbine based on the velocity at its hub
            local_deficit = self._field_velocity_at_coord(coord, u_wake)
            turbine.update_quantities(
                self.wind_speed - local_deficit, self.shear)
            
            # get the wake deflecton field
            deflection = self._compute_turbine_wake_deflection(
                self.x, turbine, coord)

            # get the velocity deficit accounting for the deflection
            turb_wake = self.wind_speed * self._compute_turbine_velocity_deficit(
                self.x, self.y, self.z, turbine, coord, deflection, self.wake, self)

            # combine this turbine's wake into the full wake field
            u_wake = self.wake_combination.combine(u_wake, turb_wake)

        # apply the velocity deficit field to the freestream
        self.u_field = self.wind_speed - u_wake

    # Visualization

    def plot_flow_field_plane(self, percent_height=0.5, show=True):
        zplane = int(self.x.shape[2] * percent_height)
        self.viz_manager.plot_constant_z(
            self.x[:, :, zplane], self.y[:, :, zplane], self.u_field[:, :, zplane])
        for coord, turbine in self.turbine_map.items():
            self.viz_manager.add_turbine_marker(turbine, coord)
        if show:
            self.viz_manager.show()

    def plot_flow_field_planes(self, heights):
        for height in heights:
            self.plot_flow_field_plane(height, False)
        self.viz_manager.show()

    # FUTURE
    # TODO def get_properties_at_turbine(tuple_of_coords):
    #     #probe the FlowField
    #     FlowfieldPropertiesAtTurbine[tuple_of_coords].wake_function()

    # TODO def update_flowfield():
