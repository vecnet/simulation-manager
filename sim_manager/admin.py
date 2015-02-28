from django.contrib import admin

from sim_manager.models import Simulation, SimulationGroup

admin.site.register(Simulation)
admin.site.register(SimulationGroup)