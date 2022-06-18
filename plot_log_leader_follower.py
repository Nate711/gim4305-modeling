import log_utils
import argparse
import pandas as pd
import three_dof_utils
import pdb


parser = argparse.ArgumentParser(description='Plot 3dof jump dadta')
parser.add_argument('--filename', required=False, type=str)
args = parser.parse_args()

if __name__ == "__main__":
    df = log_utils.load_log_df(args.filename)
    # pdb.set_trace()
    pd.options.plotting.backend = "plotly"

    fig = df.plot.line(x='ts', y=df.columns)
    fig.show()
