## Racial Bais and Police caused in the USA

#### Disclaimer:
The data used in for this analysis was sourced from the
washington post. The data is third party data and even though
there is little or no evidence to doubt its accuracy it should be noted.

**Installation Requirements**
- numpy >= 1.20.0
- Python >= 3.9
- bs4(BeautifulSoup) >= 0.0.1
- pandas >= 1.3.1

*For visualization only*
- dash >= 1.21.0
- plotly >= 5.1.0

## Getting Started
Make sure all libraries are correctly imported and 
installed
```python
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

#Dash import
import dash
import dash_html_components as html
import dash_core_components as dcc


```
Access the script from the command and run
```commandline
python main.py
```
Make sure you can access python from the command line. if you can't
you may get this error 
```commandline
python is not recognized as an internal or external command
```
you can learn how to add python to path here:
[Add python to path]("https://www.pythoncentral.io/add-python-to-path-python-is-not-recognized-as-an-internal-or-external-command/")

Once you run the application you should see 
```commandline
Dash is running on http://127.0.0.1:8050/
 * Serving Flask app "main" 
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on

```

That's it you can now view the report including charts
and summaries and the conclusion I reached based on the analysis.
