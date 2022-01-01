import os
import urllib.request
from flask import Flask, flash, request, redirect, render_template, send_file, session
from werkzeug.utils import secure_filename
from MASPC_Engine import MASPC_Engine

app = Flask(__name__)

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/process', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			flash('File successfully uploaded')
			session['filename'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			session['autoParams'] = (False,True)['on' == request.form.get('autoGenParams')]
			session['autoDiscretize'] = (False,True)['on' == request.form.get('autoDiscretize')]
			session['discretizeStrategy'] = request.form.get('dStrat')
			session['oneDiagnosisPerLine'] = (False,True)['on' == request.form.get('oneDiagnosisPerLine')]
			session['containsTemporal'] = (False,True)['on' == request.form.get('containsTemporalData')]
			session['minSup'] = request.form.get('minSup')
			session['minOv'] = request.form.get('minOv')
			session['minAc'] = request.form.get('minAc') # These are stored as str
			session['k'] = request.form.get('k')
			session['q'] = request.form.get('q')
			return redirect('/analyze')
		else:
			flash('Allowed file types are txt or csv')
			return redirect(request.url)

@app.route('/analyze')
def run_maspc():
	print("Filename is: "+str(session.get('filename'))) 
	print("autoGen is: "+str(session.get('autoParams'))) #boolean values True/False
	print("autoDiscretize is: "+str(session.get('autoDiscretize')))

	maspc_engine = MASPC_Engine(session.get('filename'),
			session['minAc'],session['minOv'],session['minSup'],
			session['k'],session['containsTemporal'],session['autoDiscretize'],
			session['discretizeStrategy'],session['q'])

	if (session.get('containsTemporal')):
		maspc_engine.processTemporal()
	
	if (session.get('oneDiagnosisPerLine')):
		maspc_engine.processOneDiagPerLine()
	
	if (session.get('autoParams')):
		maspc_engine.autogenerateParameters()

	successful_run = maspc_engine.runAnalyzer()
	if (not successful_run):
		return redirect('/nomfas')

	return redirect('/download')
	# return send_file(outputFileName) 

@app.route('/download')
def downloadFile():
	resultPath = "/tmp/clusteringResults.csv"
	return send_file(resultPath, as_attachment=True)

@app.route('/nomfas')
def errorPageMFA():
	return render_template('nomfas.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')