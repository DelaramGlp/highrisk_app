from website import create_app

app = create_app()
app.secret_key = "LDNh56g77**hjh(u)"

if __name__ == '__main__':
    app.run(debug=True, port=8000)