from website import create_app,db2

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)