"""
Working on the client side
==========================

Generating fake client data
---------------------------
.. automodule:: snap.elements.client.fake
    :members: 

Calculating significance time series from event timestamps
-----------------------------------------------------------
.. autoclass:: snap.elements.client.CountAna
    :members: 
.. autoclass:: snap.elements.client.ShapeAna
    :members: 

Setting client ID
-----------------
.. autoclass:: snap.elements.client.setId
    :members: 


"""
from .setId import setId
from . import fake
from .sigcalc import CountAna, ShapeAna

