# Excel Comparator — FastAPI Project

**Excel Comparator** is a FastAPI-based web application that allows users to upload Excel files, compare data between an existing dataset and the uploaded file, and highlight differences in stock, sales price, and unit price. The application also provides downloadable comparison results and visualizations of stock data.

---

## Project Structure
Excel-Comparator/
│
├── main.py # FastAPI application
├── updated_09.xlsx # Base Excel file for comparison
├── uploads/ # Folder to store uploaded Excel files
├── compare.xlsx # Output file generated after comparison
├── templates/
│ ├── index.html # Results display page
│ └── upload.html # Upload form page
├── venv/ # Virtual environment
└── README.md


---

## Features

- Upload Excel files to compare with a base dataset (`updated_09.xlsx`).  
- Detect changes in:
  - **Current Stock**
  - **Sales Price**
  - **Unit Price**
- Mark updated fields with a **✔** symbol.  
- Download comparison results as a new Excel file (`compare.xlsx`).  
- Visualize total stock per brand with an interactive bar chart.  
- Fully browser-based interface using HTML templates.

---

## Technologies Used

- **Python 3.12**  
- **FastAPI** — for backend API and web server  
- **Jinja2** — for HTML templating  
- **Pandas** — for Excel processing and data manipulation  
- **NumPy** — for numerical operations  
- **Matplotlib** — for data visualization  
- **Uvicorn** — ASGI server for development

---

## How to Run

1. Clone the repository:
```bash
git clone https://github.com/kun-ahmadraza/Excel-Comparator.git
cd "Excel-Comparator"

python -m venv venv
venv\Scripts\activate

Install dependencies:
pip install fastapi uvicorn pandas numpy matplotlib openpyxl jinja2
Start the FastAPI server:
uvicorn main:app --reload
Open your browser and go to:
http://127.0.0.1:8000/



