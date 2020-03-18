

'''Implementation Using Sheets directly'''


from flask import Flask, render_template, url_for, flash, redirect, session
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
list1 = wks.get_all_records()
data['history'] = list1
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

@app.route("/", methods=['GET', 'POST'])
def index():
    form = LoginForm()
    values = []
    components = []
    tS = []
    if form.validate_on_submit():
        email = form.email.data
        id = form.id.data
        x = re.search("[1-9][1-9][6789][0-4][01][0-9][0-9]0", id)
        if x == None:
            flash('You entered invalid ID!!', 'danger')
            return render_template('/index.html', form=form, title='Login')
        try:
            cell_list = wks.findall(id)
            email_list = wks.findall(email)
            if cell_list != [] and email_list != []:
                email_checker = wks.cell(cell_list[0].row, cell_list[0].col - 2).value
                id_checker = wks.cell(email_list[0].row, email_list[0].col + 2).value
                if cell_list[0].value == id_checker  and  email_list[0].value == email_checker :
                    for cell in cell_list:
                        emailCheck = wks.cell(cell.row, cell.col - 2).value
                        if email == emailCheck:
                            values.append(wks.cell(cell.row, cell.col + 5).value)
                            components.append(wks.cell(cell.row, cell.col + 3).value)
                            timeStamp = wks.cell(cell.row, cell.col - 3).value
                            tS.append(re.split(r'\s', timeStamp))
                        else:
                            flash("You entered someother's credentials", 'danger')
                            return render_template('/index.html', form=form, title='Login')
                    return render_template('status.html', val=values, comp=components, time=tS, title='History')
                else:
                    flash(f'Check your credentials once again', 'warning')
            elif cell_list == [] and email_list == []:
                flash(f"Seems you've not taken any Components till now", 'info')
                return redirect(url_for('status', val=values, comp=components, time=tS, title='History'))
            elif cell_list == [] or email_list == []:
                flash(f"You entered someother's credentials", 'warning')
                return render_template('/index.html', form=form, title='Login')
        except gspread.exceptions.CellNotFound:
            return redirect(url_for('status', val=values, comp=components, time=tS, title='History'))
        except gspread.exceptions.APIError:
            flash(f'Try After Sometime','danger')
            return render_template('/index.html', form=form, title='Login')


    return render_template('/index.html', form=form, title='Login')

@app.route("/status", methods=['GET', 'POST'])
def status():
    return render_template("status.html", val=val, comp=comp,time=time, title='History')

if __name__ == '__main__':
   app.run(debug = True)
