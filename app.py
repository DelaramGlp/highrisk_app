from website import create_app

app = create_app()
app.secret_key = "abcde"

if __name__ == '__main__':
    app.run(debug=True, port=8000)