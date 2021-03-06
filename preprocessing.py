import sys
import os
import pandas as pd
import argparse

ALLOWED_MODES = ['clean', 'create_pickle', 'normalize_pickle']
CREATE_PICKLE_MANDATORY_FILES = ['ENV_QH.csv', 'AllNO2_QH.csv', 'AllPM_QH.csv']

NORMALIZED_COLUMN_NAMES = {
    '# date': 'date',
    'Temp': 'temp',
    'RH': 'rh',
    'Tgrad': 't_grad',
    'Patm': 'pressure',
    'Pluvio': 'pluvio',
    '#ref': 'ref',
    '#61FD': 'NO2_61FD',
    '#61F0': 'NO2_61F0',
    '#61EF': 'NO2_61EF',
    '#6182': 'PM_6182',
    '#6179': 'PM_6179',
    '#617B': 'PM_617B',
    'pm2.5#6182': 'PM25_6182',
    'pm2.5#6179': 'PM25_6179',
    'PM25_6170': 'PM25_6179',
    'pm2.5#617B': 'PM25_617B',
}

NO2_FILENAME = "AllNO2_QH.csv"
PM_FILENAME ='AllPM_QH.csv'
ENV_FILENAME = "Env_QH.csv"

def clean(filename, output=None):
    """ Process a csv file taking into account the COLUMN_NAMES dictionnary
    :param filename:
    :return:
    """
    if os.path.isdir(filename):
        list_csv = [os.path.join(filename, name) for name in os.listdir(filename) if name.split('.')[-1] == "csv"]
    else:
        list_csv = [filename]
    for csv_file in list_csv:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8', delimiter=';')
        except UnicodeEncodeError:
            df = pd.read_csv(csv_file, encoding='ISO-8859-1', delimiter=';')

        df = df.rename(columns=NORMALIZED_COLUMN_NAMES)
        if output:
            if os.path.isdir(output):
                out_file = os.path.join(output, csv_file.split('/')[-1])
            else:
                out_file = output
        else:
            out_file = csv_file
        df.to_csv(out_file, sep=';', encoding="utf-8", index=False)
        print("{} cleaned with success !".format(csv_file))


def create_no2_pkl(folder, out_pickle):
    """
    :param folder: path of the folder containing the NO2 and ENV csv inputs file
    :param out_pickle: path of the output pickle file
    :return:
    """
    if not os.path.isdir(folder):
        raise NotADirectoryError
    no2_filename = os.path.join(folder, NO2_FILENAME)
    env_filename = os.path.join(folder, ENV_FILENAME)

    df_no2 = pd.read_csv(no2_filename, encoding='utf-8', delimiter=';')
    df_env = pd.read_csv(env_filename, encoding='utf-8', delimiter=';')

    df_env = df_env.set_index('date').T

    out_df = pd.DataFrame(columns=['date', 'ref', 'NO2_61FD', 'NO2_61F0', 'NO2_61EF', 'rh', 't_grad', 'pressure',
                                   'temp', 'pluvio'])

    for i in range(len(df_no2)):
        row = df_no2.iloc[i]
        date = row.date
        env = df_env[date]
        rh = env.rh if 'rh' in env else 'NA'
        t_grad = env.t_grad if 't_grad' in env else 'NA'
        pressure = env.pressure if 'pressure' in env else 'NA'
        pluvio = env.pluvio if 'pluvio' in env else 'NA'
        temp = env.temp if 'temp' in env else 'NA'

        out_df.loc[i] = [date, row.ref, row.NO2_61FD, row.NO2_61F0, row.NO2_61EF, rh, t_grad, pressure,
                         temp, pluvio]

    out_df.to_pickle(out_pickle)


def create_pm_pkl(folder, out_pickle):
    """
    :param folder: path of the folder containing the NO2 and ENV csv inputs file
    :param out_pickle: path of the output pickle file
    :return:
    """
    if not os.path.isdir(folder):
        raise NotADirectoryError
    pm_filename = os.path.join(folder, PM_FILENAME)
    env_filename = os.path.join(folder, ENV_FILENAME)

    df_pm = pd.read_csv(pm_filename, encoding='utf-8', delimiter=';')
    df_env = pd.read_csv(env_filename, encoding='utf-8', delimiter=';')

    df_env = df_env.set_index('date').T
    out_df = pd.DataFrame(columns=['date', 'ref', 'PM_6182', 'PM_6179', 'PM_617B', 'PM25_6182', 'PM25_6179', 'PM25_617B', 'rh', 't_grad', 'pressure',
                                   'temp', 'pluvio'])

    for i in range(len(df_pm)):
        row = df_pm.iloc[i]
        date = row.date
        env = df_env[date]
        rh = env.rh if 'rh' in env else 'NA'
        t_grad = env.t_grad if 't_grad' in env else 'NA'
        pressure = env.pressure if 'pressure' in env else 'NA'
        pluvio = env.pluvio if 'pluvio' in env else 'NA'
        temp = env.temp if 'temp' in env else 'NA'
        out_df.loc[i] = [date, row.ref, row.PM_6182, row.PM_6179, row.PM_617B, row.PM25_6182, row.PM25_6179, row.PM25_617B, rh, t_grad, pressure,
                         temp, pluvio]

    out_df.to_pickle(out_pickle)


def normalize_pickle(input_pickle, data_type, output_pickle = None):
    if data_type == "NO2":
        normalize_no2_pickle(input_pickle, output_pickle)
    elif data_type == "PM":
        normalize_pm_pickle(input_pickle, output_pickle)
    else:
        print("Invalid type: must be PM or NO2")
        sys.exit()

def normalize_pm_pickle(input_pickle, output_pickle = None):
    if not output_pickle:
        output_pickle = "{}_normalized.pkl".format(input_pickle.split('.')[0])
    df = pd.read_pickle(input_pickle)

    df = df[pd.notnull(df).all(axis=1)]
    tmp_df = df[['PM_6182', 'PM_6179', 'PM_617B', 'PM25_6182', 'PM25_6179', 'PM25_617B', 'rh', 't_grad', 'pressure', 'temp']]
    normalized_df = (tmp_df - tmp_df.mean()) / tmp_df.std()
    df[['PM_6182', 'PM_6179', 'PM_617B', 'PM25_6182', 'PM25_6179', 'PM25_617B', 'rh', 't_grad', 'pressure', 'temp']] = normalized_df

    df.to_pickle(output_pickle)
    
def normalize_no2_pickle(input_pickle, output_pickle = None):
    if not output_pickle:
        output_pickle = "{}_normalized.pkl".format(input_pickle.split('.')[0])
    df = pd.read_pickle(input_pickle)

    df = df[pd.notnull(df).all(axis=1)]
    tmp_df = df[['NO2_61FD', 'NO2_61F0', 'NO2_61EF', 'rh', 't_grad', 'pressure', 'temp']]
    normalized_df = (tmp_df - tmp_df.mean()) / tmp_df.std()
    df[['NO2_61FD', 'NO2_61F0', 'NO2_61EF', 'rh', 't_grad', 'pressure', 'temp']] = normalized_df

    df.to_pickle(output_pickle)

def file_match_extension(filename, extension):
    return filename.split('.')[-1] == extension

def is_csv(filename):
    return file_match_extension(filename, 'csv')

def is_pickle(filename):
    return file_match_extension(filename, 'pkl')

def create_pickle(folder, data_type, out_pickle=None):
    if data_type == "NO2":
        create_no2_pkl(folder, out_pickle=out_pickle)
    elif data_type == "PM":
        create_pm_pkl(folder, out_pickle=out_pickle)
    else:
        print("Invalid type: must be PM or NO2")
        sys.exit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="clean, create_pickle, normalize_pickle modes sont disponibles.")
    parser.add_argument("input", help="input (file or folder depending on the use mode")
    parser.add_argument("--type", help="NO2/PM: mandatory except for clean mode")
    parser.add_argument("--output", help="if specified, will output in the given file/folder. Else, files are name by default")

    args = parser.parse_args()

    if args.mode not in ALLOWED_MODES:
        print("Allowed modes are {}".format(','.join(ALLOWED_MODES)))
        sys.exit()

    if args.mode == "clean":
        if not (os.path.isdir(args.input) or is_csv(args.input)):
            print("Input is not a folder or a csv file")
            sys.exit()
        clean(args.input, args.output)
    elif args.mode == "create_pickle":
        if not os.path.isdir(args.input):
            print("Input is not a folder")
            sys.exit()
        if not args.type:
            print("Type must be specified")
            sys.exit()
        create_pickle(args.input, args.type, args.output)
        
    elif args.mode == "normalize_pickle":
        if not args.type:
            print("Type must be specified")
            sys.exit()
        if not is_pickle(args.input):
            print("Input is not a pickle file")
            sys.exit()
        normalize_pickle(args.input, args.type, args.output)

if __name__ == '__main__':
    main()
