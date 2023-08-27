from guizero import App
app = App()

reponse = app.yesno("Info", "This is a guizero app")
if reponse:
    app.info("Info", "You selected true")
else:
    app.info("Info", "You selected no")

app.info("Info", "This is a guizero app")
app.error("Error", "Try and keep these out your code...")
app.warn("Warning", "These are helpful to alert users")
app.display()
