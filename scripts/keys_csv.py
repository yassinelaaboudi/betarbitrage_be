
import pandas as pd
import psutil

def convert_keys(keys_path):
    
    df_keys = pd.read_excel(keys_path)
    df_keys.to_csv(keys_path.split('.')[0] + '.csv')



def terminate_process(process_name):
    for proc in psutil.process_iter():
        try:
            # Get process details as named tuple
            process_info = proc.as_dict(attrs=['pid', 'name'])
            # Check if process name matches
            if process_info['name'] == process_name:
                # Terminate the process
                pid = process_info['pid']
                psutil.Process(pid).terminate()
                print(f"Process {process_name} with PID {pid} terminated")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print('unable to close the process') 




if __name__=='__main__':
    #convert_keys('teams_correspondancy.xlsx')
    
    terminate_process("chrome.exe")