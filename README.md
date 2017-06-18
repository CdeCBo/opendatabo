# opendatabo

[![Build Status](https://travis-ci.org/CdeCBo/opendatabo.svg?branch=master)](https://travis-ci.org/CdeCBo/opendatabo)

## Setup

1. Install [Conda](https://conda.io/miniconda.html).

2. Create the Conda environment:

```bash
conda env update -f environment.yml
```

3. Activate the Conda environment:

(Linux / OS X)
```bash
source activate opendatabo
```

(Windows)
```batch
activate opendatabo
```

4. Run the tests!

(Linux / OS X)
```bash
PYTHONPATH=. pytest
```

(Windows)
```batch
set PYTHONPATH=.
pytest
```

Built with ❤️ by CdeC Bolivia.
