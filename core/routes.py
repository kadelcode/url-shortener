from datetime import datetime
from core.models import ShortUrls, CustomShortUrls, User
from core.forms import LoginForm, RegistrationForm
from core import app, db, login_manager
from random import choice
import string, hashlib
import codecs
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user

# Choice algorithm
def generate_short_id(num_of_chars: int):
    """Function to generate short_id of specified number of characters"""
    return ''.join(choice(string.ascii_letters+string.digits) for _ in range(num_of_chars))

# Hashlib algorithm
def generate_short_url(custom_url):
    """ Generates a short custom URL
    from a long string
    
    Keyword arguments:
    argument -- The long link to generate the short URL from.
    Return: A short custom url
    """

    # Generate a hash of the custom URL
    hash = hashlib.sha256(custom_url.encode('utf-8')).hexdigest()

    # Take the first 5 characters of the hash
    short_url = hash[:5]

    return short_url
    
# Index(homepage) route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
            
        if not url:
            flash('The URL is required!', 'error')
            return redirect(url_for('index'))

        
        short_id = generate_short_id(8)
        
        # If the original link exits, then return the short id from the database
        if ShortUrls.query.filter_by(original_url=url).first() is not None:
            flash('Link found in the database', 'info')
            short_id = ShortUrls.query.filter_by(original_url=url).first().short_id
            short_url = request.host_url + short_id
            return render_template('index.html', short_url=short_url)
        

        # If the original link doesn't exist, then add to the database
        if ShortUrls.query.filter_by(original_url=url).first() is None:
            new_link = ShortUrls(original_url=url, short_id=short_id, created_at=datetime.now())
            db.session.add(new_link)
            db.session.commit()
            short_url = request.host_url + short_id


            flash('Short link successfully created!', 'success')
            return render_template('index.html', short_url=short_url)

    return render_template('index.html')

# Redirect the short url
@app.route('/<short_id>')
def redirect_url(short_id):
    link = ShortUrls.query.filter_by(short_id=short_id).first()
    if link:
        return redirect(link.original_url)
    else:
        flash('Invalid URL', 'error')
        return redirect(url_for('index'))

# Route for registering a user to the platform
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':       
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data
            password1 = form.password1.data

            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(username=username).first():
                flash('Username already taken', 'error')
                return redirect(url_for('register'))
            
            if not password and password1:
                flash('password is required!', 'error')
                return redirect(url_for('register'))

            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()

            flash('Registration successful!', 'success')

            return redirect(url_for('user_dashboard'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('login successful', 'success')
            return redirect(url_for('user_dashboard'))
        flash('Invalid username or password!', 'error')
    return render_template('login.html', form=form)

# Logout function
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Dashboard route
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def user_dashboard():
    # A post request method to generate a custom URL for a logged in user
    if request.method == 'POST':
        url = request.form.get('url') # Required input
        domain = request.form.get('domain') # Optional but also required if the user is on a payed plan
        back_half = request.form.get('back_half')  # Optional

        short_id = generate_short_id(5) # For every post request, a short id is always generated

        # If the user doesn't enter a long URL, then this happens
        if not url:
            flash('The URL is required!', 'error')
            return redirect(url_for('user_dashboard'))

        if url and not(domain) and not(back_half):
            # Get the current user id
            user_id = current_user.id

            # If the original url exits in db, then return the short url from the database
            if CustomShortUrls.query.filter_by(user_id=user_id, original_url=url).first() is not None:
                flash('Custom url already created', 'info')
                short_url = CustomShortUrls.query.filter_by(user_id=user_id,original_url=url).first().short_url
                # short_url = request.host_url + short_id
                return redirect(url_for('user_dashboard', short_url=short_url))
            else: # if original url does exist
                short_url = request.host_url + short_id
                custom_link = CustomShortUrls(user_id=user_id, original_url=url, short_id=short_id, short_url=short_url)
                db.session.add(custom_link)
                db.session.commit()
                flash('Custom URL successfully generated', 'success')
                return redirect(url_for('user_dashboard', short_url = short_url))

        if url and domain and not(back_half):
            # Get the current user id
            user_id = current_user.id

            # Check if url and domain already exist in database
            if CustomShortUrls.query.filter_by(user_id=user_id, original_url=url).first() is not None and \
                (CustomShortUrls.query.filter_by(user_id=user_id, domain=domain).first() is not None):
                short_url = CustomShortUrls.query.filter_by(user_id=user_id, original_url=url, domain=domain).first().short_url
                flash('Custom url already created', 'info')
                return redirect(url_for('user_dashboard', short_url = short_url))

            else:
                short_url = domain + "/" + short_id
                custom_link = CustomShortUrls(user_id=user_id, original_url=url, domain=domain, short_id=short_id, short_url = short_url)
                db.session.add(custom_link)
                db.session.commit()
                flash('Custom URL successfully generated', 'success')
                return redirect(url_for('user_dashboard', short_url = short_url))

        if url and domain and back_half:
            # Get the current user id
            user_id = current_user.id

            # Check if url, domain, and back_half already in database
            if CustomShortUrls.query.filter_by(user_id=user_id, original_url=url).first() is not None and \
                (CustomShortUrls.query.filter_by(user_id=user_id, domain=domain).first() is not None) and \
                    (CustomShortUrls.query.filter_by(user_id=user_id, back_half=back_half).first() is not None):
                flash('Custom url already created.', 'info')
                return redirect(url_for('user_dashboard', short_url = short_url))
            
            else:
                short_url = domain + "/" + short_id + "/" + back_half
                custom_link = CustomShortUrls(user_id=user_id, original_url=url, domain=domain, back_half=back_half, short_id=short_id, short_url = short_url)
                db.session.add(custom_link)
                db.session.commit()
                flash('Custom URL successfully generated', 'success')
                return redirect(url_for('user_dashboard', short_url = short_url))

        if url and back_half and not(domain):
            # Get the current user id
            user_id = current_user.id
            
            # Check if url and back_half exist in database
            if CustomShortUrls.query.filter_by(user_id=user_id, original_url=url).first() is not None and \
                (CustomShortUrls.query.filter_by(user_id=user_id, back_half=back_half).first() is not None):
                short_url = CustomShortUrls.query.filter_by(user_id=user_id, original_url=url, back_half=back_half).first().short_url
                flash('Custom url already created.')
                return redirect(url_for('user_dashboard', short_url = short_url))
            
            else:
                short_url = request.host_url + short_id + "/" + back_half
                custom_link = CustomShortUrls(user_id=user_id, original_url=url, back_half=back_half, short_id=short_id, short_url = short_url)
                db.session.add(custom_link)
                db.session.commit()
                flash('Custom URL successfully generated', 'success')
                return redirect(url_for('user_dashboard', short_url = short_url))
        '''
        # If the original link doesn't exist, then add to the database
        if CustomShortUrls.query.filter_by(original_url=url).first() is None:
            new_link = CustomShortUrls(original_url=url, domain=domain, back_half=back_half, short_id=short_id, created_at=datetime.now())
            db.session.add(new_link)
            db.session.commit()
            short_url = request.host_url + short_id
            flash('Short custom link successfully generated', 'success')
            return render_template("overview.html", short_url=short_url)
        '''
    
    # for GET request
    return render_template('overview.html')

# Redirect the custom short url with only short_id
@app.route('/<short_id>')
def redirect_custom_url_s(short_id):
    link = CustomShortUrls.query.filter_by(short_id=short_id).first()
    if link:
        return redirect(link.original_url)
    else:
        flash('Invalid URL', 'error')
        return redirect(url_for('index'))

# Redirect the custom short url with short_id && domain
@app.route('/<domain>/<short_id>/')
def redirect_custom_url_ds(short_id, back_half):
    link = CustomShortUrls.query.filter_by(domain=domain, short_id=short_id).first()
    if link:
        return redirect(link.original_url)
    else:
        flash('Invalid URL', 'error')
        return redirect(url_for('index'))

# Redirect the custom short url with short_id && back_half
@app.route('/<short_id>/<back_half>')
def redirect_custom_url_sb(short_id, back_half):
    link = CustomShortUrls.query.filter_by(short_id=short_id, back_half=back_half).first()
    if link:
        return redirect(link.original_url)
    else:
        flash('Invalid URL', 'error')
        return redirect(url_for('index'))

# Redirect the custom short url with short_id, domain && back_half
@app.route('/<domain>/<short_id>/<back_half>')
def redirect_custom_url_dsb(domain, short_id, back_half):
    link = CustomShortUrls.query.filter_by(domain=domain, short_id=short_id, back_half=back_half).first()
    if link:
        return redirect(link.original_url)
    else:
        flash('Invalid URL', 'error')
        return redirect(url_for('index'))

# Route for the user generated custom URLs
@app.route('/user-custom-url')
@login_required
def user_custom_url():
    return render_template('user_custom_url.html')

# Route for the help section
@app.route('/help')
@login_required
def help():
    return render_template('help.html')
