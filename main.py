from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import matplotlib.pyplot as plt
import shutil
import pandas as pd
import numpy as np
import io
import os

app = FastAPI()

templates = Jinja2Templates(directory=os.path.dirname(__file__))

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("upload.html", {"request":request})


@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    data1 = pd.read_excel('updated_09.xlsx', engine='openpyxl')
    data2 = pd.read_excel(file_path, engine='openpyxl')

    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)

    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    global df1_clean
    df1_clean = df1.dropna(subset=['SKU']).copy()
    df2_clean = df2.dropna(subset=['SKU']).copy()

    df1_clean = df1_clean.set_index("SKU")
    df2_clean = df2_clean.set_index("SKU")

    df2_clean.to_excel('df2.xlsx')

    def clean_numeric(df, cols):
        for col in cols:
            df[col] = df[col].astype(str).str.replace(',','').astype('float')
        return df

    cols_to_clean = ['Current Stock', 'Value', 'Unit Price(£)', 'Sales Price(£)']
    df1_clean = clean_numeric(df1_clean, cols_to_clean)
    df2_clean = clean_numeric(df2_clean, cols_to_clean)

    merged = df1_clean.merge(df2_clean, on='SKU', suffixes=('_old', '_new'))
    merged['Stock_change'] = merged['Current Stock_new'] - merged['Current Stock_old']
    merged['Value_change'] = merged['Value_new'] - merged['Value_old']
    merged['Sales_price_change'] = merged['Sales Price(£)_new'] - merged['Sales Price(£)_old']
    merged['Unit Price_change'] = merged['Unit Price(£)_new'] - merged['Unit Price(£)_old']

    changes = merged[(merged['Stock_change'] != 0) | (merged['Value_change'] != 0) | (merged['Sales_price_change'] != 0) | (merged['Unit Price_change']) != 0]


    #update df1
    cols_to_update = ['Current Stock', 'Value', 'Unit Price(£)', 'Sales Price(£)']

    postition = df1_clean.columns.get_loc('Value')
    df1_clean.insert(loc=postition, column='Prev Stock', value=df1_clean['Current Stock'].copy())

    loc_for_prev_sales = df1_clean.columns.get_loc('Current Stock')
    df1_clean.insert(loc=loc_for_prev_sales, column='Prev Sales Price', value=df1_clean['Sales Price(£)'].copy())

    loc_for_prev_unit_price = df1_clean.columns.get_loc('Tax')
    df1_clean.insert(loc=loc_for_prev_unit_price, column='Prev Unit Price', value=df1_clean['Unit Price(£)'])

    df1_clean['Prev Stock'] = df1_clean['Current Stock']
    df1_clean['Prev Sales Price'] = df1_clean['Sales Price(£)']
    df1_clean['Prev Unit Price'] = df1_clean['Unit Price(£)']

    df2_aligned = df2_clean.reindex(df1_clean.index)

    for col in cols_to_update:
        mask = df2_aligned[col].notna()
        df1_clean.loc[mask, col] = df2_aligned.loc[mask, col]


    location_for_stock_mark = df1_clean.columns.get_loc('Value')
    location_for_sales_mark = df1_clean.columns.get_loc('Current Stock')
    location_for_unit_mark = df1_clean.columns.get_loc('Tax')

    df1_clean['Stock Changed'] = np.where(df1_clean['Current Stock'] != df1_clean['Prev Stock'], '✔', '')
    df1_clean['Sales Changed'] = np.where(df1_clean['Prev Sales Price'] != df1_clean['Sales Price(£)'], '✔', '')
    df1_clean['Unit price Changed'] = np.where(df1_clean['Prev Unit Price'] != df1_clean['Unit Price(£)'], '✔', '')


    stock_col = df1_clean.pop('Stock Changed')
    sales_col = df1_clean.pop('Sales Changed')
    unit_col = df1_clean.pop('Unit price Changed')

    df1_clean.insert(loc=location_for_stock_mark, column='Stock Changed', value=stock_col)
    df1_clean.insert(loc=location_for_sales_mark, column='Sales Changed', value=sales_col)
    df1_clean.insert(loc=location_for_unit_mark, column='Unit Price Changed', value=unit_col)

    
    cols_to_show = ['Item Code', 'Current Stock', 'Prev Stock', 'Stock Changed', 'Sales Price(£)',
            'Prev Sales Price', 'Sales Changed']
    global df
    df = df1_clean[cols_to_show]
    dff = df.head(15)
    data = dff.to_dict(orient='records')
    columns = dff.columns.tolist()

    df.to_excel('compare.xlsx')

    return templates.TemplateResponse('index.html', {
        "request": request,
        "columns": columns,
        "rows": data,
        "filename": file.filename
    })

@app.get("/download")
async def download():
    file_path = 'compare.xlsx'
    return FileResponse(
        path = file_path,
        filename = 'compare.xlsx',
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.get("/Stock-plot")
async def sales_plot():
    brand_stock = df1_clean.groupby("Brand")["Current Stock"].sum().sort_values(ascending=False)

    plt.figure(figsize=(9,6))
    bars = plt.bar(brand_stock.index, brand_stock.values, color="skyblue", edgecolor="black")
    plt.xlabel("Brand", fontsize=14)
    plt.ylabel("Total Stock", fontsize=14)
    plt.xticks(rotation=30, ha="right")
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2,  
            height,                           
            f"{int(height)}",                 
            ha="center", va="bottom", fontsize=10, fontweight="bold", color="black"
        )

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
