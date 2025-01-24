# myenv\Scripts\activate
# python -m venv myenv
# pip install flask streamlit pandas plotly openpyxl pyinstaller
# .\Main.exe --debug
# pyinstaller --onefile --add-data "app/view/index.html;app/view" --add-data "app/view/App.html;app/view" --add-data "app/view/css/reset.css;app/view/css" --add-data "app/view/css/style.css;app/view/css" --add-data "app/view/css/log_style.css;app/view/css" --add-data "app/view/js/script.js;app/view/js" --add-data "app/Arquivos_Armazenados;app/Arquivos_Armazenados" --add-data "app/model/streamlit_app.py;app/model" --add-data "app/model/Side_Consult.py;app/model" --add-data "app/model/Users.py;app/model" --add-data "myenv;myenv" --hidden-import "pandas._libs.tslibs.timedeltas" --hidden-import "pandas._libs.tslibs.timestamps" --hidden-import "pandas._libs.tslibs.np_datetime" --hidden-import "pandas._libs.tslibs.nattype" --hidden-import "pandas._libs.tslibs.timezones" --hidden-import "streamlit" --hidden-import "flask" --workpath build --distpath dist --specpath . app/controller/Main.py
import os
import atexit
import signal
import subprocess
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import logging
logging.basicConfig(level=logging.DEBUG)
print("Iniciando aplicativo...")
app = Flask(__name__)
app.secret_key = 'your_secret_key'
print("Verificando diretório temporário...")
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    logging.debug(f"base_path: {base_path}")
    template_folder = os.path.join(base_path, 'app/view')
    static_folder = os.path.join(base_path, 'app/view')
    streamlit_app_path = os.path.join(base_path, 'app/model/streamlit_app.py')
    streamlit_side_path = os.path.join(base_path, 'app/model/Side_Consult.py')
    venv_path = os.path.join(base_path, 'myenv')
    python_exe_path = os.path.join(venv_path, 'Scripts', 'python.exe')
    streamlit_exe_path = os.path.join(venv_path, 'Scripts', 'streamlit.exe')
else:
    base_path = os.path.dirname(__file__)
    logging.debug(f"base_path: {base_path}")
    template_folder = os.path.join(base_path, '../view')
    static_folder = os.path.join(base_path, '../view')
    streamlit_app_path = os.path.abspath(os.path.join(base_path, "../model/streamlit_app.py"))
    streamlit_side_path = os.path.abspath(os.path.join(base_path, "../model/Side_Consult.py"))
    venv_path = os.path.abspath(os.path.join(base_path, "../myenv"))
    python_exe_path = os.path.join(venv_path, 'Scripts', 'python.exe')
    streamlit_exe_path = os.path.join(venv_path, 'Scripts', 'streamlit.exe')
logging.debug(f"template_folder: {template_folder}")
logging.debug(f"streamlit_app_path: {streamlit_app_path}")
logging.debug(f"streamlit_side_path: {streamlit_side_path}")
logging.debug(f"venv_path: {venv_path}")
logging.debug(f"python_exe_path: {python_exe_path}")
logging.debug(f"streamlit_exe_path: {streamlit_exe_path}")
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.secret_key = 'your_secret_key'
print("Configurando variáveis de ambiente...")
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '0'
veiculo_data = None
abastecimento_data = None
veiculo_filename = None
abastecimento_filename = None
streamlit_processes = []
@app.route('/', methods=['GET', 'POST'])
def login():
    print("Entrou na rota /")
    logging.debug(f"Tentando renderizar o template index.html a partir de: {template_folder}")
    if request.method == 'POST':
        print("Requisição POST recebida")
        usuario = request.form['usuario']
        senha = request.form['senha']
        users = {"Jose Mario": "1234", "Saulo": "5678", "Gesse": "9123"}
        if usuario in users and users[usuario] == senha:
            session['usuario'] = usuario
            logging.debug(f"Usuário {usuario} autenticado")
            return redirect(url_for('app_page'))
        else:
            print("Credenciais inválidas")
            return 'Credenciais inválidas!'
    return render_template('index.html')
@app.route('/app', methods=['GET', 'POST'])
def app_page():
    print("Entrou na rota /app")
    if 'usuario' not in session:
        print("Usuário não autenticado, redirecionando para /")
        return redirect(url_for('login'))
    return render_template('App.html')
@app.route('/process_files', methods=['POST'])
def process_files():
    print("Entrou na rota /process_files")
    if 'veiculoFile' not in request.files or 'abastecimentoFile' not in request.files:
        print("Arquivos veiculoFile ou abastecimentoFile não fornecidos")
        return jsonify({'error': 'Ambos os arquivos são necessários'})
    veiculo_file = request.files['veiculoFile']
    abastecimento_file = request.files['abastecimentoFile']
    global veiculo_data, abastecimento_data, veiculo_filename, abastecimento_filename
    veiculo_data = veiculo_file.read()
    abastecimento_data = abastecimento_file.read()
    veiculo_filename = veiculo_file.filename
    abastecimento_filename = abastecimento_file.filename
    stored_folder = "app/Arquivos_Armazenados"
    os.makedirs(stored_folder, exist_ok=True)
    with open(os.path.join(stored_folder, "veiculo_data.bin"), "wb") as f:
        f.write(veiculo_data)
    with open(os.path.join(stored_folder, "abastecimento_data.bin"), "wb") as f:
        f.write(abastecimento_data)
    print("Arquivos importados com sucesso")
    return jsonify({'result': 'Arquivos importados com sucesso', 'veiculo_filename': veiculo_filename, 'abastecimento_filename': abastecimento_filename})
@app.route('/main_consult', methods=['GET'])
def main_consult():
    print("Redirecionando para /main_consult")
    return redirect("http://localhost:8501")
@app.route('/side_consult', methods=['GET'])
def side_consult():
    print("Redirecionando para /side_consult")
    return redirect("http://localhost:8502")
@app.route('/start_streamlit')
def start_streamlit():
    print("Entrou na rota /start_streamlit")
    stored_folder = "app/Arquivos_Armazenados"
    streamlit_control_path = os.path.join(stored_folder, "streamlit_control")
    with open(streamlit_control_path, "w") as f:
        f.write("control")
    process = None
    def execute_streamlit(consult_type):
        if os.path.exists(python_exe_path):
            python_path = python_exe_path
        else:
            python_path = 'python'
        if consult_type == 'main':
            streamlit_path = streamlit_app_path
            port = "8501"
        else:
            streamlit_path = streamlit_side_path
            port = "8502"
        return subprocess.Popen([python_path, "-m", "streamlit", "run", streamlit_path, "--server.port", port], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    consult_type = request.args.get('consult_type')
    if consult_type == 'main':
        print("Iniciando streamlit para consulta principal")
    else:
        print("Iniciando streamlit para consulta secundária")
    process = execute_streamlit(consult_type)
    if process:
        streamlit_processes.append(process)
        stdout, stderr = process.communicate()
        print("STDOUT:", stdout.decode())
        print("STDERR:", stderr.decode())
        return "Streamlit iniciado. Por favor, acesse a análise na nova aba do navegador."
@app.route('/clean_and_shutdown', methods=['POST'])
def clean_and_shutdown():
    print("Entrou na rota /clean_and_shutdown")
    global streamlit_processes
    stored_folder = "app/Arquivos_Armazenados"
    for filename in os.listdir(stored_folder):
        file_path = os.path.join(stored_folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Erro ao deletar {file_path}: {e}")
    for process in streamlit_processes:
        process.terminate()
    streamlit_processes = []
    print("Finalizando servidor")
    shutdown_server()
    return "Aplicação fechada e arquivos limpos."
def shutdown_server():
    os.kill(os.getpid(), signal.SIGINT)
atexit.register(shutdown_server)
if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    app.run(debug=False, port=5001)