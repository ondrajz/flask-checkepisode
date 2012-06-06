from checkepisode import app
from flask import current_app, redirect, url_for, \
    render_template, flash
from flask.ext.security import LoginForm
from flask.ext.wtf import Form, TextField, PasswordField, \
     Required, EqualTo, Email, RecaptchaField
from flask.ext.security.confirmable import send_confirmation_instructions


class RegisterForm(Form):
    name = TextField('NickName', [Required()])
    email = TextField("Email Address",
        validators=[Required(message='Email is required.'), Email()])
    password = PasswordField("Password",
        validators=[Required(message="Password not provided.")])
    password_confirm = PasswordField("Repeat password",
        validators=[EqualTo('password', message="Passwords did not match.")])
    recaptcha = RecaptchaField()


@app.route("/login")
def login():
    return render_template('login.html', form=LoginForm())


@app.route("/register", methods=('GET', 'POST'))
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = current_app.security.datastore.create_user( \
            name=form.name.data, email=form.email.data, \
            password=form.password.data, roles=['user'])
        app.logger.debug('User %s registered' % user)

        # Send confirmation instructions if necessary
        if current_app.security.confirm_email:
            send_confirmation_instructions(user)

        # Login the user if allowed
        flash('Your account has been created, please check your email \
            to verify.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)
