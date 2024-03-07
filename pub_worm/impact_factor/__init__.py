import importlib.util
import os
import pandas as pd

module_name = __name__
module_spec = importlib.util.find_spec(module_name)
package_path = os.path.dirname(module_spec.origin)
file_path = os.path.join(package_path, 'data', '2022_JCR_IF.csv')
print("Full path to the file:", file_path)

impact_factor_df = pd.read_csv(file_path)
