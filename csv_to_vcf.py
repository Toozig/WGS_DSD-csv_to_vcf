import sys
import pandas as pd
import datetime
import concurrent.futures
from pandarallel import pandarallel

pandarallel.initialize(progress_bar=False)

NUM_WORKERS = 8
CSV_IDX = 1
INFO_IDX = 2
OUTPUT_IDX = 3


def get_current_date_ddmmyy():
    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime("%d%m%y")
    return formatted_date


def create_info_lines(file,col_info_file):
    VCF_VERSION ='##fileformat=VCFv4.2'
    date = f'##date={get_current_date_ddmmyy()}'
    source_file = f'##sourcefile={file}'
    ref = '##reference=hg38'
    info_s = pd.Series([VCF_VERSION,date,source_file,ref])
    info_df = pd.read_csv(col_info_file).replace(' ','.')
    info_s = pd.concat([info_s,info_df.apply(
        lambda x: f'##{x.type}=<ID={x.ID},Number={x.Number},Type={x.Dtype},Description={x.Description}>',
          axis=1)])
    return info_s

def prepare_sample(df,id):
    cols = [f'{id}:GT',f'{id}:DP',f'{id}:GQ',f'{id}:AB']
    sample_df =df[cols].copy()
    sample_df[f'{id}:GT'] = sample_df[f'{id}:GT'].replace(' ','./.').fillna('./.')
    sample_df[[f'{id}:DP',f'{id}:GQ']] = sample_df[[f'{id}:DP',f'{id}:GQ']].fillna(-1).astype(int)
    sample_df[f'{id}:AB'] =  sample_df[f'{id}:AB'].replace(0,'.')
    sample_df =sample_df.fillna('.').replace(-1,'.')
    return sample_df.parallel_apply(lambda x : ':'.join(x.astype(str).tolist()), axis=1).rename(id)

def df_to_vcf(file,info_col):
    info_df = pd.read_csv(info_col)
    df = pd.read_csv(file, low_memory=False)
    res_df = pd.DataFrame()
    res_df['#CHROM'] = df.CHROM.str.replace('chr','')
    res_df['POS'] = df.POS
    res_df['ID'] = '.'
    res_df['REF'] = df.REF
    res_df['ALT'] = df.ALT
    res_df['QUAL'] = 0
    res_df['FILTER'] = df.FILTER.replace(' ','.')
    INFO_cols = info_df[info_df.type == 'INFO'].ID
    INFO_cols = INFO_cols[INFO_cols.isin(df.columns)]
    df.loc[:,INFO_cols] = df[INFO_cols].replace(' ','.').fillna('.')
    res_df['INFO'] = df.parallel_apply(lambda x: ';'.join([f'{i}={x[i]}' for i in INFO_cols]),axis=1)
    FORMAT_cols = info_df[info_df.type == 'FORMAT'].ID
    format = ':'.join(FORMAT_cols.tolist())
    res_df['FORMAT'] = format
    samples = set([i.split(':')[0] for i in df.columns if ':' in i])

    # Create a ThreadPoolExecutor to run the function in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # Submit the function for each item in the list
        # This starts the parallel execution
        futures = [executor.submit(lambda x:prepare_sample(df,x) , id) for id in samples]

        # Wait for all tasks to complete and retrieve the results
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    sample_df = pd.concat(results, axis=1)
    res_df = pd.concat([res_df,sample_df], axis=1)
    return res_df


def main(file, col_info_file, output_name):
    print("Prepare info")
    info_s =create_info_lines(file, col_info_file)
    print("Prepare data")
    vcf_df = df_to_vcf(file, col_info_file).T.reset_index().T
    output_name = file.replace('csv','vcf').split('/')[-1]
    vcf_df = pd.concat([info_s,vcf_df])
    print("saving")
    vcf_df.to_csv(output_name,sep='\t',index=False,header=None)
    print(f'Saved as {output_name}')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Error: Insufficient command line arguments.")
        print("Usage: python csv_to_vcf.py csv_file col_info_file output_name")
        sys.exit(1)
    
    csv_file = sys.argv[CSV_IDX]
    col_info_file = sys.argv[INFO_IDX]
    output_name = sys.argv[OUTPUT_IDX]
    main(csv_file, col_info_file, output_name)
    
    