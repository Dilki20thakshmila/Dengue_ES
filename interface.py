from flask import Flask, render_template, request
from knowledge_base import DengueExpertSystem, PatientFact
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diagnose', methods=['POST'])
def diagnose():
    f = request.form

    patient_data = {
        'name':                  f.get('name', 'Patient'),
        'age':                   int(f.get('age', 0)),
        'district':              f.get('district', 'other').lower(),
        'month':                 datetime.datetime.now().month,
        'fever':                 float(f.get('fever', 37.0)),
        'days_of_fever':         int(f.get('days_of_fever', 0)),
        'headache':              'headache'             in f,
        'eye_pain':              'eye_pain'             in f,
        'muscle_pain':           'muscle_pain'          in f,
        'joint_pain':            'joint_pain'           in f,
        'rash':                  'rash'                 in f,
        'nausea':                'nausea'               in f,
        'abdominal_pain':        'abdominal_pain'       in f,
        'persistent_vomiting':   'persistent_vomiting'  in f,
        'mucosal_bleeding':      'mucosal_bleeding'     in f,
        'rapid_breathing':       'rapid_breathing'      in f,
        'fluid_accumulation':    'fluid_accumulation'   in f,
        'platelet':              float(f.get('platelet', 150000)),
        'severe_bleeding':       'severe_bleeding'       in f,
        'organ_failure':         'organ_failure'         in f,
        'altered_consciousness': 'altered_consciousness' in f,
        'jaundice':              'jaundice'              in f,
        'rat_exposure':          'rat_exposure'          in f,
    }

    engine = DengueExpertSystem()
    result = engine.run(PatientFact(**patient_data))

    severity_meta = {
        0: {'label': 'LOW RISK',      'color': 'green',  'icon': '✓',  'badge': 'Unlikely Dengue'},
        1: {'label': 'MODERATE',      'color': 'yellow', 'icon': '⚠',  'badge': 'Probable Dengue'},
        2: {'label': 'HIGH RISK',     'color': 'orange', 'icon': '⚠⚠', 'badge': 'Warning Signs'},
        3: {'label': 'CRITICAL',      'color': 'red',    'icon': '🚨', 'badge': 'Severe / DSS'},
    }

    meta = severity_meta[result.severity]
    cf_percent = int(result.final_cf * 100)

    return render_template('result.html',
        patient=patient_data,
        result=result,
        meta=meta,
        cf_percent=cf_percent
    )

if __name__ == '__main__':
    app.run(debug=True)
