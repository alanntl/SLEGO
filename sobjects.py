import panel as pn
import numpy as np
import holoviews as hv
import ast
import param
pn.extension('terminal','tabulator','texteditor','plotly', sizing_mode='stretch_width')
import pandas as pd
import inspect
from collections import ChainMap
import os
import datetime
import shutil
import pathlib
import plotly.express as px
import func
import time
import webbrowser
import dtale
import uuid
import typing
#from tkinter import Tk, filedialog
import ipywidgets as widgets
import json
import contextlib
import io
import threading
from unicodedata import name

#from turtle import title

# datafileblock
class DataFileBlock(param.Parameterized):
    def __init__(self, folderpath='./data/' ,**params):
        self.folderpath = folderpath
        self.selected_file_path = None
        self.messagebox = pn.widgets.TextAreaInput( name='File name',placeholder='Input file name for file rename or duplicate')
        self.filesselector = pn.widgets.MultiSelect(name='Select data files',options = self.get_files(self.folderpath), size=20)
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
        #self.file_input.on_click(self.file_upload_clicked)
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
        #time.sleep(1)
        #self.filesselector.options = self.get_files()

    # def file_upload_clicked(self,*b):
    #     root = Tk()
    #     root.withdraw()                                        
    #     root.call('wm', 'attributes', '.', '-topmost', True)   
    #     self.uploaded_files = filedialog.askopenfilename(multiple=True)  
    #     self.messagebox.value = 'Uploaded file: ' +str(self.uploaded_files)
    #     return self.uploaded_files                 

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

#DataFileBlockin =DataFileBlock()
#DataFileBlockin.view

# ProgramFileBlock
class ProgramFileBlock(param.Parameterized):
    def __init__(self, folderpath ,**params):
        self.folderpath = folderpath
        self.selected_file_path = None
        self.messagebox = pn.widgets.TextAreaInput( name='File name',placeholder='Input file name for file rename or duplicate')
        self.filesselector = pn.widgets.MultiSelect(name='Select saved function files',options = self.get_files(), size=20)
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
        #self.file_input.on_click(self.file_upload_clicked)
        self.folderpath_input.param.watch(self.folder_path_change, 'value')

    def get_files(self,folder_path='./user_function/'):
        file_list= [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return file_list
        
    def get_subfolders(self,folder_path='./user_function/'):
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
            new_filename = str(self.folderpath + self.filesselector.value[i]+'_copy_'+time_str).replace('.json','')+ '.json'
            shutil.copyfile(old_filename, new_filename)
            self.filesselector.options = self.get_files()

    def btn_delete_click(self,event):   
        fileslist = self.filesselector.value[:]
        for i in range(len(fileslist)):
            file = pathlib.Path(self.folderpath + fileslist[i])
            file.unlink()
        self.filesselector.options = self.get_files()

    # def file_upload_clicked(self,*b):
    #     root = Tk()
    #     root.withdraw()                                        
    #     root.call('wm', 'attributes', '.', '-topmost', True)   
    #     self.uploaded_files = filedialog.askopenfilename(multiple=True)  
    #     self.messagebox.value = 'Uploaded file: ' +str(self.uploaded_files)
    #     return self.uploaded_files                 

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

#FunctionFileBlock

class FunctionFileBlock(param.Parameterized):
    def __init__(self, folderpath ,**params):
        self.folderpath = folderpath
        self.selected_file_path = None
        self.messagebox = pn.widgets.TextAreaInput( name='File name',placeholder='Input file name for file rename or duplicate')
        self.filesselector = pn.widgets.MultiSelect(name='Select saved function files',options = self.get_files(), size=20)
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
        #self.file_input.on_click(self.file_upload_clicked)
        self.folderpath_input.param.watch(self.folder_path_change, 'value')

    def get_files(self,folder_path='./functions/'):
        file_list= [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return file_list
        
    def get_subfolders(self,folder_path='./functions/'):
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
            new_filename = str(self.folderpath + self.filesselector.value[i]+'_copy_'+time_str).replace('.py','')+ '.py'
            shutil.copyfile(old_filename, new_filename)
            self.filesselector.options = self.get_files()

    def btn_delete_click(self,event):   
        fileslist = self.filesselector.value[:]
        for i in range(len(fileslist)):
            file = pathlib.Path(self.folderpath + fileslist[i])
            file.unlink()
        self.filesselector.options = self.get_files()

    # def file_upload_clicked(self,*b):
    #     root = Tk()
    #     root.withdraw()                                        
    #     root.call('wm', 'attributes', '.', '-topmost', True)   
    #     self.uploaded_files = filedialog.askopenfilename(multiple=True)  
    #     self.messagebox.value = 'Uploaded file: ' +str(self.uploaded_files)
    #     return self.uploaded_files                 

    def file_import_clicked(self,event):
        self.messagebox.value = 'Imported files: \n'
        for i in range(len(self.uploaded_files)):
            shutil.copyfile(self.uploaded_files[i], self.folderpath+os.path.basename(self.uploaded_files[i]))
            self.messagebox.value += os.path.basename(self.uploaded_files[i])+'\n'
        self.filesselector.options = self.get_files()


    @property
    def filepath(self):
        return  self.folderpath_input.value+ self.filesselector.value[0]

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

# functionfileblock =FunctionFileBlock(folderpath= './functions/')
# functionfileblock.view


# DataPreviewBlock
class DataPreviewBlock(param.Parameterized):
    def __init__(self,  **params):
        self.df= None
        self.tabulator = pn.widgets.Tabulator( pagination='remote')
        self.choidx = pn.widgets.MultiChoice(name='Select index',options=['index'])
        self.mulchocol = pn.widgets.MultiChoice(name='Select value')
        self.seltype = pn.widgets.Select(name='select chart type', options=['scatter','bar','line', 'histogram', 'box'])
        self.plot = pn.pane.Plotly(sizing_mode='fixed')

        self.selformat= pn.widgets.Select(name='select data format', options=['csv','json', 'xml', 'html', 'excel'])
        #self.choidx.param.watch(self.mulchocol_selected, 'value')
        self.mulchocol.param.watch(self.mulchocol_selected, 'value')
        self.choidx.param.watch(self.mulchocol_selected, 'value')
        self.seltype.param.watch(self.mulchocol_selected, 'value')

        self.slide_height = pn.widgets.EditableIntSlider(name='Height', start=0, end=5000, step=50, value=500)
        self.slide_width = pn.widgets.EditableIntSlider(name='Width',  start=0, end=5000, step=50, value=1500)
        self.slide_height.param.watch(self.slider_changed, 'value')
        self.slide_width.param.watch(self.slider_changed, 'value')

    def slider_changed(self,event):
        self.plot.width = self.slide_width.value
        self.plot.height = self.slide_height.value

    def mulchocol_selected(self,event):
        if self.choidx.value ==[] or self.mulchocol.value == []:
            self.plot.object = None
            return
        self.plot.object=None
        df = self.df.convert_dtypes()
        ptype = self.seltype.value
        df['index'] =df.index

        if self.choidx.value[0] != [] or self.choidx.value[0] != 'index':
            index = self.choidx.value[0]
            df.sort_values(by=[index])
            df = df.set_index([index])

        if len(self.choidx.value)> 1:
            event.obj.value = [self.choidx.value[0]]
            return
        df = df[self.mulchocol.value]

        fig =eval('px.'+ptype)(df)
        fig.update_layout(legend=dict(orientation="h",  yanchor="top"))
        self.plot.object = fig
  
    def feed_data(self, data_path):
        self.choidx.value =[]
        self.mulchocol.value = []

        if self.selformat.value =='csv':
            data = pd.read_csv(data_path)
        elif self.selformat.value =='json':
            data = pd.read_json(data_path)
        elif self.selformat.value =='excel':
            data = pd.read_excel(data_path)
        elif self.selformat.value =='xml':
            data = pd.read_xml(data_path)
        elif self.selformat.value =='html':
            data = pd.read_html(data_path)

        self.df = data
        self.tabulator.value = data
        columns_list = data.columns.to_list()
        self.choidx.options = ['index']+columns_list
        self.mulchocol.options = columns_list

        self.choidx.value = ['index']
        self.mulchocol.value = [columns_list[0]]

    @property
    def view(self):
        return pn.Column(
            pn.Row(self.selformat,
            self.mulchocol,
            self.choidx,
            self.seltype,),
            pn.Row(self.slide_height, self.slide_width),
            self.plot,
            pn.Card(self.tabulator,collapsed=False, title= 'Expand for table view' )
            )

#chartblock = DataBlock()
#chartblock.view

# ProgramFilePreview

class ProgramFilePreviewBlock(param.Parameterized):
    def __init__(self,  **params):
        self.paneJSON = pn.pane.JSON(name='Program File Visualization',depth=-1,theme='light' )
        

    def feed_data(self, data_path='user_function\program.json'):
        with open(data_path, 'r') as f:
            json_obj = json.load(f)      
        self.paneJSON.object=  json_obj
        self.paneJSON.name =data_path

    @property
    def view(self):
        return pn.Column(self.paneJSON)


# Function EditorBlock
class FunctionEditorBlock(param.Parameterized):
    def __init__(self,  **params):

        self.editor = pn.widgets.TextAreaInput(name='Function file:',height=500)
        
        self.filepath = pn.widgets.TextInput(name='Function file path:', value ='./functions/pfunc.py' )

        self.btn_open = pn.widgets.Button(name = 'Open file', button_type= 'success', max_width=100)
        self.btn_open.on_click(self.btn_open_clicked)

        self.btn_overwrite = pn.widgets.Button(name = 'Write/change file', button_type= 'warning', max_width=100)
        self.btn_overwrite.on_click(self.btn_write_clicked)

    def btn_write_clicked(self,event):

        text= self.editor.value 
        path = self.filepath .value
        try:
            with open(path, 'x') as f:
                f.write(text)
        except:
            with open(path, 'w') as f:
                f.write(text)    

    def btn_open_clicked(self,event):
        path = self.filepath.value
        code=''
        with open(path, "r") as f:
            s = f.read()
            code += s
            my_list = code.split('\n')
            result = '\n'.join(my_list)
        self.editor.value =result        


    @property
    def view(self):
        return pn.Column(self.filepath ,pn.Row(self.btn_open,self.btn_overwrite), self.editor)

# functioneditorblock =FunctionEditorBlock()
# functioneditorblock.view

#functioneditorblock.editor.value=functioneditorblock


# FunctionBlock


class FuncSelector(param.Parameterized):
    def __init__(self, module, datapath='./data/', tag='first'):
        self.tag=tag
        self.data_format = [pd.DataFrame ] #['_data']
        self.messagebox = pn.widgets.TextInput( name='Message', placeholder='1 select a function, 2 input parameters , 3 click compute button')
        self.datapath = datapath
        self.module = module
        self.funcs_dict, self.funcs_name_list, self.funcs_argument_list = self.get_function_name() #+type list
        self.btn_compute = pn.widgets.Button(name='Compute Block', button_type = 'primary')
        self.sel_func = pn.widgets.MultiChoice(name='Select an analytic service:', options=['']+self.funcs_name_list, max_items =1)
        self.card_param = pn.Card(title='Input parameters:')
        self.sel_func.param.watch(self.select_func_change, 'value')
        self.btn_compute.on_click(self.btn_compute_clicked)
        self.func_name = None
        self.func_param_dict = None
        self.func = None
        self.data_list = None
        self.func_param_dict = [] #!!
        self.result = None
        self.display = pn.Column()
        self.text_input_save = pn.widgets.TextInput(name='output data names' ,placeholder='result_functionName_[current_time].csv')
        self.param_type = {}
        self.data_param_list = []
        self.func_desc = pn.widgets.TextInput(name='Instruction' ,height_policy='max')

    
    def btn_compute_clicked(self,event):
        self.btn_compute.button_type = 'warning'
        self.display.clear()
        self.messagebox.placeholder = 'Computing...please wait'
        start_time = time.time()
        self.result = self.func(**self.func_param_dict)
        exec_time = time.time() - start_time
        self.messagebox.placeholder = 'execution time: '+str( round(exec_time,3))+ ' seconds.' +' Saving the file...'
        self.btn_compute.button_type = 'success'
    
    def select_func_change(self,event):
        self.func_desc.value=''
        self.display.clear()
        self.btn_compute.button_type = 'primary'
        self.card_param.clear()
        if self.sel_func.value == []:
            return
        self.func_value = self.sel_func.value[-1]
        self.func_name = self.func_value 
        self.func = eval('self.module.'+self.func_name)
        self.param_type = inspect.getfullargspec(self.func)[6] 
        self.func_param_dict = self.funcs_dict[self.func_value ]
        self.param_inputs = []    

        for k,v in self.func_param_dict.items():
            if self.param_type[k] in self.data_format: #if k =='data':
                arg_input = pn.widgets.MultiChoice(name=k,options=os.listdir(self.datapath) ) # not textinput , is multichoice
                arg_input.param.watch(self.select_data_changed, 'value')
                self.data_param_list.append(arg_input)
            else:
                arg_input = pn.widgets.LiteralInput(name=k, value=v)
                arg_input.param.watch(self.text_changed,'value')
            self.param_inputs.append(arg_input)
        self.card_param.objects = self.param_inputs
        self.func_desc.value = self.func.__doc__

    def select_data_changed(self,event):
        self.display.clear()
        if len(event.obj.value)> 1:
            event.obj.value = [event.obj.value[0]]
            return

        self.btn_compute.button_type = 'primary'
        self.data_list = []
        sinput_list = event.obj.value
        for sinput in sinput_list:
            data = pd.read_csv(self.datapath+sinput)
            #data.drop(["Unnamed: 0"], axis=1, inplace=True)
            self.data_list.append(data)
        self.func_param_dict[event.obj.name] = self.data_list[0] 

    def text_changed(self,event):
        self.btn_compute.button_type = 'primary'
        #https://panel.holoviz.org/user_guide/Links.html?highlight=event
        self.func_param_dict[event.obj.name] = event.obj.value

    def get_function_name(self):
        funcs = inspect.getmembers(self.module, inspect.isfunction)
        funcs_name_list = [fun[0] for fun in funcs]
        funcs_argument_list = [inspect.getfullargspec(fun[1])[0]  for fun in funcs]
        funcs_argument_default_list = [inspect.getfullargspec(fun[1])[3]  for fun in funcs]
        funcs_dict = [{f:dict(zip(a,d))} for f,a,d in zip(funcs_name_list, funcs_argument_list, funcs_argument_default_list)]
        funcs_dict =dict(ChainMap(*funcs_dict ))
        return funcs_dict, funcs_name_list, funcs_argument_list #+type list

    @property
    def view(self):
        return pn.Row( 
            pn.Column(self.sel_func,
            pn.Row(self.messagebox),
            self.display,),self.card_param,self.func_desc)



class FuncSelector(param.Parameterized):
    def __init__(self, module, datapath='./data/', tag='first'):
        self.tag=tag
        self.data_format = [pd.DataFrame ] #['_data']
        self.messagebox = pn.widgets.TextInput( name='Message', placeholder='1 select a function, 2 input parameters , 3 click compute button')
        self.datapath = datapath
        self.module = module
        self.funcs_dict, self.funcs_name_list, self.funcs_argument_list = self.get_function_name() #+type list
        self.btn_compute = pn.widgets.Button(name='Compute Block', button_type = 'primary')
        self.sel_func = pn.widgets.MultiChoice(name='Select an analytic service:', options=['']+self.funcs_name_list, max_items =1)
        self.card_param = pn.Card(title='Input parameters:')
        self.sel_func.param.watch(self.select_func_change, 'value')
        self.btn_compute.on_click(self.btn_compute_clicked)
        self.func_name = None
        self.func_param_dict = None
        self.func = None
        self.data_list = None
        self.func_param_dict = [] #!!
        self.result = None
        self.display = pn.Column()
        self.text_input_save = pn.widgets.TextInput(name='output data names' ,placeholder='result_functionName_[current_time].csv')
        self.param_type = {}
        self.data_param_list = []
        self.func_desc = pn.widgets.TextInput(name='Instruction' ,height_policy='max')

    
    def btn_compute_clicked(self,event):
        self.btn_compute.button_type = 'warning'
        self.display.clear()
        self.messagebox.placeholder = 'Computing...please wait'
        start_time = time.time()
        self.result = self.func(**self.func_param_dict)
        exec_time = time.time() - start_time
        self.messagebox.placeholder = 'execution time: '+str( round(exec_time,3))+ ' seconds.' +' Saving the file...'
        self.btn_compute.button_type = 'success'
    
    def select_func_change(self,event):
        self.func_desc.value=''
        self.display.clear()
        self.btn_compute.button_type = 'primary'
        self.card_param.clear()
        if self.sel_func.value == []:
            return
        self.func_value = self.sel_func.value[-1]
        self.func_name = self.func_value 
        self.func = eval('self.module.'+self.func_name)
        self.param_type = inspect.getfullargspec(self.func)[6] 
        self.func_param_dict = self.funcs_dict[self.func_value ]
        self.param_inputs = []    

        for k,v in self.func_param_dict.items():
            if self.param_type[k] in self.data_format: #if k =='data':
                arg_input = pn.widgets.MultiChoice(name=k,options=os.listdir(self.datapath) ) # not textinput , is multichoice
                arg_input.param.watch(self.select_data_changed, 'value')
                self.data_param_list.append(arg_input)
            else:
                arg_input = pn.widgets.LiteralInput(name=k, value=v)
                arg_input.param.watch(self.text_changed,'value')
            self.param_inputs.append(arg_input)
        self.card_param.objects = self.param_inputs
        self.func_desc.value = self.func.__doc__

    def select_data_changed(self,event):
        self.display.clear()
        if len(event.obj.value)> 1:
            event.obj.value = [event.obj.value[0]]
            return

        self.btn_compute.button_type = 'primary'
        self.data_list = []
        sinput_list = event.obj.value
        for sinput in sinput_list:
            data = pd.read_csv(self.datapath+sinput)
            #data.drop(["Unnamed: 0"], axis=1, inplace=True)
            self.data_list.append(data)
        self.func_param_dict[event.obj.name] = self.data_list[0] 

    def text_changed(self,event):
        self.btn_compute.button_type = 'primary'
        #https://panel.holoviz.org/user_guide/Links.html?highlight=event
        self.func_param_dict[event.obj.name] = event.obj.value

    def get_function_name(self):
        funcs = inspect.getmembers(self.module, inspect.isfunction)
        funcs_name_list = [fun[0] for fun in funcs]
        funcs_argument_list = [inspect.getfullargspec(fun[1])[0]  for fun in funcs]
        funcs_argument_default_list = [inspect.getfullargspec(fun[1])[3]  for fun in funcs]
        funcs_dict = [{f:dict(zip(a,d))} for f,a,d in zip(funcs_name_list, funcs_argument_list, funcs_argument_default_list)]
        funcs_dict =dict(ChainMap(*funcs_dict ))
        return funcs_dict, funcs_name_list, funcs_argument_list #+type list

    @property
    def view(self):
        return pn.Row( 
            pn.Column(self.sel_func,
            pn.Row(self.messagebox),
            self.display,),self.card_param,self.func_desc)


# FunctionStack

from unicodedata import name
class FunctionStack(param.Parameterized):

    def __init__(self, datapath='./data/',functions_module=None):
        self.datapath = datapath
        self.functions_module= functions_module
        self.menu_items = [('Add', 'add'), ('Delete', 'delete'), ('Analyze', 'analyze')]

        self.btn_compute = pn.widgets.Button(name='Compute Stacks', button_type='primary', items=self.menu_items,max_width=100, tag='first')
        self.btn_compute.on_click(self.btn_compute_clicked)
        btn_add = pn.widgets.Button(name='Add Block', button_type='success', items=self.menu_items,max_width=100, tag='first')
        btn_add.on_click(self.btn_add_clicked)

        functionblock = FuncSelector(func, tag='first')
        combo = pn.WidgetBox(functionblock.view, btn_add, pn.layout.Divider(),tag='first')
        self.combostack = pn.WidgetBox(objects=[combo])
        self.block_list = [functionblock]
        #self.textbox = pn.widgets.TextInput(name='Function stack message:')
        self.result = None
        #self.outputtext = pn.widgets.TextAreaInput(name='Jupyter output capture:')
        #self.output = widgets.Output()
        # self.btn_save = pn.widgets.Button(name='Save Stacks', button_type='warning',  max_width=100, tag='first')
        # self.btn_save.on_click(self.btn_save_clicked)
        # self.textbox_save_func = pn.widgets.TextInput(name='Save/Load function stack with name:', value='./saved_function/app.json' )
        # self.btn_load = pn.widgets.Button(name='Load Stacks', button_type='success',  max_width=100, tag='first')
        # self.btn_load.on_click(self.click_load_functions)
        self.btn_delete_list = []
        self.btn_clear = pn.widgets.Button(name='Clear Blocks', button_type='danger',  max_width=100, tag='first')
        self.btn_clear.on_click(self.btn_clear_clicked)

    def btn_clear_clicked(self,event):

        while len(self.btn_delete_list)>0:
            self.btn_delete_list[-1].clicks += 1

         
    def btn_compute_clicked(self,event):
        #with self.output:
        for i in range(len(self.block_list)):
            for key in self.block_list[i].func_param_dict:
                if self.block_list[i].func_param_dict[key] == 'output1':
                    self.block_list[i].func_param_dict[key] = self.result
            self.block_list[i].btn_compute_clicked(self.block_list[i].btn_compute)
            self.result = self.block_list[i].result
            time.sleep(1)
            #self.textbox.value = f'finsih computing function {i+1}: {self.block_list[i].func_name} '  
            self.block_list[i].btn_compute.button_type = 'primary'
            #self.outputtext.value = str(self.output.outputs)
  
    def btn_add_clicked(self,event):
        idx = 1
        try:
            btn_tag = event.obj.tag
        except:
            btn_tag = 'first'

        if btn_tag!='first':
            for i in range(1, len(self.combostack)):
                if self.combostack[i].tag == btn_tag:
                    idx = i +1
                    break

        tag = str(uuid.uuid4())
        btn_add = pn.widgets.Button(name='Add Blocks', button_type='success', items= self.menu_items,max_width=100, tag=tag)
        btn_add.on_click(self.btn_add_clicked)
        btn_delete = pn.widgets.Button(name='Delete Blocks', button_type='danger', items= self.menu_items,max_width=100, tag=tag)
        btn_delete.on_click(self.click_del)

        self.btn_delete_list.insert(idx,btn_delete)
        
        functionblock = FuncSelector(func, tag=tag)
        combo = pn.WidgetBox(functionblock.view, pn.Row(btn_add, btn_delete,  tag=tag), pn.layout.Divider(tag=tag), tag=tag) 
        self.combostack.insert(idx, combo)
        self.block_list.insert(idx, functionblock)
        #self.textbox.value = 'Add block: '+str(tag)

    def click_del(self,event):
        tag = event.obj.tag
        #self.textbox.value = str(tag)
        
        for i in range(0,len(self.combostack)):
            if self.combostack[i].tag == tag:
                combo_select = self.combostack[i]

            if self.block_list[i].tag == tag:
                functionblock_select = self.block_list[i]

            try:
                if self.btn_delete_list[i].tag == tag:
                    btn_delete = self.btn_delete_list[i]
            except:
                pass

        #self.textbox.value = 'Delete block: '+str(tag)
        self.combostack.remove(combo_select)
        self.block_list.remove(functionblock_select) 
        self.btn_delete_list.remove(btn_delete) 
        #self.del_widgets_recursive(combo_select) 
        del functionblock_select
        del combo_select
        self.block_list[0].sel_func.value=[]

    
    def del_widgets_recursive(self, widget):
        if hasattr(widget,'objects'):          
            child_wid_list = widget.objects
            for child_wid in child_wid_list:
                self.del_widgets_recursive(child_wid) # recursing here
            widget.clear()
            del widget
        else:
            del widget
        del widget
    @property

    def view(self):
        return pn.Column( self.combostack, pn.Row(self.btn_clear))    
        
#functionstack =  FunctionStack()
#functionstack.view




# FunctionPack

class FunctionPack(param.Parameterized):
    def __init__(self, datapath='./data/',functions_module=None):
        funcstack =  FunctionStack()
        self.btn_add = pn.widgets.Button(name='Add Stack',max_width=125, button_type = 'success' )
        self.btn_add.on_click(self.btn_add_clicked)
        self.btn_del = pn.widgets.Button(name='Delete Stack',max_width=125, button_type = 'danger')
        self.btn_del.on_click(self.btn_del_clicked)
        self.btn_compute_all = pn.widgets.Button(name='Compute Stacks',max_width=125, button_type = 'primary')
        self.btn_compute_all.on_click(self.btn_compute_all_clicked)

        self.btn_clear = pn.widgets.Button(name='Clear Stacks',max_width=125, button_type = 'danger')
        self.btn_clear.on_click(self.btn_clear_clicked)

        self.stack_list= [funcstack]
        self.tabs = pn.Tabs(('Function Stack 0',self.stack_list[-1].view))

    def btn_clear_clicked(self, event):
        if len(self.tabs)>0:
            len_tabs = len(self.tabs)
            for idx in range(len_tabs):
                self.tabs.remove(self.tabs[-1])
                funcstack = self.stack_list[-1]
                self.stack_list.remove(funcstack)
                del funcstack

    def btn_compute_all_clicked(self, event):
        for program in self.stack_list:
            #program.textbox.value= str(program)
            program.btn_compute_clicked(program.btn_compute)

    def btn_del_clicked(self, event):
        if len(self.tabs)>0:
            idx = self.tabs.active
            self.tabs.remove(self.tabs[idx])
            funcstack = self.stack_list[idx]
            self.stack_list.remove(funcstack)
            del funcstack

    def btn_add_clicked(self, event):
        funcstack = FunctionStack()
        num = len(self.stack_list)
        self.tabs.append(('Function Stack '+str(num),funcstack.view))
        self.stack_list.append(funcstack)

    @property
    def view(self):
        return pn.Column(pn.Row(self.btn_add,self.btn_del,self.btn_clear),self.tabs)    

#functionpack = FunctionPack()
#functionpack.view


# FunctionLayer

class FunctionLayer(param.Parameterized):
    def __init__(self, datapath='./data/',functions_module=None):
        functionpack = FunctionPack()
        self.pack_list=[functionpack]
        self.accordian = pn.Accordion(('Layer 0',functionpack.view),toggle =False, active=[0])
        self.btn_compute = pn.widgets.Button(name='Compute Program', button_type = 'primary',max_width=150)
        self.btn_clear = pn.widgets.Button(name='Clear Layers', button_type = 'danger',max_width=150)
        self.btn_add = pn.widgets.Button(name='Add Layer', button_type = 'success',max_width=150)
        self.btn_del = pn.widgets.Button(name='Delete Folded Layer', button_type = 'danger',max_width=150)
        self.btn_add.on_click(self.btn_add_clicked)
        self.btn_del.on_click(self.btn_del_clicked)
        self.btn_clear.on_click(self.btn_clear_clicked)
        self.btn_compute.on_click(self.btn_compute_clicked)
        self.outputlog = pn.widgets.TextAreaInput(name='Output message:',height= 200,max_length =5000000000000000,disabled =False)
        #self.outputlog = pn.widgets.StaticText(name='Static Text', value='')


    def btn_compute_clicked(self,event):

        self.outputlog.value = '============Program starts:============\n'
        run_thread = True
        thread1 = threading.Thread(target=self.thread_func,args=(self.outputlog.value,run_thread))
        thread1.start()
        
        for i in range(len(self.accordian)):
            self.pack_list[i].btn_compute_all_clicked(self.pack_list[i].btn_compute_all)

        run_thread = False

        self.outputlog.value += '\n\n============Program ends============'
            
    def btn_clear_clicked(self,event):
        for i in reversed(range(1,len(self.accordian))):
            self.accordian.remove(self.accordian[i])
            functionpack = self.pack_list[i]
            self.pack_list.remove(functionpack)
            del functionpack

        functionpack = self.pack_list[0]
        functionpack.btn_clear_clicked(functionpack.btn_clear)

    def btn_del_clicked(self,event):
        inactive_list = list(set(range(0,len(self.accordian))) - set(self.accordian.active))
        for num in reversed(inactive_list):
            self.accordian.remove(self.accordian[num])
            functionpack = self.pack_list[num]
            self.pack_list.remove(functionpack)
            del functionpack

    def btn_add_clicked(self,event):
        functionpack = FunctionPack()
        self.pack_list.append(functionpack)
        self.accordian.append(functionpack.view)
        #self.accordian.active =list(range(0,len(self.accordian)))
        #self.accordian.active =list(range(len(self.accordian))-3,len(self.accordian))
        #self.accordian[-1].name = str(len(self.accordian))  

    def thread_func(self, disp, run_thread):

        while True:
            with io.StringIO() as buf, contextlib.redirect_stdout(buf):
                time.sleep(0.000005)
                output_log =  buf.getvalue()
                try:
                    self.outputlog.value += str(output_log)
                except:
                    with io.StringIO() as err, contextlib.redirect_stdout(err):
                        output_log =  err.getvalue()
                        self.outputlog.value += str(output_log)
                if run_thread==False:
                    break
    @property
    def view(self):
        return pn.Column(pn.Row(self.btn_add, self.btn_del,self.btn_clear), pn.layout.Divider(),self.accordian,self.btn_compute,self.outputlog)    
#functionlayer = FunctionLayer()
#functionlayer.view
# Program

class Program(param.Parameterized):
    def __init__(self, datapath='./data/',functions_module=None):
        self.functionlayer = FunctionLayer()

        self.btn_save = pn.widgets.Button(name='Save Program', button_type='warning',  max_width=150, tag='first')
        self.btn_save.on_click(self.click_save_functions)
        self.textbox_save_func = pn.widgets.TextInput(name='Save/Load program name:', value='./user_function/program.json' )
        self.btn_load = pn.widgets.Button(name='Load Program', button_type='success',  max_width=150, tag='first')
        self.btn_load.on_click(self.click_load_functions)
        self.textbox =  pn.widgets.TextAreaInput(name='Program Message')

    def click_load_functions(self,event):
        filename = self.textbox_save_func.value
        with open(filename, 'r') as f:
            saved_functions = json.load(f)   
            
        functionlayer = self.functionlayer

        for key, value in saved_functions.items():
            i = int(key.split('_')[1])
            if i == 0:
                functionlayer.btn_clear_clicked(functionlayer.btn_clear)
                
            #print('layer')
            else:
                functionlayer.btn_add_clicked(functionlayer.btn_add)
            functionpack = functionlayer.pack_list[i]

            for key, value in value.items():
                j = int(key.split('_')[1])
                if j == 0:
                    functionpack.btn_clear_clicked(functionpack.btn_clear)
                #print('pack')
                functionpack.btn_add_clicked(functionpack.btn_add)
                functionstack = functionpack.stack_list[j]
                for key, value in value.items():
                    k = int(key.split('_')[1])
                    #print('stack')
                    if k != 0:
                        functionstack.btn_add_clicked(functionstack.combostack[-1].objects[1])
                    functionblock= functionstack.block_list[k]

                    for key_function_name, value_params in value.items():
                        functionblock.sel_func.value = [key_function_name]
                        num_textbox = 0
                        
                        for key_param_name, value_param_val in value_params.items():
                            functionblock.card_param[num_textbox].value = value_param_val
                            num_textbox+=1  
        self.textbox.value = 'Program has been loaded!!!'


    def click_save_functions(self,event):
        
        layer_dict ={}
        for i in range(len(self.functionlayer.pack_list)):
            pack = self.functionlayer.pack_list[i].stack_list
            pack_dict={}
            layer_dict['layer_'+str(i)]=pack_dict

            for j in range(len(pack)):
                stack = pack[j].block_list
                stack_dict= {}
                pack_dict['pack_'+str(j)]=stack_dict
                for k in range(len(stack)):
                    block =stack[k]
                    stack_dict['stack_'+str(k)]= {block.func_value: block.func_param_dict}

        filename = self.textbox_save_func.value
        with open(filename, 'w') as f:
            json.dump(layer_dict, f)

        self.textbox.value = 'Program has been saved!!!'
         
    @property
    def view(self):
        return pn.Column( pn.Row(self.btn_load,self.btn_save,self.textbox_save_func,self.textbox) ,pn.layout.Divider(), self.functionlayer.view)    




# App
from ast import Delete
from turtle import width

class App(param.Parameterized):
    def __init__(self, module= func, datapath='./data/', programpath='./user_function/', funcpath='./user_function/',open_in_browser=True):
        self.module= module
        self.datafileblock = DataFileBlock(datapath)
        self.programfileblock = ProgramFileBlock(programpath)
        self.functionfileblock =FunctionFileBlock(funcpath)

        self.functioneditorblock =FunctionEditorBlock()
        self.datapreview = DataPreviewBlock()
        self.programpreview = ProgramFilePreviewBlock()
 
        self.functioneditorblock.btn_overwrite.on_click(self.btn_write_clicked_functioneditor)
        self.functionfileblock.filesselector.param.watch(self.filesselector_change_functionfile, 'value')

        self.program = Program()
        self.program.functionlayer.btn_compute.on_click(self.btn_compute_clicked)
        self.program.btn_save.on_click(self.btn_save_clicked)

        #self.filesselector.param.watch(self.filesselector_change, 'value')
        self.datafileblock.filesselector.param.watch(self.filesselector_change_datafile, 'value')
        self.programfileblock.filesselector.param.watch(self.filesselector_change_programfile, 'value')

        self.tabs_sidebar = pn.Tabs(('Data files',self.datafileblock.view),
                                        ('Program files',self.programfileblock.view),
                                        ('Function files',self.functionfileblock.view),
                                        )

        self.tabs = pn.Tabs(('Analytics services',self.program.view),('Data Preview',self.datapreview.view),
        ('Program files preview',self.programpreview.view),('Function editor',self.functioneditorblock.view ))

        self.accordion = pn.Accordion(('Layer0', self.tabs),toggle =False, active=[0]  )
        self.template = pn.template.MaterialTemplate(title='SLEGO - Additive Program/User config software')

        self.template.sidebar.append(self.tabs_sidebar)
        self.template.sidebar.append(pn.layout.Divider())
        self.tabs.dynamic =True

        self.template.main.append(self.tabs)
        self.template.main.append(pn.layout.Divider() )
        
        self.server= self.template.show(open=open_in_browser)
        self.output = widgets.Output(layout={'border': '1px solid black'})

    def btn_write_clicked_functioneditor(self,event):
        self.functionfileblock.filesselector.options =self.get_files(folder_path='./functions/')

    def filesselector_change_functionfile(self,event):
        self.functioneditorblock.filepath.value = self.functionfileblock.filepath
        self.functioneditorblock.btn_open_clicked(self.functioneditorblock.btn_open)
        self.functionfileblock.filesselector.options =self.get_files(folder_path='./functions/')

    def filesselector_change_programfile(self,event):
        self.programpreview.feed_data(self.programfileblock.selected_file_path)

    def filesselector_change_datafile(self,event):
        self.datapreview.feed_data(self.datafileblock.selected_file_path)
        
    def btn_save_clicked(self,event):
        self.programfileblock.filesselector.options =self.get_files(folder_path='./user_function/')

    def btn_compute_clicked(self,event):
        self.datafileblock.filesselector.options =self.get_files(folder_path='./data/')

    def open_in_browser(self):
        webbrowser.open(f'http://localhost:{self.server.port}')

    def get_files(self,folder_path='./data/'):
        file_list= [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return file_list
        
    @property
    def view(self):
        iframe = pn.pane.HTML(f'<iframe src="http://localhost:{self.server.port}" frameborder="0" scrolling="yes" height="800" width="100%""></iframe>')
        return iframe

#app