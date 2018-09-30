# pyredfish
This is a work-in-progress, a previous version was used for an internal config tool a while back, but it's not in active use anymore.
I decided to open-source it as an alternative to the DTMF library which I find to be a little cumbersome (which is normal for a reference implementation).
I've got a few ideas as to future improvements, so expect more housekeeping soon.


## Current status:
Should work with V1.0, but hasn't been tested since housekeeping.

## Goal:
A class that: 
    - Is automatically constructed from simple input (such as a spec dictionary)
    - Builds query urls from class hierarchy
    - Automatic relogin if session expired
    - Automatic logout on garbage collection
    - Provides a simple pythonic adaption of the Redfish API

## TODO:
    - More housekeeping
    - Packaging
    - Documentation
