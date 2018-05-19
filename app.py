from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine, desc, inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
engine = create_engine("sqlite:///DataSets/belly_button_biodiversity.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
session = Session(engine)

Metadata = Base.classes.samples_metadata
Otu = Base.classes.otu
Samples = Base.classes.samples


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/names', methods=['GET', 'POST'])
def names():
    inspector = inspect(engine)
    columns = inspector.get_columns('samples')
    names_list = []
    for column in columns[1:]:
        names_list.append(column['name'])
    return jsonify(names_list)


@app.route('/otu')
def otu():
    results = session.query(Otu.lowest_taxonomic_unit_found).all()
    otu_list = []
    for result in results:
        otu_list.append(result[0])
    return jsonify(otu_list)


@app.route('/metadata/<sample>')
def metadata(sample):
    bb_id = sample[3:]
    results = session.query(Metadata.AGE,
                            Metadata.BBTYPE,
                            Metadata.ETHNICITY,
                            Metadata.GENDER,
                            Metadata.LOCATION,
                            Metadata.SAMPLEID).filter(Metadata.SAMPLEID == bb_id).first()
    metadict = {
        "AGE": results[0],
        "BBTYPE": results[1],
        "ETHNICITY": results[2],
        "GENDER": results[3],
        "LOCATION": results[4],
        "SAMPLEID": results[5]
    }
    return jsonify(metadict)


@app.route('/wfreq/<sample>')
def wfreq(sample):
    bb_id = sample[3:]
    result = session.query(Metadata.WFREQ, \
                           Metadata.SAMPLEID) \
        .filter(Metadata.SAMPLEID == bb_id).first()
    return jsonify(result)


@app.route('/samples/<sample>')
def samples(sample):
    print("Sample " + sample)
    bb_id_query = f"Samples.{sample}"
    results = session.query(Samples.otu_id, \
                            bb_id_query) \
        .order_by(desc(bb_id_query))
    sampdict = {"otu_ids": [result[0] for result in results],
                "sample_values": [result[1] for result in results]}
    return jsonify(sampdict)


if __name__ == '__main__':
    app.run(debug=True)