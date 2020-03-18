

'''Implementation using JSON file'''

from flask import Flask, render_template, url_for, flash, redirect, session, request
from forms import LoginForm
import json
import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.config['SECRET_KEY'] = '38da1a48011502ec337fb2ca236a712f'
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('Electrical Lab-31017c64dbcc.json',scope)

gc = gspread.authorize(credentials)
wks = gc.open('EELAB').sheet1
val = []
comp = []
time = []
date = []
data = {}
num = 0
@app.route("/", methods=['GET', 'POST'])
def index():
    form = LoginForm()
    values = []
    components = []
    tS = []
    cell_list = []
    email_list = []
    if request.method == 'POST' and form.validate_on_submit():
        list1 = wks.get_all_records()
        data['history'] = list1
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        email = form.email.data.lower()
        id = form.id.data
        x = re.search("[1-9][1-9][6789][0-4][01][0-9][0-9]0", id)
        if x == None:
            flash('You entered invalid ID!!', 'danger')
            return render_template('/index.html', form=form, title='Login')
        try:
            with open('data.json') as f:
                data2 = json.load(f)
            for hist in data2['history']:
                if str(hist['ID Number']) == str(id) and hist['Email Address'] == email:
                    cell_list.append(hist['ID Number'])
                    email_list.append(hist['Email Address'])
                    tS.append(re.split(r'\s', hist['Timestamp']))
                    components.append(hist['Component issuing'])
                    values.append(hist['Status'])
            if cell_list != [] and email_list != []:
                return render_template('status.html', val=values, comp=components, time=tS, title='History')
            elif cell_list == [] or email_list == []:
                flash(f"Check your credentials or you have not taken any components till now", 'warning')
                return render_template('/index.html', form=form, title='Login')
            '''elif cell_list == [] and email_list == []:
                flash(f"Seems you've not taken any Components till now", 'info')
                return redirect(url_for('status', val=values, comp=components, time=tS, title='History'))'''


        except gspread.exceptions.CellNotFound:
            return redirect(url_for('status', val=values, comp=components, time=tS, title='History'))
        except gspread.exceptions.APIError:
            flash(f'Try After Sometime', 'danger')
            return render_template('/index.html', form=form, title='Login')

    return render_template('/index.html', form=form, title='Login')

@app.route("/status", methods=['GET', 'POST'])
def status():
    return render_template("status.html", val=val, comp=comp,time=time, title='History')

if __name__ == '__main__':
   app.run(debug = True, use_reloader=True, threaded=True)
