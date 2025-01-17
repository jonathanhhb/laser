<p align="center" width="100%">
<img src="https://user-images.githubusercontent.com/10873335/283954768-97685a6d-7b86-4bba-a3e6-07ac22d5a2b3.png" alt="LASER logo" width="600px"/>
</p>

## Schedule

### First 30 Days (EOY 2023)

- firm up team/stakeholders/advisory committee
- enumerate necessary features for reproducing/supporting previous and in-progress modeling efforts
  - measles (kmccarthy)
  - malaria (cbever/pselvaraj)
  - end-game/end-stage polio (¿kfrey?)
- enumerate necessary features for outstanding questions and issues

### First 60 Days (January 31, 2024)

- "paper search" / investigate potential existing solutions
- capture development requirements
  - tools for preparing data (demographics, networks, etc.)
  - file formats
  - select initial features
    - spatial connectivity
      - individual agent migration (genetics - vector _and_ parasite)
      - NxN matrix connectivity, contagion transport
      - multi-level (meso-scale?) connectivity (communities of communities)
    - community transmission dynamics
      - agents
      - cohorts
      - \*Sim
      - stochastic compartmental
      - ODEs
      - emulator
    - demographics
      - urban/rural
      - class/caste
    - multiple independent populations/community (people + mosquitoes, people + dogs, etc.)
    - ¿co-transmission? TB _and_ HIV
    - non-disease vital dynamics
  - visualization choices

### First 120 Days (February 29, 2024)

- technical considerations
  - single laptop
  - single laptop w/Nvidia GPU
  - multicore
    - single machine
    - large machine (cloud)
    - beyond?
  - Numpy
  - NumPy + Numba
  - NumPy + Numba + CUDA

## Problem Space

The problem is inherently an issue of heterogeneity. Spatial decomposition is the easiest consideration, but not sufficient - a model of N "independent" but identical communities is generally not useful.

Spatial connectivity and the associated latencies in transmission address one dimension of heterogeneity: how "close" is a given community to a potential source of imported contagion (exogenous to the model "world", locally endogenous, e.g., an adjacent community, endogenous but at a remove - rare transmission or multi-stop chain of transmission).

Community size in a spatial model is also a consideration - what is the configuration and connectivity of sub-CCS nodes to nodes at or above CCS for the given disease?

We need configurable characteristics of the individual communities which can vary, along with their interconnectedness, to capture additional heterogeneity.

What _is_ the modeling of the individual communities? "Light-Agent" seems to limit us to an ABM, but we should consider cohorts of epidemiologically similar populations (polio >5, HIV <15, TB latents, etc.) as well as stochastic compartmental models.

Are the individual communities well-mixed or should we also provide for explicit networks at the local level?

## Technology

- Python
- high performance computing:
  - [NumPy](https://numpy.org/)
  - [NUMBA](https://numba.pydata.org/)
  - [CuPy](https://cupy.dev/)
  - [PyCUDA](https://documen.tician.de/pycuda/)
  - [mlx](https://github.com/ml-explore/mlx)
- native code
  - C++ (somewhat awkward interop with Python, but potentially accessible from other technologies, e.g., R)
  - Rust ([PyO3](https://github.com/PyO3/pyo3) is quite nice, but requires getting up to speed on Rust 😳)
- compute requirements:
  - laptop 2010+? (might inform SIMD capabilities)
  - GPU (CUDA) enabled machine laptop/desktop/cloud
  - single core/multi-core
  - largest scenarios?
- visualization
  - cross-platform
  - real-time
- existing file formats for input data
- existing file formats for output data (GeoTIFF? - works with ArcGIS?)

## Other

- community builder tool for given total population and community size distribution
- network builder given a set of communities (gravity, radiation, other algorithms in existing libraries/packages)
- independent populations w/in a community, e.g., mosquitoes or dogs along with humans
- independent or co-transmission, i.e. multiple "diseases"
- models need to be connected with real-world scenarios, not [just] hypothetical explorations

## Notes

- "light" : How light is "light"?
- "agent" : Cohorts? Stochastic compartmental?
- "spatial" : How good are the individual community models? Good enough for non-spatial questions?
- dynamic properties (e.g. GPU flu simulation)
- ¿Ace/clorton-based state machines?
