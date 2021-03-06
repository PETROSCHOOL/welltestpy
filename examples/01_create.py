# -*- coding: utf-8 -*-
import numpy as np
import welltestpy as wtp
import anaflow as ana

### create the field-site and the campaign
field = wtp.data.FieldSite(name="UFZ", coordinates=[51.353839, 12.431385])
campaign = wtp.data.Campaign(name="UFZ-campaign", fieldsite=field)

### add 4 wells to the campaign
campaign.add_well(name="well_0", radius=0.1, coordinates=(0., 0.))
campaign.add_well(name="well_1", radius=0.1, coordinates=(1., -1.))
campaign.add_well(name="well_2", radius=0.1, coordinates=(2., 2.))
campaign.add_well(name="well_3", radius=0.1, coordinates=(-2., -1.))

### generate artificial drawdown data with the Theis solution
prate = -1e-4
time = np.geomspace(10, 7200, 10)
transmissivity = 1e-4
storage = 1e-4
rad = [
   campaign.wells["well_0"].radius,                     # well radius of well_0
   campaign.wells["well_0"] - campaign.wells["well_1"], # distance between 0-1
   campaign.wells["well_0"] - campaign.wells["well_2"], # distance between 0-2
   campaign.wells["well_0"] - campaign.wells["well_3"], # distance between 0-3
]
drawdown = ana.theis(
    rad=rad,
    time=time,
    T=transmissivity,
    S=storage,
    Qw=prate,
)

### create a pumping test at well_0
pumptest = wtp.data.PumpingTest(
    name="well_0",
    pumpingwell="well_0",
    pumpingrate=prate,
    description="Artificial pump test with Theis",
)

### add the drawdown observation at the 4 wells
pumptest.add_transient_obs("well_0", time, drawdown[:, 0])
pumptest.add_transient_obs("well_1", time, drawdown[:, 1])
pumptest.add_transient_obs("well_2", time, drawdown[:, 2])
pumptest.add_transient_obs("well_3", time, drawdown[:, 3])

### add the pumping test to the campaign
campaign.addtests(pumptest)

### plot the well constellation and a test overview
campaign.plot_wells()
campaign.plot()

### save the whole campaign
campaign.save()
