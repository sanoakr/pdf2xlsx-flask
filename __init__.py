import os
from werkzeug.utils import secure_filename
from flask import Flask,flash,request,redirect,send_file,render_template,after_this_request
import pandas as pd
import tabula
import random, string
import shutil

#app = Flask(__name__)
app = Flask(__name__, template_folder='templates')
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Upload API
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    dir = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    try:
        os.mkdir(dir)
        print('create upload dir')
    except:
        return redirect(request.url)
    upload_dir = f'{dir}/'

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            upload_file = os.path.join(upload_dir, filename)
            file.save(upload_file)
            print("saved file successfully")
            # tabula
            pages = request.form.get('pages')
            print(f"{pages} page(s)")
            dfs = tabula.read_pdf(upload_file, pages=pages)
            #dfs = tabula.read_pdf(upload_file, lattice=True, pages=pages)
            print(f'{len(dfs)} tables are found')
            for i, df in enumerate(dfs):
                df.to_csv(upload_file + f'_{i}.csv', index=None)
                df.to_excel(upload_file + f'_{i}.xlsx', index=None)

      #send file name as parameter to downlad
            return redirect('/downloadfile/'+ dir)

    return render_template('upload_file.html')

# Download API
@app.route("/downloadfile/<dir>", methods = ['GET'])
def download_file(dir):
    shutil.make_archive(dir, format='zip', root_dir=dir)
    return render_template('download.html',value=dir)

@app.route('/return-files/<dir>')
def return_files_tut(dir):
    zipfile = dir+'.zip'
    @after_this_request
    def remove_files(response):
        try:
            os.remove(zipfile)
            shutil.rmtree(dir)
        except:
            print("remove error")
        return response
    return send_file(zipfile)
    #return send_file(zipfile, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
