# Main.exe
DataAnalysis-WebConsult-TruckCompany

"Arquivos_Armazenados" Will Keep the Excel Files Stored, so Then They can Be Used t/
Consult, when the streamlit application is runnning..

Pretty Much Like a DataBase.
When you click "Limpar e Fechar", the application will clean the stored files and shut down the
server, closing the ports which are running the files ('5001', '8501' and '8502').

create your Virtual Environment to install all dependencies:

python -m venv myenv

Activate your Virtual Environment:

myenv\Scripts\activate

Install all Dependencies:

pip install flask streamlit pandas plotly openpyxl pyinstaller

Run the "Pyinstaller" Command on the terminal, outside app's Directory to Create The Executable ("Main.exe"):

pyinstaller --onefile --add-data "app/view/index.html;app/view" --add-data "app/view/App.html;app/view" --add-data "app/view/css/reset.css;app/view/css" --add-data "app/view/css/style.css;app/view/css" --add-data "app/view/css/log_style.css;app/view/css" --add-data "app/view/js/script.js;app/view/js" --add-data "app/Arquivos_Armazenados;app/Arquivos_Armazenados" --add-data "app/model/streamlit_app.py;app/model" --add-data "app/model/Side_Consult.py;app/model" --add-data "app/model/Users.py;app/model" --add-data "myenv;myenv" --hidden-import "pandas._libs.tslibs.timedeltas" --hidden-import "pandas._libs.tslibs.timestamps" --hidden-import "pandas._libs.tslibs.np_datetime" --hidden-import "pandas._libs.tslibs.nattype" --hidden-import "pandas._libs.tslibs.timezones" --hidden-import "streamlit" --hidden-import "flask" --workpath build --distpath dist --specpath . app/controller/Main.py

