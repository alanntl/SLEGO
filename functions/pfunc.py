import numpy as np
import pandas as pd
import os
import dtale
import panel as pn
import datetime
import yahoo_fin.stock_info as si
import datetime
from typing import Union
import os

default_data_path = './data/'
result =None
import param

class FileBlock(param.Parameterized):
    def __init__(self, folderpath ,**params):
        self.folderpath = folderpath
        self.selected_file_path = None
        self.messagebox = pn.widgets.TextAreaInput( name='File name',placeholder='Input file name for file rename or duplicate')
        self.filesselector = pn.widgets.MultiSelect(name='Select data files',options = self.get_files(), size=20)
        self.btn_duplicate = pn.widgets.Button(name='Duplicate',button_type='success')
        self.btn_rename = pn.widgets.Button(name='Rename', button_type='primary')
        self.btn_delete = pn.widgets.Button(name='Delete', button_type='danger')
        self.file_import = pn.widgets.Button(name='Import uploaded file')
        self.filedownload = pn.widgets.FileDownload(filename='Download')
        self.file_input = pn.widgets.Button(name="Upload file")
        self.folderpath_input = pn.widgets.Select( name='Folder path name:',options=self.get_subfolders())
        self.btn_refresh = pn.widgets.Button(name="Refresh folder")

        self.filesselector.param.watch(self.filesselector_change, 'value')
        self.btn_rename.on_click(self.btn_rename_click)
        self.btn_duplicate.on_click(self.btn_duplicate_click)
        self.btn_delete.on_click(self.btn_delete_click)
        self.file_import.param.watch(self.file_import_clicked, 'value')
        self.file_input.on_click(self.file_upload_clicked)
        self.folderpath_input.param.watch(self.folder_path_change, 'value')

    def get_files(self,folder_path='./data/'):
        file_list= [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return file_list
        
    def get_subfolders(self,folder_path='./data/'):
        subfolder_list= [x[0] for x in os.walk(folder_path)]
        return subfolder_list

    def folder_path_change(self,event):
        self.folderpath =  self.folderpath_input.value
        self.filesselector.options = self.get_files()

    def filesselector_change(self,event):
        self.messagebox.value = str(self.filesselector.value).replace("[", "").replace("]", "")
        if self.filesselector.value!= []:
            self.filedownload.filename = self.filesselector.value[0]
            self.filedownload.file = self.folderpath + self.filesselector.value[0]
            self.selected_file_path = self.folderpath + self.filesselector.value[0]
        
    def btn_rename_click(self,event):   
        self.filesselector.value = [self.filesselector.value[0]]
        old_filename = self.folderpath + self.filesselector.value[0]
        new_filename = self.folderpath + self.messagebox.value.replace("[", "").replace("]", "")
        os.rename(old_filename, new_filename)
        self.filesselector.options = self.get_files()

    def btn_duplicate_click(self,event):   
        time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        for i in range(len(self.filesselector.value)):
            old_filename = self.folderpath + self.filesselector.value[i]
            new_filename = str(self.folderpath + self.filesselector.value[i]+'_copy_'+time_str).replace('.csv','')+ '.csv'
            shutil.copyfile(old_filename, new_filename)
            self.filesselector.options = self.get_files()

    def btn_delete_click(self,event):   
        fileslist = self.filesselector.value[:]
        for i in range(len(fileslist)):
            file = pathlib.Path(self.folderpath + fileslist[i])
            file.unlink()
        self.filesselector.options = self.get_files()

    def file_upload_clicked(self,*b):
        root = Tk()
        root.withdraw()                                        
        root.call('wm', 'attributes', '.', '-topmost', True)   
        self.uploaded_files = filedialog.askopenfilename(multiple=True)  
        self.messagebox.value = 'Uploaded file: ' +str(self.uploaded_files)
        return self.uploaded_files                 

    def file_import_clicked(self,event):
        self.messagebox.value = 'Imported files: \n'
        for i in range(len(self.uploaded_files)):
            shutil.copyfile(self.uploaded_files[i], self.folderpath+os.path.basename(self.uploaded_files[i]))
            self.messagebox.value += os.path.basename(self.uploaded_files[i])+'\n'
        self.filesselector.options = self.get_files()

    def btn_refresh_click(self,event):
        self.refresh_directory()

    def refresh_directory(self):
        self.fileblock.filesselector.options = os.listdir(self.fileblock.folderpath)

    @property
    def view(self):
        return pn.Column(
            self.folderpath_input,
            self.filesselector,
            self.btn_refresh,
            self.messagebox ,
            pn.Row(self.btn_rename,self.btn_duplicate,self.btn_delete,),
            pn.widgets.StaticText(value='Upload and then import files:'), self.file_input,self.file_import,
            pn.widgets.StaticText(value='Select files to download:'),self.filedownload, 
            max_width=300
            )


def data_management_app(folder_path:str='./data'):

    """
    Instruction:\n
    input: data folder path\n
    output: pop-up browser webapp \n
    
    """
    fileblock=  FileBlock(folder_path)
    import random
    port_number = random.randint(1000,9999)
    fileblock.view.show(port=port_number)


def visualize_csv_in_dtale(csv_file_name:str='./data/output1.csv'):
    """
    Instruction:\n
    input: csv file path\n
    output: pop-up browser webapp\n
    
    """
    df = pd.read_csv(csv_file_name)
    dtale_obj = dtale.show(df)
    dtale_obj.open_browser()
    return None

def get_marketdata_yahoo_csv(ticker:str='msft', start_date:str =  (datetime.datetime.now()- datetime.timedelta(days=365)).strftime("%Y-%m-%d"),
                                            end_date:str = datetime.datetime.now().strftime("%Y-%m-%d"), 
                                            output_csv_name:str ='./data/output1.csv' ):
                                            #output_csv_name:str ='result_get_marketdata_yahoo'+'_'+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+ '.csv' ):
    """ 
    This is the function that get yahoo finance market data!
    ticker:str='msft', start_date:str =  (datetime.datetime.now()- datetime.timedelta(days=365)).strftime("%Y-%m-%d"),
                                                end_date:str = datetime.datetime.now().strftime("%Y-%m-%d"), 
                                                output_csv_name:str ='./data/output1.csv' ):    

    output: csv table 
    columns: open,high,low,close,adjclose,volume,ticker,Datetime
    
    """
    data = si.get_data(ticker , start_date = start_date , end_date = end_date)
    data['Datetime'] = data.index
    csvfile = data.to_csv(output_csv_name)
    return data


def get_marketdata_yahoo_df(ticker:str='msft', start_date:str =  (datetime.datetime.now()- datetime.timedelta(days=365)).strftime("%Y-%m-%d"),
                                            end_date:str = datetime.datetime.now().strftime("%Y-%m-%d")):
    """
    Instruction:\n
    output: pandas object\n
    columns: open,high,low,close,adjclose,volume,ticker,Datetime\n
    """
    data = si.get_data(ticker , start_date = start_date , end_date = end_date)
    data['Datetime'] = data.index
    return data


def visualize_dataframe_in_dtale(dataframe:object='output1'):
    """
    Instruction:\n
    input: please type output 1 (the default return of the last function)\n
    output: pop-up browser webapp\n
    
    """
    dtale_obj = dtale.show(dataframe)
    dtale_obj.open_browser()
    return None

def get_technical_indicators_to_csv(data_path:str = './data/output1.csv', output_csv_name:str='./data/output1.csv'):
    """
    Instruction:\n
    input: market data extract from yahoo api\n
    only for csv format\n
    output: same csv table but added Technical indicator\n
    columns: open,high,low,close,adjclose,volume,ticker,Datetime,rsi,STOCH_k,STOCH_d,return_daily,return_weekly,return_monthly\n
    """

    import talib
    df= pd.read_csv(data_path)

    c = df['adjclose']

    # this is the library function
    k, d = talib.STOCHRSI(c)

    # this produces the same result, calling STOCHF
    rsi = talib.RSI(c)
    k, d = talib.STOCHF(rsi, rsi, rsi)

    # you might want this instead, calling STOCH
    rsi = talib.RSI(c)
    k, d = talib.STOCH(rsi, rsi, rsi)

    df['rsi'] =rsi
    df['STOCH_k'] =k
    df['STOCH_d'] = d
    df['return_daily'] = c.pct_change()
    df['return_weekly'] = c.pct_change(5)
    df['return_monthly'] = c.pct_change(20)
    df['Datetime'] = df.index

    csvfile = df.to_csv(output_csv_name)
    return df


def autoML__structural_data_prediction(train_file_path:str='./data/train.csv', test_file_path:str='./data/test.csv', 
                                        target_column:str='target', epochs:int=10, max_trials:int=3,
                                        output_csv_filename:str='./data/prediction.csv'):

    """
    Instruction:\n
    1. input 2 two csv file: train.csv and test. csv\n
    2. columns : PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,Cabin,Embarked\n
    3. output a csv file\n
    """
    import autokeras as ak
    # Initialize the structured data classifier.
    clf = ak.StructuredDataClassifier(
        overwrite=True, max_trials=max_trials
    )  # It tries 3 different models.
    # Feed the structured data classifier with training data.
    clf.fit(
        # The path to the train.csv file.
        train_file_path,
        # The name of the label column.
        target_column,
        epochs=epochs,
    )
    # Predict with the best model.
    predicted_y = clf.predict(test_file_path)
    # Evaluate the best model with testing data.
    #print(clf.evaluate(test_file_path))
    print(clf.predict(test_file_path))
    df= pd.read_csv(test_file_path)
    df['predicted_y'] =predicted_y
    df.to_csv(output_csv_filename)
    return df