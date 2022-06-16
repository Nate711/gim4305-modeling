import log_utils
import argparse
import pandas as pd
import three_dof_utils


parser = argparse.ArgumentParser(description='Plot 3dof jump dadta')
parser.add_argument('--filename', required=False, type=str)
args = parser.parse_args()

if __name__ == "__main__":
    df = log_utils.load_log_df(args.filename)

    df["ts"] = df["ts"] - 0.2

    df["qB deg"] = three_dof_utils.actuator_1_qB_deg(df["position-1"])
    df["qB' rad/sec"] = three_dof_utils.actuator_1_qB_dot_rad_sec(df["velocity-1"])
    df["qC deg"] = three_dof_utils.actuator_3_qC_deg(df["position-3"])
    df["qC' rad/sec"] = three_dof_utils.actuator_3_qC_dot_rad_sec(df["velocity-3"])

    df["TB N*m"] = df["torque-1"] * 10.0
    df["TC N*m"] = df["torque-3"] * 10.0

    pd.options.plotting.backend = "plotly"

    fig = df.plot.line(x='ts', y=df.columns)
    fig.show()
