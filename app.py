from flask import Flask, render_template, request, jsonify, make_response, Response
import requests

import plotly
import plotly.graph_objs as go
import MySQLdb
import dash
import json
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


conn = MySQLdb.connect(host="localhost", user="root", passwd="MYSQLpwd123.", db="classicmodels")
cursor = conn.cursor()

app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/table_test')
def table_test():
	cursor.execute('select employeeNumber, lastName, firstName from employees');
	rows = cursor.fetchall()
	df = pd.DataFrame(list(rows), columns=['employeeNumber', 'lastName', 'firstName'])
	fig = go.Figure(data=[go.Table(
		header=dict(values=list(df.columns),
		fill_color='paleturquoise',
		align='left'),
		cells=dict(values=[df.employeeNumber, df.lastName, df.firstName],
		fill_color='lavender',
		align='left'))
	])
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return render_template('table_test.html', graphJSON=graphJSON)

@app.route('/plotly_test')
def plotly_test():
	cursor.execute("""
		SELECT productLine, count(productLine) as 'num_pl' FROM classicmodels.products
		group by productLine;
		""")
	rows = cursor.fetchall()
	df = pd.DataFrame(list(rows), columns=['Product_Line', 'Number_PL'])
	fig = px.bar(df, x="Product_Line", y="Number_PL", color="Number_PL", barmode="group")
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return render_template('plotly_test.html', graphJSON=graphJSON)

@app.route('/plotly_test2')
def plotly_test2():
	cursor.execute("""
		SELECT
		EXTRACT(year FROM orderDate) AS year,
		count(orderDate) AS num_order
		FROM orders
		GROUP BY EXTRACT(year FROM orderDate);
		""")
	rows = cursor.fetchall()
	df = pd.DataFrame(list(rows), columns=['year', 'number_order'])
	fig = px.pie(df, values='number_order', names='year', title='Number of order each year')
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return render_template('plotly_test2.html', graphJSON=graphJSON)

@app.route('/get_employee_webpage')
def get_employee_webpage():
	cursor.execute('select * from employees');
	rows = cursor.fetchall()
	return render_template('get_employee.html', rows=rows)

@app.route('/api/v1/employees/all', methods = ['GET'])
def get_all_emp():
	cursor.execute('select * from employees');
	rows = cursor.fetchall()
	return make_response(jsonify(rows))

@app.route('/api/v1/employees', methods=['GET'])
def get_emp():
	emp_id = request.args.get('emp_id')
	query = "select * from employees"
	if emp_id:
		query += ' where employeeNumber = ' + emp_id + ';'
	else:
		return page_not_found(404)
	cursor.execute(query);
	rows = cursor.fetchall()
	return jsonify(rows)

@app.route('/create_employee_webpage')
def create_emp_webpage():
	return render_template('create_employee.html')

@app.route('/create_employee_form', methods=['POST'])
def create_emp_form():
	emp_id = request.form['employee_id']
	emp_ln = request.form['lastname']
	emp_fn = request.form['firstname']
	emp_ex = request.form['emp_extension']
	emp_em = request.form['emp_email']
	emp_oc = request.form['emp_office_code']
	emp_rt = request.form['emp_report_to']
	emp_jt = request.form['emp_job_title']
	
	cursor.execute(
      """INSERT INTO employees (employeeNumber, lastName, firstName, 
      extension, email, officeCode, reportsTo, jobTitle)
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
      (emp_id, emp_ln, emp_fn, emp_ex, emp_em, emp_oc, emp_rt, emp_jt)
      )
	conn.commit()

	return render_template('success.html')

@app.route('/api/v1/employees', methods=['POST'])
def create_emp():
	content = request.get_json()
	emp_id = content['employeeNumber']
	emp_ln = content['lastName']
	emp_fn = content['firstName']
	emp_ex = content['extension']
	emp_em = content['email']
	emp_oc = content['officeCode']
	emp_rt = content['reportsTo']
	emp_jt = content['jobTitle']

	cursor.execute(
      """INSERT INTO employees (employeeNumber, lastName, firstName, 
      extension, email, officeCode, reportsTo, jobTitle)
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
      (emp_id, emp_ln, emp_fn, emp_ex, emp_em, emp_oc, emp_rt, emp_jt)
      )
	conn.commit()

	response={
		"employeeNumber": emp_id, 
		"lastName": emp_ln,
		"firstName": emp_fn, 
		"extension": emp_ex, 
		"email": emp_em, 
		"officeCode": emp_oc, 
		"reportsTo": emp_rt, 
		"jobTitle": emp_jt
	}
	return make_response(jsonify({"employee": response}),200)

@app.route('/delete_employee_webpage')
def delete_emp_webpage():
	cursor.execute('select * from employees');
	rows = cursor.fetchall()
	return render_template('delete_employee.html', rows=rows)

@app.route('/api/v1/employees', methods=['DELETE'])
def delete_emp():
	emp_id = request.args.get('emp_id')
	cursor.execute( "DELETE FROM employees WHERE employeeNumber = %s", [emp_id] )
	conn.commit()

	return make_response("successfully deleted",204)

@app.route('/api/v1/employees', methods=['PUT'])
def update_emp():
	content = request.get_json()
	emp_id = content['employeeNumber']
	emp_ln = content['lastName']
	emp_fn = content['firstName']
	emp_ex = content['extension']
	emp_em = content['email']
	emp_oc = content['officeCode']
	emp_rt = content['reportsTo']
	emp_jt = content['jobTitle']

	cursor.execute(
      """UPDATE employees SET 
      lastName = %s, firstName = %s, 
      extension = %s, email = %s, officeCode = %s, reportsTo = %s, jobTitle = %s
      WHERE employeeNumber = %s""",
      [emp_ln, emp_fn, emp_ex, emp_em, emp_oc, emp_rt, emp_jt, emp_id]
      )
	conn.commit()

	response={
		"employeeNumber": emp_id, 
		"lastName": emp_ln,
		"firstName": emp_fn, 
		"extension": emp_ex, 
		"email": emp_em, 
		"officeCode": emp_oc, 
		"reportsTo": emp_rt, 
		"jobTitle": emp_jt
	}
	return make_response(jsonify({"employee": response}),200)

@app.errorhandler(404)
def page_not_found(e):
	return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == '__main__':
	app.run(debug=True)

